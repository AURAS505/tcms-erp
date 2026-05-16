from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from accounting.models import Account, JournalEntry, JournalEntryLine
from accounting.services import AccountingPostingService
from common.audit import AuditAction, AuditLogService, AuditModule, serialize_model_instance
from common.money import ZERO_MONEY, quantize_money

from .models import TeacherEarning, TeacherPayment, TeacherPaymentAllocation


@dataclass
class TeacherPaymentAllocationInput:
    teacher_earning_id: str
    amount_allocated: Decimal
    notes: str = ""


class PayrollServiceMixin:
    CASH_ACCOUNT_CODE = "1110"
    BANK_ACCOUNT_CODE = "1120"
    WALLET_ACCOUNT_CODE = "1130"
    TEACHER_PAYABLE_CODE = "2110"
    TEACHER_SALARY_EXPENSE_CODE = "5100"

    @staticmethod
    def _get_account_by_code(*, organization_id, code: str) -> Account:
        try:
            return Account.objects.get(organization_id=organization_id, code=code, is_active=True)
        except Account.DoesNotExist as exc:
            raise ValidationError(
                f"Accounting configuration error: account code '{code}' is required and must be active."
            ) from exc

    @classmethod
    def _generate_journal_entry_number(cls, *, organization_id) -> str:
        last_entry = (
            JournalEntry.objects.select_for_update().filter(organization_id=organization_id).order_by("-created_at", "-id").first()
        )
        if last_entry is None:
            sequence = 1
        else:
            sequence = JournalEntry.objects.filter(organization_id=organization_id).count() + 1
        return f"JV-{sequence:06d}"

    @classmethod
    def _next_sequence_for_payments(cls, *, organization_id) -> int:
        last_payment = (
            TeacherPayment.objects.select_for_update()
            .filter(organization_id=organization_id)
            .order_by("-created_at", "-id")
            .first()
        )
        if last_payment is None:
            return 1
        return TeacherPayment.objects.filter(organization_id=organization_id).count() + 1


