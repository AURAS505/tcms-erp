from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from academic.models import AcademicPeriod, AcademicYear

from .models import JournalEntry


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
        return locked_entry
