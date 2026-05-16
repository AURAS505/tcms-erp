from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from academic.models import AcademicPeriod, AcademicYear
from common.audit import AuditAction, AuditLogService, AuditModule, serialize_model_instance
from common.money import ZERO_MONEY, quantize_money

from .models import AccountingDocument, JournalEntry, JournalEntryLine


def _validation_error(message: str) -> ValidationError:
    return ValidationError(message)


class AccountingMutationService:
    @classmethod
    def _next_entry_number(cls, *, organization_id) -> str:
        last_entry = (
            JournalEntry.objects.select_for_update()
            .filter(organization_id=organization_id)
            .order_by("-created_at", "-id")
            .first()
        )
        if last_entry is None:
            sequence = 1
        else:
            sequence = JournalEntry.objects.filter(organization_id=organization_id).count() + 1
        return f"JV-{sequence:06d}"

    @classmethod
    def validate_manual_journal_lines(cls, *, organization, lines: list[dict]) -> tuple[Decimal, Decimal]:
        if len(lines) < 2:
            raise _validation_error("Manual journal entry must have at least two lines.")

        debit_total = ZERO_MONEY
        credit_total = ZERO_MONEY
        seen_accounts = set()
        for line in lines:
            account = line["account"]
            if account.organization_id != organization.id:
                raise _validation_error("Journal line account must belong to the journal organization.")
            if not account.is_active:
                raise _validation_error("Journal line account must be active.")
            debit = quantize_money(line.get("debit_amount", ZERO_MONEY))
            credit = quantize_money(line.get("credit_amount", ZERO_MONEY))
            if debit > ZERO_MONEY and credit > ZERO_MONEY:
                raise _validation_error("A journal line cannot have both debit and credit.")
            if debit == ZERO_MONEY and credit == ZERO_MONEY:
                raise _validation_error("A journal line must have either debit or credit.")
            debit_total += debit
            credit_total += credit
            seen_accounts.add(account.id)

        if len(seen_accounts) < 2:
            raise _validation_error("Manual journal entry must use at least two accounts.")
        if debit_total != credit_total:
            raise _validation_error("Journal entry debits and credits must be equal.")
        return debit_total, credit_total

    @classmethod
    @transaction.atomic
    def create_manual_journal_entry(
        cls,
        *,
        organization,
        branch,
        academic_year,
        entry_date_ad,
        description,
        created_by=None,
        academic_period=None,
        entry_date_bs="",
        narration="",
        lines: list[dict],
    ) -> JournalEntry:
        if branch and branch.organization_id != organization.id:
            raise _validation_error("Branch must belong to the journal organization.")
        if academic_year.organization_id != organization.id:
            raise _validation_error("Academic year must belong to the journal organization.")
        if academic_period:
            if academic_period.organization_id != organization.id:
                raise _validation_error("Academic period must belong to the journal organization.")
            if academic_period.academic_year_id != academic_year.id:
                raise _validation_error("Academic period must belong to the selected academic year.")
        cls.validate_manual_journal_lines(organization=organization, lines=lines)

        journal_entry = JournalEntry.objects.create(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            academic_period=academic_period,
            entry_number=cls._next_entry_number(organization_id=organization.id),
            entry_date_ad=entry_date_ad,
            entry_date_bs=entry_date_bs,
            description=description,
            narration=narration,
            source_type=JournalEntry.SourceType.MANUAL,
            created_by=created_by,
            status=JournalEntry.Status.DRAFT,
        )
        journal_entry.full_clean()
        for line in lines:
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                organization=organization,
                branch=branch,
                account=line["account"],
                description=line.get("description", ""),
                debit_amount=quantize_money(line.get("debit_amount", ZERO_MONEY)),
                credit_amount=quantize_money(line.get("credit_amount", ZERO_MONEY)),
            )
        AuditLogService.record_model_change(
            action=AuditAction.CREATE,
            module=AuditModule.ACCOUNTING,
            instance=journal_entry,
            user=created_by,
            after_data=serialize_model_instance(journal_entry, fields=["entry_number", "status", "description"]),
            metadata={"event": "manual_journal_created"},
        )
        return journal_entry

    @classmethod
    @transaction.atomic
    def approve_journal_entry(cls, *, journal_entry_id, approved_by) -> JournalEntry:
        journal_entry = JournalEntry.objects.select_for_update().get(id=journal_entry_id)
        if journal_entry.created_by_id and journal_entry.created_by_id == getattr(approved_by, "id", None):
            raise _validation_error("Maker-checker violation: journal creator cannot approve the same journal.")
        if journal_entry.status not in {JournalEntry.Status.DRAFT, JournalEntry.Status.PENDING_APPROVAL}:
            raise _validation_error("Only draft/pending journal entries can be approved.")
        AccountingPostingService.validate_line_count(journal_entry)
        AccountingPostingService.validate_balanced(journal_entry)
        journal_entry.status = JournalEntry.Status.APPROVED
        journal_entry.approved_by = approved_by
        journal_entry._allow_immutable_update = True
        journal_entry.save(update_fields=["status", "approved_by", "updated_at"])
        AuditLogService.record_model_change(
            action=AuditAction.APPROVE,
            module=AuditModule.ACCOUNTING,
            instance=journal_entry,
            user=approved_by,
            after_data=serialize_model_instance(journal_entry, fields=["entry_number", "status", "approved_by"]),
            metadata={"event": "journal_entry_approved"},
        )
        return journal_entry

    @classmethod
    @transaction.atomic
    def post_manual_journal_entry(cls, *, journal_entry_id, posted_by=None) -> JournalEntry:
        journal_entry = JournalEntry.objects.select_for_update().get(id=journal_entry_id)
        if journal_entry.status == JournalEntry.Status.POSTED:
            return journal_entry
        if journal_entry.source_type not in {JournalEntry.SourceType.MANUAL, JournalEntry.SourceType.REVERSAL}:
            raise _validation_error("Only manual journal entries can be posted through this endpoint.")
        if journal_entry.status != JournalEntry.Status.APPROVED:
            raise _validation_error("Only approved journal entries can be posted.")
        if journal_entry.created_by_id and posted_by and journal_entry.created_by_id == posted_by.id:
            raise _validation_error("Maker-checker violation: journal creator cannot post the same journal.")
        return AccountingPostingService.post_journal_entry(journal_entry, posted_by=posted_by)

    @classmethod
    @transaction.atomic
    def reverse_journal_entry(cls, *, journal_entry_id, reversed_by=None, reversal_date_ad=None, narration="") -> JournalEntry:
        original = (
            JournalEntry.objects.select_for_update()
            .select_related("organization", "branch", "academic_year", "academic_period")
            .prefetch_related("lines")
            .get(id=journal_entry_id)
        )
        if original.status != JournalEntry.Status.POSTED:
            raise _validation_error("Only posted journal entries can be reversed.")
        if original.reversal_entries.exists():
            raise _validation_error("Journal entry has already been reversed.")
        if original.created_by_id and reversed_by and original.created_by_id == reversed_by.id:
            raise _validation_error("Maker-checker violation: journal creator cannot reverse the same journal.")

        reversal = JournalEntry.objects.create(
            organization=original.organization,
            branch=original.branch,
            academic_year=original.academic_year,
            academic_period=original.academic_period,
            entry_number=cls._next_entry_number(organization_id=original.organization_id),
            entry_date_ad=reversal_date_ad or timezone.now().date(),
            entry_date_bs="",
            description=f"Reversal of {original.entry_number}",
            narration=narration or f"Reversal of journal entry {original.entry_number}",
            source_type=JournalEntry.SourceType.REVERSAL,
            source_app="accounting",
            source_model="JournalEntry",
            source_object_id=original.id,
            source_number=original.entry_number,
            status=JournalEntry.Status.APPROVED,
            created_by=reversed_by,
            approved_by=reversed_by,
            reversed_entry=original,
        )
        for line in original.lines.all():
            JournalEntryLine.objects.create(
                journal_entry=reversal,
                organization=reversal.organization,
                branch=reversal.branch,
                account=line.account,
                description=f"Reversal: {line.description}"[:255],
                debit_amount=line.credit_amount,
                credit_amount=line.debit_amount,
                student_id=line.student_id,
                teacher_id=line.teacher_id,
                class_id=line.class_id,
            )
        posted_reversal = AccountingPostingService.post_journal_entry(reversal, posted_by=reversed_by)
        AuditLogService.record_model_change(
            action=AuditAction.REVERSE,
            module=AuditModule.ACCOUNTING,
            instance=original,
            user=reversed_by,
            after_data=serialize_model_instance(original, fields=["entry_number", "status"]),
            metadata={"event": "journal_entry_reversed", "reversal_entry_id": str(posted_reversal.id)},
        )
        return posted_reversal

    @classmethod
    @transaction.atomic
    def attach_accounting_document(
        cls,
        *,
        journal_entry_id,
        document_type,
        reference_number="",
        file_path="",
        description="",
        uploaded_by=None,
    ) -> AccountingDocument:
        journal_entry = JournalEntry.objects.select_related("organization").get(id=journal_entry_id)
        document = AccountingDocument.objects.create(
            organization=journal_entry.organization,
            journal_entry=journal_entry,
            document_type=document_type,
            reference_number=reference_number,
            file_path=file_path,
            description=description,
            uploaded_by=uploaded_by,
        )
        AuditLogService.record_model_change(
            action=AuditAction.CREATE,
            module=AuditModule.ACCOUNTING,
            instance=document,
            user=uploaded_by,
            after_data=serialize_model_instance(document, fields=["document_type", "reference_number", "file_path"]),
            metadata={"event": "accounting_document_attached", "journal_entry_id": str(journal_entry.id)},
        )
        return document