class TeacherEarningService(PayrollServiceMixin):
    @classmethod
    def calculate_teacher_share(cls, *, gross_amount, cut_percentage) -> Decimal:
        gross = quantize_money(gross_amount)
        cut = Decimal(cut_percentage)
        if cut < Decimal("0") or cut > Decimal("100"):
            raise ValidationError("Teacher cut percentage must be between 0 and 100.")
        return quantize_money(gross * (cut / Decimal("100")))

    @classmethod
    def validate_earning_amounts(cls, *, gross_amount, deduction_amount, net_amount=None) -> tuple[Decimal, Decimal, Decimal]:
        gross = quantize_money(gross_amount)
        deduction = quantize_money(deduction_amount)
        if gross <= ZERO_MONEY:
            raise ValidationError("Gross amount must be greater than zero.")
        if deduction < ZERO_MONEY:
            raise ValidationError("Deduction amount cannot be negative.")
        computed_net = quantize_money(gross - deduction)
        if computed_net < ZERO_MONEY:
            raise ValidationError("Deduction cannot exceed gross amount.")
        if net_amount is not None:
            provided_net = quantize_money(net_amount)
            if provided_net != computed_net:
                raise ValidationError("Net amount does not match gross minus deduction.")
        return gross, deduction, computed_net

    @classmethod
    @transaction.atomic
    def create_manual_earning(
        cls,
        *,
        organization,
        branch,
        academic_year,
        teacher,
        earning_date_ad,
        gross_amount,
        deduction_amount=ZERO_MONEY,
        net_amount=None,
        earning_source=TeacherEarning.EarningSource.MANUAL_ADJUSTMENT,
        created_by=None,
        academic_period=None,
        earning_date_bs="",
        period_label="",
        student=None,
        class_room=None,
        class_enrollment=None,
        student_payment=None,
        notes="",
        status=TeacherEarning.Status.DRAFT,
    ) -> TeacherEarning:
        gross, deduction, computed_net = cls.validate_earning_amounts(
            gross_amount=gross_amount,
            deduction_amount=deduction_amount,
            net_amount=net_amount,
        )
        earning = TeacherEarning.objects.create(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            academic_period=academic_period,
            teacher=teacher,
            student=student,
            class_room=class_room,
            class_enrollment=class_enrollment,
            student_payment=student_payment,
            earning_source=earning_source,
            earning_date_ad=earning_date_ad,
            earning_date_bs=earning_date_bs,
            period_label=period_label,
            gross_amount=gross,
            deduction_amount=deduction,
            net_amount=computed_net,
            paid_amount=ZERO_MONEY,
            balance_amount=computed_net,
            created_by=created_by,
            status=status,
            notes=notes,
        )
        earning.full_clean()
        earning.save()
        return earning

    @classmethod
    @transaction.atomic
    def create_earning_from_student_payment(
        cls,
        *,
        teacher,
        student_payment,
        cut_percentage,
        created_by=None,
        notes="",
    ) -> TeacherEarning:
        if student_payment.status not in {student_payment.Status.APPROVED, student_payment.Status.POSTED}:
            raise ValidationError("Teacher earning can only be created from approved/posted student payment.")
        gross_share = cls.calculate_teacher_share(gross_amount=student_payment.amount, cut_percentage=cut_percentage)
        return cls.create_manual_earning(
            organization=student_payment.organization,
            branch=student_payment.branch,
            academic_year=student_payment.academic_year,
            teacher=teacher,
            student=student_payment.student,
            student_payment=student_payment,
            earning_source=TeacherEarning.EarningSource.STUDENT_PAYMENT,
            earning_date_ad=student_payment.payment_date_ad,
            earning_date_bs=student_payment.payment_date_bs,
            gross_amount=gross_share,
            deduction_amount=ZERO_MONEY,
            created_by=created_by,
            notes=notes or f"Earning from student payment {student_payment.receipt_number or student_payment.draft_receipt_number}",
            status=TeacherEarning.Status.DRAFT,
        )

    @classmethod
    @transaction.atomic
    def approve_earning(cls, *, earning_id, approved_by) -> TeacherEarning:
        earning = TeacherEarning.objects.select_for_update().get(id=earning_id)
        if earning.created_by_id and earning.created_by_id == getattr(approved_by, "id", None):
            raise ValidationError("Maker-checker violation: earning creator cannot approve the same earning.")
        if earning.status not in {TeacherEarning.Status.DRAFT, TeacherEarning.Status.PENDING_APPROVAL}:
            raise ValidationError("Only draft/pending earnings can be approved.")
        earning.status = TeacherEarning.Status.APPROVED
        earning.approved_by = approved_by
        earning.approved_at = timezone.now()
        earning._allow_immutable_update = True
        earning.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        return earning

    @classmethod
    @transaction.atomic
    def post_earning(cls, *, earning_id, posted_by=None) -> TeacherEarning:
        earning = (
            TeacherEarning.objects.select_for_update()
            .select_related("organization", "branch", "academic_year", "academic_period", "teacher", "created_by", "approved_by")
            .get(id=earning_id)
        )
        if earning.status == TeacherEarning.Status.POSTED:
            return earning
        if earning.status != TeacherEarning.Status.APPROVED:
            raise ValidationError("Only approved earnings can be posted.")

        salary_expense = cls._get_account_by_code(
            organization_id=earning.organization_id,
            code=cls.TEACHER_SALARY_EXPENSE_CODE,
        )
        teacher_payable = cls._get_account_by_code(
            organization_id=earning.organization_id,
            code=cls.TEACHER_PAYABLE_CODE,
        )
        entry = JournalEntry.objects.create(
            organization=earning.organization,
            branch=earning.branch,
            academic_year=earning.academic_year,
            academic_period=earning.academic_period,
            entry_number=cls._generate_journal_entry_number(organization_id=earning.organization_id),
            entry_date_ad=earning.earning_date_ad,
            entry_date_bs=earning.earning_date_bs or "",
            description=f"Teacher earning {earning.id}",
            narration=earning.notes,
            source_type=JournalEntry.SourceType.SYSTEM,
            source_app="payroll",
            source_model="TeacherEarning",
            source_object_id=earning.id,
            source_number=str(earning.id),
            status=JournalEntry.Status.APPROVED,
            is_system_generated=True,
            created_by=earning.created_by,
            approved_by=earning.approved_by or posted_by,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=earning.organization,
            branch=earning.branch,
            account=salary_expense,
            debit_amount=earning.net_amount,
            credit_amount=ZERO_MONEY,
            teacher_id=earning.teacher_id,
            student_id=earning.student_id,
            class_id=earning.class_room_id,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=earning.organization,
            branch=earning.branch,
            account=teacher_payable,
            debit_amount=ZERO_MONEY,
            credit_amount=earning.net_amount,
            teacher_id=earning.teacher_id,
            student_id=earning.student_id,
            class_id=earning.class_room_id,
        )
        posted_entry = AccountingPostingService.post_journal_entry(entry, posted_by=posted_by or earning.approved_by)

        earning.status = TeacherEarning.Status.POSTED
        earning.posted_at = timezone.now()
        earning._allow_immutable_update = True
        earning.save(update_fields=["status", "posted_at", "updated_at"])
        AuditLogService.record_model_change(
            action=AuditAction.POST,
            module=AuditModule.PAYROLL,
            instance=earning,
            user=posted_by or earning.approved_by,
            after_data=serialize_model_instance(earning, fields=["status", "posted_at"]),
            metadata={"event": "teacher_earning_posted", "journal_entry_id": str(posted_entry.id)},
        )
        return earning


