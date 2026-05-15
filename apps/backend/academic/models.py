from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.models import BaseModel
from organizations.models import Organization


class AcademicYear(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        SOFT_CLOSED = "soft_closed", "Soft Closed"
        HARD_CLOSED = "hard_closed", "Hard Closed"
        ARCHIVED = "archived", "Archived"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="academic_years")
    name = models.CharField(max_length=50)
    bs_start_year = models.PositiveSmallIntegerField()
    bs_end_year = models.PositiveSmallIntegerField()
    bs_start_date = models.CharField(max_length=10)
    bs_end_date = models.CharField(max_length=10)
    ad_start_date = models.DateField(db_index=True)
    ad_end_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    is_active = models.BooleanField(default=False, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["organization__display_name", "-ad_start_date"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_academic_year_name_per_organization"),
            models.UniqueConstraint(
                fields=["organization"],
                condition=models.Q(is_active=True),
                name="unique_active_academic_year_per_organization",
            ),
            models.CheckConstraint(
                condition=models.Q(ad_start_date__lte=models.F("ad_end_date")),
                name="academic_year_ad_start_before_end",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["bs_start_year", "bs_end_year"]),
            models.Index(fields=["ad_start_date", "ad_end_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization.display_name} - {self.name}"


class AcademicPeriod(BaseModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        SOFT_CLOSED = "soft_closed", "Soft Closed"
        HARD_CLOSED = "hard_closed", "Hard Closed"
        ARCHIVED = "archived", "Archived"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="academic_periods")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="periods")
    name = models.CharField(max_length=100)
    period_order = models.PositiveSmallIntegerField()
    bs_month = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    bs_month_name = models.CharField(max_length=30)
    bs_year = models.PositiveSmallIntegerField()
    bs_start_date = models.CharField(max_length=10)
    bs_end_date = models.CharField(max_length=10)
    ad_start_date = models.DateField(db_index=True)
    ad_end_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["academic_year", "period_order"]
        constraints = [
            models.UniqueConstraint(fields=["academic_year", "period_order"], name="unique_period_order_per_academic_year"),
            models.UniqueConstraint(fields=["academic_year", "bs_year", "bs_month"], name="unique_bs_month_per_academic_year"),
            models.CheckConstraint(
                condition=models.Q(ad_start_date__lte=models.F("ad_end_date")),
                name="academic_period_ad_start_before_end",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["academic_year", "is_active"]),
            models.Index(fields=["bs_year", "bs_month"]),
            models.Index(fields=["ad_start_date", "ad_end_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.academic_year.name} - {self.name}"

    def clean(self) -> None:
        super().clean()
        if self.academic_year_id and self.organization_id != self.academic_year.organization_id:
            raise ValidationError({"organization": "Period organization must match academic year organization."})
        if self.academic_year_id:
            if self.ad_start_date < self.academic_year.ad_start_date or self.ad_end_date > self.academic_year.ad_end_date:
                raise ValidationError("Period dates must fall inside the academic year date range.")


class NepaliCalendarDay(BaseModel):
    bs_date = models.CharField(max_length=10, unique=True, db_index=True)
    bs_year = models.PositiveSmallIntegerField(db_index=True)
    bs_month = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], db_index=True)
    bs_day = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(32)])
    ad_date = models.DateField(db_index=True)
    bs_month_name = models.CharField(max_length=30)
    is_month_start = models.BooleanField(default=False, db_index=True)
    is_month_end = models.BooleanField(default=False, db_index=True)
    is_holiday = models.BooleanField(default=False, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["ad_date"]
        indexes = [
            models.Index(fields=["bs_year", "bs_month"]),
            models.Index(fields=["ad_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.bs_date} / {self.ad_date.isoformat()}"


class AcademicYearRollover(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        VALIDATING = "validating", "Validating"
        READY = "ready", "Ready"
        EXECUTED = "executed", "Executed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="academic_year_rollovers")
    from_academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="rollovers_from",
    )
    to_academic_year = models.ForeignKey(
        AcademicYear,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rollovers_to",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    trial_balance_validated = models.BooleanField(default=False)
    revenue_expense_closing_completed = models.BooleanField(default=False)
    opening_balances_posted = models.BooleanField(default=False)
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="executed_academic_year_rollovers",
    )
    executed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["organization__display_name", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["from_academic_year", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization.display_name}: rollover from {self.from_academic_year.name}"

    def clean(self) -> None:
        super().clean()
        if self.from_academic_year_id and self.organization_id != self.from_academic_year.organization_id:
            raise ValidationError({"from_academic_year": "Source academic year must belong to the rollover organization."})
        if self.to_academic_year_id and self.organization_id != self.to_academic_year.organization_id:
            raise ValidationError({"to_academic_year": "Target academic year must belong to the rollover organization."})