class AccountingPostingService:
    @staticmethod
    def compute_totals(journal_entry: JournalEntry) -> tuple[Decimal, Decimal]:
        totals = journal_entry.lines.aggregate(
            debit_total=Sum("debit_amount", default=Decimal("0.00")),
            credit_total=Sum("credit_amount", default=Decimal("0.00")),
        )
        return totals["debit_total"], totals["credit_total"]

    @classmethod
    def validate_balanced(cls, journal_entry: JournalEntry) -> tuple[Decimal, Decimal]:
        debit_total, credit_total = cls.compute_totals(journal_entry)
        if debit_total != credit_total:
            raise ValidationError("Journal entry debits and credits must be equal.")
        return debit_total, credit_total

    @staticmethod
    def validate_line_count(journal_entry: JournalEntry) -> None:
        if journal_entry.lines.count() < 2:
            raise ValidationError("Journal entry must have at least two lines.")

    @staticmethod
    def validate_period_open(journal_entry: JournalEntry) -> None:
        if journal_entry.academic_year.status == AcademicYear.Status.HARD_CLOSED:
            raise ValidationError("Cannot post to a hard-closed academic year.")
        if journal_entry.academic_period and journal_entry.academic_period.status == AcademicPeriod.Status.HARD_CLOSED:
            raise ValidationError("Cannot post to a hard-closed academic period.")

    @classmethod
    @transaction.atomic
    def post_journal_entry(cls, journal_entry: JournalEntry, *, posted_by=None) -> JournalEntry:
        locked_entry = (
            JournalEntry.objects.select_for_update()
            .select_related("academic_year", "academic_period")
            .get(id=journal_entry.id)
        )

        if locked_entry.status == JournalEntry.Status.POSTED:
            return locked_entry

        cls.validate_line_count(locked_entry)
        cls.validate_balanced(locked_entry)
        cls.validate_period_open(locked_entry)

        now = timezone.now()
        locked_entry.status = JournalEntry.Status.POSTED
        locked_entry.posted_at = now
        locked_entry.posting_date_ad = now.date()
        locked_entry.posted_by = posted_by
        locked_entry.save(update_fields=["status", "posted_at", "posting_date_ad", "posted_by", "updated_at"])
        AuditLogService.record_model_change(
            action=AuditAction.POST,
            module=AuditModule.ACCOUNTING,
            instance=locked_entry,
            user=posted_by,
            after_data=serialize_model_instance(
                locked_entry,
                fields=["entry_number", "status", "posting_date_ad", "posted_at", "posted_by"],
            ),
            metadata={"event": "journal_entry_posted"},
        )
        return locked_entry
