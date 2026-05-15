from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from academic.models import AcademicPeriod, AcademicYear
from common.models import BaseModel
from common.money import ZERO_MONEY, money_field, validate_money_amount
from organizations.models import Branch, Organization


class Account(BaseModel):
    class AccountType(models.TextChoices):
        ASSET = "asset", "Asset"
        LIABILITY = "liability", "Liability"
        EQUITY = "equity", "Equity"
        REVENUE = "revenue", "Revenue"
        EXPENSE = "expense", "Expense"
        CONTRA_ASSET = "contra_asset", "Contra Asset"
        CONTRA_REVENUE = "contra_revenue", "Contra Revenue"
        OTHER_INCOME = "other_income", "Other Income"
        OTHER_EXPENSE = "other_expense", "Other Expense"

    class NormalBalance(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="accounts")
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=30, choices=AccountType.choices, db_index=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
    normal_balance = models.CharField(max_length=10, choices=NormalBalance.choices)
    is_system_account = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["organization__display_name", "code"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "code"], name="unique_account_code_per_organization"),
        ]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["organization", "account_type"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def clean(self) -> None:
        super().clean()
        if self.parent_id and self.organization_id != self.parent.organization_id:
            raise ValidationError({"parent": "Parent account must belong to the same organization."})


class JournalEntry(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        POSTED = "posted", "Posted"
        REVERSED = "reversed", "Reversed"
        VOID = "void", "Void"

    class SourceType(models.TextChoices):
        MANUAL = "manual", "Manual"
        SYSTEM = "system", "System"
        OPENING = "opening", "Opening"
        CLOSING = "closing", "Closing"
        REVERSAL = "reversal", "Reversal"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="journal_entries")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.PROTECT, related_name="journal_entries")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="journal_entries")
    academic_period = models.ForeignKey(
        AcademicPeriod,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="journal_entries",
    )
    entry_number = models.CharField(max_length=50)
    entry_date_ad = models.DateField(db_index=True)
    entry_date_bs = models.CharField(max_length=10)
    posting_date_ad = models.DateField(null=True, blank=True, db_index=True)
    posting_date_bs = models.CharField(max_length=10, blank=True)
    description = models.CharField(max_length=255)
    narration = models.TextField(blank=True)
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.MANUAL, db_index=True)
    source_app = models.CharField(max_length=100, blank=True)
    source_model = models.CharField(max_length=100, blank=True)
    source_object_id = models.UUIDField(null=True, blank=True)
    source_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT, db_index=True)
    is_system_generated = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_journal_entries",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_journal_entries",
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="posted_journal_entries",
    )
    reversed_entry = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reversal_entries",
    )
    posted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["organization__display_name", "-entry_date_ad", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "entry_number"], name="unique_journal_entry_number_per_org"),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "entry_date_ad"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["academic_period", "status"]),
            models.Index(fields=["source_app", "source_model"]),
        ]

    def __str__(self) -> str:
        return self.entry_number

    @property
    def is_posted(self) -> bool:
        return self.status == self.Status.POSTED

    @property
    def is_immutable(self) -> bool:
        return self.status in {self.Status.POSTED, self.Status.REVERSED, self.Status.VOID}

    def save(self, *args, **kwargs):
        if not self._state.adding:
            existing_status = type(self).objects.only("status").get(pk=self.pk).status
            if existing_status in {self.Status.POSTED, self.Status.REVERSED, self.Status.VOID} and not getattr(
                self, "_allow_immutable_update", False
            ):
                raise ValidationError("Posted, reversed, and void journal entries are immutable. Use reversal entries.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_immutable:
            raise ValidationError("Posted, reversed, and void journal entries cannot be deleted.")
        return super().delete(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if self.branch_id and self.organization_id != self.branch.organization_id:
            raise ValidationError({"branch": "Branch must belong to the same organization as the journal entry."})
        if self.academic_year_id and self.organization_id != self.academic_year.organization_id:
            raise ValidationError({"academic_year": "Academic year must belong to the journal entry organization."})
        if self.academic_period_id:
            if self.organization_id != self.academic_period.organization_id:
                raise ValidationError({"academic_period": "Academic period must belong to the journal entry organization."})
            if self.academic_year_id != self.academic_period.academic_year_id:
                raise ValidationError({"academic_period": "Academic period must belong to the selected academic year."})


class JournalEntryLine(BaseModel):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="journal_entry_lines")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.PROTECT, related_name="journal_entry_lines")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="journal_entry_lines")
    description = models.CharField(max_length=255, blank=True)
    debit_amount = money_field(default=ZERO_MONEY)
    credit_amount = money_field(default=ZERO_MONEY)
    student_id = models.UUIDField(null=True, blank=True)
    teacher_id = models.UUIDField(null=True, blank=True)
    class_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["journal_entry", "created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(debit_amount__gt=Decimal("0.00")) & Q(credit_amount=Decimal("0.00")))
                    | (Q(credit_amount__gt=Decimal("0.00")) & Q(debit_amount=Decimal("0.00")))
                ),
                name="journal_line_has_debit_or_credit_only",
            ),
            models.CheckConstraint(
                condition=Q(debit_amount__gte=Decimal("0.00")) & Q(credit_amount__gte=Decimal("0.00")),
                name="journal_line_amounts_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "account"]),
            models.Index(fields=["journal_entry", "account"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["student_id"]),
            models.Index(fields=["teacher_id"]),
            models.Index(fields=["class_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.journal_entry.entry_number} - {self.account.code}"

    def save(self, *args, **kwargs):
        if self.journal_entry_id:
            entry_status = self.journal_entry.status
            if entry_status in {
                JournalEntry.Status.POSTED,
                JournalEntry.Status.REVERSED,
                JournalEntry.Status.VOID,
            } and not getattr(self, "_allow_immutable_update", False):
                raise ValidationError("Lines for posted, reversed, and void journal entries are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.journal_entry.status in {
            JournalEntry.Status.POSTED,
            JournalEntry.Status.REVERSED,
            JournalEntry.Status.VOID,
        }:
            raise ValidationError("Lines for posted, reversed, and void journal entries cannot be deleted.")
        return super().delete(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        debit = validate_money_amount(self.debit_amount)
        credit = validate_money_amount(self.credit_amount)
        if debit > ZERO_MONEY and credit > ZERO_MONEY:
            raise ValidationError("A journal line cannot have both debit and credit.")
        if debit == ZERO_MONEY and credit == ZERO_MONEY:
            raise ValidationError("A journal line must have either debit or credit.")
        if self.journal_entry_id and self.organization_id != self.journal_entry.organization_id:
            raise ValidationError({"organization": "Line organization must match journal entry organization."})
        if self.account_id and self.organization_id != self.account.organization_id:
            raise ValidationError({"account": "Account must belong to the same organization as the journal entry line."})
        if self.branch_id and self.organization_id != self.branch.organization_id:
            raise ValidationError({"branch": "Branch must belong to the same organization as the journal entry line."})


class AccountingDocument(BaseModel):
    class DocumentType(models.TextChoices):
        RECEIPT = "receipt", "Receipt"
        VOUCHER = "voucher", "Voucher"
        INVOICE = "invoice", "Invoice"
        CONTRACT = "contract", "Contract"
        BANK_STATEMENT = "bank_statement", "Bank Statement"
        SUPPORTING_DOCUMENT = "supporting_document", "Supporting Document"
        OTHER = "other", "Other"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="accounting_documents")
    journal_entry = models.ForeignKey(
        JournalEntry,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(max_length=50, choices=DocumentType.choices, default=DocumentType.SUPPORTING_DOCUMENT)
    reference_number = models.CharField(max_length=100, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_accounting_documents",
    )

    class Meta:
        ordering = ["organization__display_name", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "document_type"]),
            models.Index(fields=["journal_entry"]),
            models.Index(fields=["reference_number"]),
        ]

    def __str__(self) -> str:
        return self.reference_number or self.get_document_type_display()


class LedgerSnapshot(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="ledger_snapshots")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="ledger_snapshots")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="ledger_snapshots")
    academic_period = models.ForeignKey(
        AcademicPeriod,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="ledger_snapshots",
    )
    debit_total = money_field(default=ZERO_MONEY)
    credit_total = money_field(default=ZERO_MONEY)
    balance = money_field(default=ZERO_MONEY)
    snapshot_at = models.DateTimeField()

    class Meta:
        ordering = ["organization__display_name", "account__code", "-snapshot_at"]
        indexes = [
            models.Index(fields=["organization", "account"]),
            models.Index(fields=["academic_year", "academic_period"]),
            models.Index(fields=["snapshot_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.account.code} snapshot at {self.snapshot_at.isoformat()}"
