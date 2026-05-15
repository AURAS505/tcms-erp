from django.db import models
from django.utils import timezone

from accounts.models import Role
from common.models import BaseModel
from common.money import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS


class Organization(BaseModel):
    legal_name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True)
    vat_pan_number = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    logo_path = models.CharField(max_length=500, blank=True)
    default_currency = models.CharField(max_length=3, default="NPR")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["display_name"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["display_name"]),
        ]

    def __str__(self) -> str:
        return self.display_name


class Branch(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="branches")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    is_main_branch = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["organization__display_name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "code"], name="unique_branch_code_per_organization"),
            models.UniqueConstraint(
                fields=["organization"],
                condition=models.Q(is_main_branch=True),
                name="unique_main_branch_per_organization",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["organization", "code"]),
            models.Index(fields=["is_main_branch"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization.display_name} - {self.name}"


class OrganizationSetting(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="settings")
    key = models.CharField(max_length=150)
    value = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    is_system_setting = models.BooleanField(default=False)

    class Meta:
        ordering = ["organization__display_name", "key"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "key"], name="unique_setting_key_per_organization"),
        ]
        indexes = [
            models.Index(fields=["organization", "key"]),
            models.Index(fields=["is_system_setting"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization.display_name}: {self.key}"


class TaxRate(BaseModel):
    class TaxType(models.TextChoices):
        VAT = "vat", "VAT"
        PAN = "pan", "PAN"
        SERVICE_TAX = "service_tax", "Service Tax"
        OTHER = "other", "Other"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="tax_rates")
    name = models.CharField(max_length=150)
    rate_percentage = models.DecimalField(max_digits=7, decimal_places=4)
    tax_type = models.CharField(max_length=30, choices=TaxType.choices, default=TaxType.VAT)
    is_active = models.BooleanField(default=True, db_index=True)
    effective_from = models.DateField(default=timezone.localdate)
    effective_to = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["organization__display_name", "name", "-effective_from"]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["tax_type"]),
            models.Index(fields=["effective_from", "effective_to"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.rate_percentage}%)"


class ApprovalRule(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="approval_rules")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE, related_name="approval_rules")
    module_name = models.CharField(max_length=100)
    action_name = models.CharField(max_length=100)
    minimum_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        null=True,
        blank=True,
    )
    maximum_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        null=True,
        blank=True,
    )
    required_role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="required_approval_rules")
    escalation_role = models.ForeignKey(
        Role,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="escalation_approval_rules",
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["organization__display_name", "module_name", "action_name"]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["branch", "is_active"]),
            models.Index(fields=["module_name", "action_name"]),
        ]

    def __str__(self) -> str:
        scope = self.branch.name if self.branch_id else "Organization"
        return f"{self.organization.display_name}: {self.module_name}.{self.action_name} ({scope})"