class TeacherPaymentService(PayrollServiceMixin):
    @classmethod
    def generate_draft_voucher_number(cls, *, organization_id) -> str:
        sequence = cls._next_sequence_for_payments(organization_id=organization_id)
        return f"TDV-{sequence:06d}"

    @classmethod
    def generate_official_voucher_number(cls, *, organization_id) -> str:
        sequence = cls._next_sequence_for_payments(organization_id=organization_id)
        return f"TV-{sequence:06d}"

    @classmethod
    def _normalize_allocations(cls, allocations: list[TeacherPaymentAllocationInput | dict]) -> list[TeacherPaymentAllocationInput]:
        normalized: list[TeacherPaymentAllocationInput] = []
        for item in allocations:
            if isinstance(item, TeacherPaymentAllocationInput):
                normalized.append(item)
            else:
                normalized.append(
                    TeacherPaymentAllocationInput(
                        teacher_earning_id=str(item["teacher_earning_id"]),
                        amount_allocated=quantize_money(item["amount_allocated"]),
                        notes=item.get("notes", ""),
                    )
                )
        return normalized

    @classmethod
    def validate_payment_allocations(
        cls,
        *,
        payment: TeacherPayment,
        allocations: list[TeacherPaymentAllocationInput] | None = None,
    ) -> None:
        if allocations is None:
            allocations = [
                TeacherPaymentAllocationInput(
                    teacher_earning_id=str(alloc.teacher_earning_id),
                    amount_allocated=alloc.amount_allocated,
                    notes=alloc.notes,
                )
                for alloc in payment.allocations.all()
            ]
        total_allocated = ZERO_MONEY
        running: dict[str, Decimal] = {}
        for item in allocations:
            amount = quantize_money(item.amount_allocated)
            if amount <= ZERO_MONEY:
                raise ValidationError("Allocation amount must be greater than zero.")
            total_allocated += amount
            earning = TeacherEarning.objects.get(id=item.teacher_earning_id)
            if (
                earning.organization_id != payment.organization_id
                or earning.branch_id != payment.branch_id
                or earning.teacher_id != payment.teacher_id
            ):
                raise ValidationError("Allocation earning must belong to the same organization, branch, and teacher.")
            if earning.status not in {TeacherEarning.Status.POSTED, TeacherEarning.Status.PARTIAL}:
                raise ValidationError("Teacher earning must be posted before payment allocation.")
            running.setdefault(item.teacher_earning_id, ZERO_MONEY)
            running[item.teacher_earning_id] += amount
            if running[item.teacher_earning_id] > earning.balance_amount:
                raise ValidationError("Allocation cannot exceed teacher earning balance.")
        if total_allocated > payment.amount:
            raise ValidationError("Total allocation cannot exceed payment amount.")

    @classmethod
    @transaction.atomic
    def create_draft_payment(
        cls,
        *,
        organization,
        branch,
        academic_year,
        teacher,
        payment_date_ad,
        payment_method: str,
        amount,
        created_by=None,
        academic_period=None,
        payment_batch=None,
        payment_date_bs="",
        deduction_amount=ZERO_MONEY,
        net_paid_amount=None,
        reference_number="",
        acknowledgement_file_path="",
        notes="",
        allocations: list[TeacherPaymentAllocationInput | dict] | None = None,
    ) -> TeacherPayment:
        amount = quantize_money(amount)
        deduction_amount = quantize_money(deduction_amount)
        if amount <= ZERO_MONEY:
            raise ValidationError("Payment amount must be greater than zero.")
        if net_paid_amount is None:
            net_paid_amount = quantize_money(amount - deduction_amount)
        net_paid_amount = quantize_money(net_paid_amount)
        if net_paid_amount < ZERO_MONEY:
            raise ValidationError("Net paid amount cannot be negative.")
        payment = TeacherPayment.objects.create(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            academic_period=academic_period,
            payment_batch=payment_batch,
            teacher=teacher,
            draft_voucher_number=cls.generate_draft_voucher_number(organization_id=organization.id),
            payment_date_ad=payment_date_ad,
            payment_date_bs=payment_date_bs,
            payment_method=payment_method,
            amount=amount,
            deduction_amount=deduction_amount,
            net_paid_amount=net_paid_amount,
            reference_number=reference_number,
            acknowledgement_file_path=acknowledgement_file_path,
            status=TeacherPayment.Status.DRAFT,
            created_by=created_by,
            notes=notes,
        )
        payment.full_clean()
        payment.save()
        allocations = allocations or []
        if allocations:
            normalized = cls._normalize_allocations(allocations)
            cls.validate_payment_allocations(payment=payment, allocations=normalized)
            for item in normalized:
                TeacherPaymentAllocation.objects.create(
                    teacher_payment=payment,
                    teacher_earning_id=item.teacher_earning_id,
                    amount_allocated=item.amount_allocated,
                    notes=item.notes,
                )
        cls._refresh_batch_total(payment.payment_batch)
        return payment

    @classmethod
    @transaction.atomic
    def approve_payment(cls, *, payment_id, approved_by) -> TeacherPayment:
        payment = TeacherPayment.objects.select_for_update().get(id=payment_id)
        if payment.created_by_id and payment.created_by_id == getattr(approved_by, "id", None):
            raise ValidationError("Maker-checker violation: payment creator cannot approve the same payment.")
        if payment.status not in {TeacherPayment.Status.DRAFT, TeacherPayment.Status.SUBMITTED}:
            raise ValidationError("Only draft/submitted teacher payments can be approved.")
        payment.status = TeacherPayment.Status.APPROVED
        payment.approved_by = approved_by
        payment.approved_at = timezone.now()
        payment._allow_immutable_update = True
        payment.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        return cls.post_payment(payment_id=payment.id, approved_by=approved_by)

    @classmethod
    @transaction.atomic
    def post_payment(cls, *, payment_id, approved_by=None) -> TeacherPayment:
        payment = (
            TeacherPayment.objects.select_for_update()
            .select_related("organization", "branch", "academic_year", "academic_period", "teacher", "created_by", "approved_by")
            .get(id=payment_id)
        )
        if payment.status == TeacherPayment.Status.POSTED:
            return payment
        if payment.status != TeacherPayment.Status.APPROVED:
            raise ValidationError("Only approved teacher payments can be posted.")
        if payment.created_by_id and approved_by and payment.created_by_id == approved_by.id:
            raise ValidationError("Maker-checker violation: payment creator cannot approve/post the same payment.")
        allocations = list(payment.allocations.select_for_update())
        if not allocations:
            raise ValidationError("Teacher payment requires at least one allocation.")
        cls.validate_payment_allocations(payment=payment)
        if not payment.voucher_number:
            payment.voucher_number = cls.generate_official_voucher_number(organization_id=payment.organization_id)
        if approved_by and not payment.approved_by_id:
            payment.approved_by = approved_by
            payment.approved_at = timezone.now()

        cls.apply_payment_to_earnings(payment=payment, allocations=allocations)
        journal_entry = cls._create_payment_journal_entry(payment=payment, posted_by=approved_by or payment.approved_by)

        payment.status = TeacherPayment.Status.POSTED
        payment.posted_at = timezone.now()
        payment._allow_immutable_update = True
        payment.save(update_fields=["voucher_number", "approved_by", "approved_at", "status", "posted_at", "updated_at"])
        cls._refresh_batch_total(payment.payment_batch)
        AuditLogService.record_model_change(
            action=AuditAction.POST,
            module=AuditModule.PAYROLL,
            instance=payment,
            user=approved_by or payment.approved_by,
            after_data=serialize_model_instance(payment, fields=["voucher_number", "status", "posted_at"]),
            metadata={"event": "teacher_payment_posted", "journal_entry_id": str(journal_entry.id)},
        )
        return payment

    @classmethod
    def apply_payment_to_earnings(cls, *, payment: TeacherPayment, allocations: list[TeacherPaymentAllocation]) -> None:
        for alloc in allocations:
            earning = TeacherEarning.objects.select_for_update().get(id=alloc.teacher_earning_id)
            amount = quantize_money(alloc.amount_allocated)
            earning.paid_amount = quantize_money(earning.paid_amount + amount)
            if earning.paid_amount > earning.net_amount:
                raise ValidationError("Teacher earning paid amount cannot exceed earning net amount.")
            earning.balance_amount = quantize_money(earning.net_amount - earning.paid_amount)
            if earning.balance_amount == ZERO_MONEY:
                earning.status = TeacherEarning.Status.PAID
            elif earning.paid_amount > ZERO_MONEY:
                earning.status = TeacherEarning.Status.PARTIAL
            elif earning.status in {TeacherEarning.Status.APPROVED, TeacherEarning.Status.POSTED}:
                earning.status = TeacherEarning.Status.POSTED
            earning._allow_immutable_update = True
            earning.save(update_fields=["paid_amount", "balance_amount", "status", "updated_at"])

    @classmethod
    def void_payment_placeholder(cls, *, payment_id, reason: str, voided_by=None) -> TeacherPayment:
        payment = TeacherPayment.objects.get(id=payment_id)
        if payment.status == TeacherPayment.Status.POSTED:
            raise ValidationError("Void workflow with reversal is not implemented yet.")
        payment.void_reason = reason
        payment.voided_by = voided_by
        payment.voided_at = timezone.now()
        payment.status = TeacherPayment.Status.VOIDED
        payment._allow_immutable_update = True
        payment.save(update_fields=["void_reason", "voided_by", "voided_at", "status", "updated_at"])
        return payment

    @classmethod
    def _resolve_credit_account(cls, *, payment: TeacherPayment) -> Account:
        if payment.payment_method == TeacherPayment.PaymentMethod.CASH:
            return cls._get_account_by_code(organization_id=payment.organization_id, code=cls.CASH_ACCOUNT_CODE)
        if payment.payment_method == TeacherPayment.PaymentMethod.WALLET:
            return cls._get_account_by_code(organization_id=payment.organization_id, code=cls.WALLET_ACCOUNT_CODE)
        return cls._get_account_by_code(organization_id=payment.organization_id, code=cls.BANK_ACCOUNT_CODE)

    @classmethod
    def _create_payment_journal_entry(cls, *, payment: TeacherPayment, posted_by=None) -> JournalEntry:
        debit_account = cls._get_account_by_code(organization_id=payment.organization_id, code=cls.TEACHER_PAYABLE_CODE)
        credit_account = cls._resolve_credit_account(payment=payment)
        journal_entry = JournalEntry.objects.create(
            organization=payment.organization,
            branch=payment.branch,
            academic_year=payment.academic_year,
            academic_period=payment.academic_period,
            entry_number=cls._generate_journal_entry_number(organization_id=payment.organization_id),
            entry_date_ad=payment.payment_date_ad,
            entry_date_bs=payment.payment_date_bs or "",
            description=f"Teacher payment {payment.voucher_number or payment.draft_voucher_number}",
            narration=payment.notes,
            source_type=JournalEntry.SourceType.SYSTEM,
            source_app="payroll",
            source_model="TeacherPayment",
            source_object_id=payment.id,
            source_number=payment.voucher_number or payment.draft_voucher_number or "",
            status=JournalEntry.Status.APPROVED,
            is_system_generated=True,
            created_by=payment.created_by,
            approved_by=payment.approved_by,
        )
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            organization=payment.organization,
            branch=payment.branch,
            account=debit_account,
            debit_amount=payment.amount,
            credit_amount=ZERO_MONEY,
            teacher_id=payment.teacher_id,
        )
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            organization=payment.organization,
            branch=payment.branch,
            account=credit_account,
            debit_amount=ZERO_MONEY,
            credit_amount=payment.amount,
            teacher_id=payment.teacher_id,
        )
        return AccountingPostingService.post_journal_entry(journal_entry, posted_by=posted_by)

    @staticmethod
    def _refresh_batch_total(batch) -> None:
        if not batch:
            return
        total = batch.payments.aggregate(total=Sum("amount", default=Decimal("0.00")))["total"]
        batch.total_amount = quantize_money(total)
        batch._allow_immutable_update = True
        batch.save(update_fields=["total_amount", "updated_at"])
