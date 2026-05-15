from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from academic.models import AcademicPeriod, AcademicYear
from classes.models import ClassEnrollment, ClassRoom
from common.models import BaseModel
from common.money import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS, ZERO_MONEY
from organizations.models import Branch, Organization
from students.models import Student


def amount_field(*, default=ZERO_MONEY, null=False, blank=False):
    return models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=default,
        null=null,
        blank=blank,
        validators=[MinValueValidator(0)],
    )


class FeeType(models.TextChoices):
    TUITION = "tuition", "Tuition"
    ADMISSION = "admission", "Admission"
    EXAM = "exam", "Exam"
    MATERIAL = "material", "Material"
    FINE = "fine", "Fine"
    OTHER = "other", "Other"


class BillStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    APPROVED = "approved", "Approved"
    UNPAID = "unpaid", "Unpaid"
    PARTIAL = "partial", "Partial"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"
    WRITTEN_OFF = "written_off", "Written Off"


class FeePlan(BaseModel):
    class PlanType(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        PACKAGE = "package", "Package"
        ONE_TIME = "one_time", "One Time"
        CUSTOM = "custom", "Custom"

    class BillingFrequency(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        ONE_TIME = "one_time", "One Time"
        MANUAL = "manual", "Manual"

    class PaymentDueRule(models.TextChoices):
        FIXED_BS_DAY = "fixed_bs_day", "Fixed BS Day"
        END_OF_BS_MONTH = "end_of_bs_month", "End Of BS Month"
        MANUAL = "manual", "Manual"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="fee_plans")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="fee_plans")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="fee_plans")
    class_room = models.ForeignKey(
        ClassRoom,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="fee_plans",
    )
    name = models.CharField(max_length=255)
    fee_plan_type = models.CharField(max_length=20, choices=PlanType.choices, default=PlanType.MONTHLY)
    billing_frequency = models.CharField(max_length=20, choices=BillingFrequency.choices, default=BillingFrequency.MONTHLY)
    payment_due_rule = models.CharField(max_length=30, choices=PaymentDueRule.choices, default=PaymentDueRule.FIXED_BS_DAY)
    due_day = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(32)])
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["academic_year", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "academic_year", "class_room", "name"],
                name="unique_fee_plan_name_per_scope",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["branch", "is_active"]),
            models.Index(fields=["academic_year", "is_active"]),
            models.Index(fields=["class_room", "is_active"]),
            models.Index(fields=["fee_plan_type", "billing_frequency"]),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year)
        if self.class_room_id:
            validate_class_room_scope(self.class_room, self.organization_id, self.branch, self.academic_year)


class FeePlanItem(BaseModel):
    fee_plan = models.ForeignKey(FeePlan, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=255)
    fee_type = models.CharField(max_length=20, choices=FeeType.choices, default=FeeType.TUITION)
    amount = amount_field()
    is_recurring = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["fee_plan", "sort_order", "item_name"]
        indexes = [
            models.Index(fields=["fee_plan", "fee_type"]),
            models.Index(fields=["sort_order"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gte=0), name="fee_plan_item_amount_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.fee_plan.name} - {self.item_name}"


class StudentFeeDue(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="student_fee_dues")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="student_fee_dues")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="student_fee_dues")
    academic_period = models.ForeignKey(
        AcademicPeriod,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="student_fee_dues",
    )
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="fee_dues")
    class_room = models.ForeignKey(ClassRoom, null=True, blank=True, on_delete=models.PROTECT, related_name="fee_dues")
    class_enrollment = models.ForeignKey(
        ClassEnrollment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="fee_dues",
    )
    fee_plan = models.ForeignKey(FeePlan, null=True, blank=True, on_delete=models.PROTECT, related_name="fee_dues")
    period_label = models.CharField(max_length=100)
    due_date_ad = models.DateField(null=True, blank=True, db_index=True)
    due_date_bs = models.CharField(max_length=10, blank=True)
    original_amount = amount_field()
    discount_amount = amount_field()
    fine_amount = amount_field()
    net_amount = amount_field()
    paid_amount = amount_field()
    balance_amount = amount_field()
    status = models.CharField(max_length=20, choices=BillStatus.choices, default=BillStatus.DRAFT, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_student_fee_dues",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cancelled_student_fee_dues",
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "due_date_ad", "period_label"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["academic_period", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["class_enrollment", "status"]),
            models.Index(fields=["due_date_ad"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(original_amount__gte=0), name="fee_due_original_non_negative"),
            models.CheckConstraint(condition=models.Q(discount_amount__gte=0), name="fee_due_discount_non_negative"),
            models.CheckConstraint(condition=models.Q(fine_amount__gte=0), name="fee_due_fine_non_negative"),
            models.CheckConstraint(condition=models.Q(net_amount__gte=0), name="fee_due_net_non_negative"),
            models.CheckConstraint(condition=models.Q(paid_amount__gte=0), name="fee_due_paid_non_negative"),
            models.CheckConstraint(condition=models.Q(balance_amount__gte=0), name="fee_due_balance_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} - {self.period_label}"

    def calculated_net_amount(self):
        return self.original_amount - self.discount_amount + self.fine_amount

    def calculated_balance_amount(self):
        return self.net_amount - self.paid_amount

    def clean(self) -> None:
        super().clean()
        validate_billing_scope(self.student, self.organization_id, self.branch, self.academic_year, self.academic_period)
        if self.class_room_id:
            validate_class_room_scope(self.class_room, self.organization_id, self.branch, self.academic_year)
        if self.class_enrollment_id:
            validate_enrollment_scope(self.class_enrollment, self.student, self.organization_id, self.branch, self.academic_year)
        if self.fee_plan_id:
            validate_fee_plan_scope(self.fee_plan, self.organization_id, self.branch, self.academic_year)


class StudentInvoice(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="student_invoices")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="student_invoices")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="student_invoices")
    academic_period = models.ForeignKey(
        AcademicPeriod,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="student_invoices",
    )
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="invoices")
    invoice_number = models.CharField(max_length=100)
    invoice_date_ad = models.DateField(db_index=True)
    invoice_date_bs = models.CharField(max_length=10, blank=True)
    due_date_ad = models.DateField(null=True, blank=True, db_index=True)
    due_date_bs = models.CharField(max_length=10, blank=True)
    subtotal = amount_field()
    discount_amount = amount_field()
    fine_amount = amount_field()
    total_amount = amount_field()
    paid_amount = amount_field()
    balance_amount = amount_field()
    status = models.CharField(max_length=20, choices=BillStatus.choices, default=BillStatus.DRAFT, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-invoice_date_ad", "invoice_number"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["academic_period", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["due_date_ad"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["organization", "invoice_number"], name="unique_invoice_number_per_org"),
            models.CheckConstraint(condition=models.Q(subtotal__gte=0), name="invoice_subtotal_non_negative"),
            models.CheckConstraint(condition=models.Q(discount_amount__gte=0), name="invoice_discount_non_negative"),
            models.CheckConstraint(condition=models.Q(fine_amount__gte=0), name="invoice_fine_non_negative"),
            models.CheckConstraint(condition=models.Q(total_amount__gte=0), name="invoice_total_non_negative"),
            models.CheckConstraint(condition=models.Q(paid_amount__gte=0), name="invoice_paid_non_negative"),
            models.CheckConstraint(condition=models.Q(balance_amount__gte=0), name="invoice_balance_non_negative"),
        ]

    def __str__(self) -> str:
        return self.invoice_number

    def calculated_total_amount(self):
        return self.subtotal - self.discount_amount + self.fine_amount

    def calculated_balance_amount(self):
        return self.total_amount - self.paid_amount

    def clean(self) -> None:
        super().clean()
        validate_billing_scope(self.student, self.organization_id, self.branch, self.academic_year, self.academic_period)


class StudentInvoiceItem(BaseModel):
    invoice = models.ForeignKey(StudentInvoice, on_delete=models.CASCADE, related_name="items")
    fee_due = models.ForeignKey(StudentFeeDue, null=True, blank=True, on_delete=models.PROTECT, related_name="invoice_items")
    description = models.CharField(max_length=255)
    fee_type = models.CharField(max_length=20, choices=FeeType.choices, default=FeeType.TUITION)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, validators=[MinValueValidator(0)])
    unit_amount = amount_field()
    discount_amount = amount_field()
    fine_amount = amount_field()
    line_total = amount_field()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["invoice", "created_at"]
        indexes = [
            models.Index(fields=["invoice", "fee_type"]),
            models.Index(fields=["fee_due"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=0), name="invoice_item_quantity_non_negative"),
            models.CheckConstraint(condition=models.Q(unit_amount__gte=0), name="invoice_item_unit_non_negative"),
            models.CheckConstraint(condition=models.Q(discount_amount__gte=0), name="invoice_item_discount_non_negative"),
            models.CheckConstraint(condition=models.Q(fine_amount__gte=0), name="invoice_item_fine_non_negative"),
            models.CheckConstraint(condition=models.Q(line_total__gte=0), name="invoice_item_total_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.invoice.invoice_number} - {self.description}"

    def calculated_line_total(self):
        return (self.quantity * self.unit_amount) - self.discount_amount + self.fine_amount


class StudentPayment(BaseModel):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK = "bank", "Bank"
        ONLINE = "online", "Online"
        CHEQUE = "cheque", "Cheque"
        WALLET = "wallet", "Wallet"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        POSTED = "posted", "Posted"
        VOIDED = "voided", "Voided"
        REFUNDED = "refunded", "Refunded"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="student_payments")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="student_payments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="student_payments")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="payments")
    receipt_number = models.CharField(max_length=100, null=True, blank=True)
    draft_receipt_number = models.CharField(max_length=100, null=True, blank=True)
    payment_date_ad = models.DateField(db_index=True)
    payment_date_bs = models.CharField(max_length=10, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, db_index=True)
    amount = amount_field()
    discount_amount = amount_field()
    fine_amount = amount_field()
    net_received_amount = amount_field()
    reference_number = models.CharField(max_length=150, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    is_advance_payment = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_student_payments",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_student_payments",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="voided_student_payments",
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    void_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-payment_date_ad", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["payment_method", "status"]),
            models.Index(fields=["receipt_number"]),
            models.Index(fields=["draft_receipt_number"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "receipt_number"],
                condition=models.Q(receipt_number__isnull=False),
                name="unique_receipt_number_per_org_when_set",
            ),
            models.UniqueConstraint(
                fields=["organization", "draft_receipt_number"],
                condition=models.Q(draft_receipt_number__isnull=False),
                name="unique_draft_receipt_number_per_org_when_set",
            ),
            models.CheckConstraint(condition=models.Q(amount__gte=0), name="payment_amount_non_negative"),
            models.CheckConstraint(condition=models.Q(discount_amount__gte=0), name="payment_discount_non_negative"),
            models.CheckConstraint(condition=models.Q(fine_amount__gte=0), name="payment_fine_non_negative"),
            models.CheckConstraint(condition=models.Q(net_received_amount__gte=0), name="payment_net_received_non_negative"),
        ]

    def __str__(self) -> str:
        return self.receipt_number or self.draft_receipt_number or f"Payment {self.id}"

    def clean(self) -> None:
        super().clean()
        validate_billing_scope(self.student, self.organization_id, self.branch, self.academic_year)


class StudentPaymentAllocation(BaseModel):
    payment = models.ForeignKey(StudentPayment, on_delete=models.CASCADE, related_name="allocations")
    fee_due = models.ForeignKey(StudentFeeDue, null=True, blank=True, on_delete=models.PROTECT, related_name="payment_allocations")
    invoice = models.ForeignKey(StudentInvoice, null=True, blank=True, on_delete=models.PROTECT, related_name="payment_allocations")
    invoice_item = models.ForeignKey(
        StudentInvoiceItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="payment_allocations",
    )
    amount_allocated = amount_field()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["payment", "created_at"]
        indexes = [
            models.Index(fields=["payment"]),
            models.Index(fields=["fee_due"]),
            models.Index(fields=["invoice"]),
            models.Index(fields=["invoice_item"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount_allocated__gte=0), name="payment_allocation_amount_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.payment} allocation {self.amount_allocated}"


class StudentAdvanceBalance(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="student_advance_balances")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="student_advance_balances")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="student_advance_balances")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="advance_balances")
    opening_amount = amount_field()
    received_amount = amount_field()
    applied_amount = amount_field()
    refunded_amount = amount_field()
    balance_amount = amount_field()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "academic_year"]
        indexes = [
            models.Index(fields=["organization", "academic_year"]),
            models.Index(fields=["branch", "academic_year"]),
            models.Index(fields=["student", "academic_year"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(opening_amount__gte=0), name="advance_opening_non_negative"),
            models.CheckConstraint(condition=models.Q(received_amount__gte=0), name="advance_received_non_negative"),
            models.CheckConstraint(condition=models.Q(applied_amount__gte=0), name="advance_applied_non_negative"),
            models.CheckConstraint(condition=models.Q(refunded_amount__gte=0), name="advance_refunded_non_negative"),
            models.CheckConstraint(condition=models.Q(balance_amount__gte=0), name="advance_balance_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} advance balance"

    def calculated_balance_amount(self):
        return self.opening_amount + self.received_amount - self.applied_amount - self.refunded_amount

    def clean(self) -> None:
        super().clean()
        validate_billing_scope(self.student, self.organization_id, self.branch, self.academic_year)


class BillingDiscount(BaseModel):
    class DiscountType(models.TextChoices):
        SCHOLARSHIP = "scholarship", "Scholarship"
        SIBLING = "sibling", "Sibling"
        MERIT = "merit", "Merit"
        HARDSHIP = "hardship", "Hardship"
        ONE_TIME = "one_time", "One Time"
        BULK = "bulk", "Bulk"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="billing_discounts")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="billing_discounts")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="billing_discounts")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="billing_discounts")
    class_enrollment = models.ForeignKey(
        ClassEnrollment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="billing_discounts",
    )
    fee_due = models.ForeignKey(StudentFeeDue, null=True, blank=True, on_delete=models.PROTECT, related_name="billing_discounts")
    invoice = models.ForeignKey(StudentInvoice, null=True, blank=True, on_delete=models.PROTECT, related_name="billing_discounts")
    discount_type = models.CharField(max_length=30, choices=DiscountType.choices)
    discount_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    discount_amount = amount_field(null=True, blank=True, default=None)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_billing_discounts",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["discount_type", "status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(discount_amount__isnull=True) | models.Q(discount_amount__gte=0),
                name="billing_discount_amount_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} - {self.get_discount_type_display()}"


class BillingWaiver(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="billing_waivers")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="billing_waivers")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="billing_waivers")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="billing_waivers")
    fee_due = models.ForeignKey(StudentFeeDue, null=True, blank=True, on_delete=models.PROTECT, related_name="billing_waivers")
    invoice = models.ForeignKey(StudentInvoice, null=True, blank=True, on_delete=models.PROTECT, related_name="billing_waivers")
    waiver_amount = amount_field()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_billing_waivers",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["student", "status"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(waiver_amount__gte=0), name="waiver_amount_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} waiver {self.waiver_amount}"


class BillingFine(BaseModel):
    class FineType(models.TextChoices):
        LATE_FEE = "late_fee", "Late Fee"
        PENALTY = "penalty", "Penalty"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        WAIVED = "waived", "Waived"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="billing_fines")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="billing_fines")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="billing_fines")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="billing_fines")
    fee_due = models.ForeignKey(StudentFeeDue, null=True, blank=True, on_delete=models.PROTECT, related_name="billing_fines")
    invoice = models.ForeignKey(StudentInvoice, null=True, blank=True, on_delete=models.PROTECT, related_name="billing_fines")
    fine_type = models.CharField(max_length=20, choices=FineType.choices, default=FineType.LATE_FEE)
    amount = amount_field()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_billing_fines",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["fine_type", "status"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gte=0), name="fine_amount_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} fine {self.amount}"


class StudentRefund(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="student_refunds")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="student_refunds")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="student_refunds")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="refunds")
    original_payment = models.ForeignKey(
        StudentPayment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    refund_voucher_number = models.CharField(max_length=100, null=True, blank=True)
    refund_date_ad = models.DateField(null=True, blank=True, db_index=True)
    refund_date_bs = models.CharField(max_length=10, blank=True)
    refund_amount = amount_field()
    refund_reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_student_refunds",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_student_refunds",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="paid_student_refunds",
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["refund_voucher_number"]),
            models.Index(fields=["refund_date_ad"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "refund_voucher_number"],
                condition=models.Q(refund_voucher_number__isnull=False),
                name="unique_refund_voucher_per_org_when_set",
            ),
            models.CheckConstraint(condition=models.Q(refund_amount__gte=0), name="refund_amount_non_negative"),
        ]

    def __str__(self) -> str:
        return self.refund_voucher_number or f"{self.student.admission_number} refund"

    def clean(self) -> None:
        super().clean()
        validate_billing_scope(self.student, self.organization_id, self.branch, self.academic_year)
        if self.original_payment_id and self.original_payment.student_id != self.student_id:
            raise ValidationError({"original_payment": "Refund payment must belong to the same student."})


def validate_scope(organization_id, branch: Branch | None, academic_year: AcademicYear | None = None) -> None:
    if branch and organization_id != branch.organization_id:
        raise ValidationError({"branch": "Branch must belong to the same organization."})
    if academic_year and organization_id != academic_year.organization_id:
        raise ValidationError({"academic_year": "Academic year must belong to the same organization."})


def validate_billing_scope(
    student: Student,
    organization_id,
    branch: Branch | None,
    academic_year: AcademicYear,
    academic_period: AcademicPeriod | None = None,
) -> None:
    if student.organization_id != organization_id:
        raise ValidationError({"student": "Student must belong to the same organization."})
    if branch and student.branch_id != branch.id:
        raise ValidationError({"student": "Student must belong to the same branch."})
    if student.academic_year_id != academic_year.id:
        raise ValidationError({"academic_year": "Academic year must match the student academic year."})
    if academic_period and academic_period.academic_year_id != academic_year.id:
        raise ValidationError({"academic_period": "Academic period must belong to the same academic year."})


def validate_class_room_scope(class_room: ClassRoom, organization_id, branch: Branch | None, academic_year: AcademicYear) -> None:
    if class_room.organization_id != organization_id:
        raise ValidationError({"class_room": "Class must belong to the same organization."})
    if branch and class_room.branch_id != branch.id:
        raise ValidationError({"class_room": "Class must belong to the same branch."})
    if class_room.academic_year_id != academic_year.id:
        raise ValidationError({"class_room": "Class must belong to the same academic year."})


def validate_enrollment_scope(
    enrollment: ClassEnrollment,
    student: Student,
    organization_id,
    branch: Branch | None,
    academic_year: AcademicYear,
) -> None:
    if enrollment.student_id != student.id:
        raise ValidationError({"class_enrollment": "Enrollment must belong to the same student."})
    validate_class_room_scope(enrollment.class_room, organization_id, branch, academic_year)


def validate_fee_plan_scope(fee_plan: FeePlan, organization_id, branch: Branch | None, academic_year: AcademicYear) -> None:
    if fee_plan.organization_id != organization_id:
        raise ValidationError({"fee_plan": "Fee plan must belong to the same organization."})
    if branch and fee_plan.branch_id != branch.id:
        raise ValidationError({"fee_plan": "Fee plan must belong to the same branch."})
    if fee_plan.academic_year_id != academic_year.id:
        raise ValidationError({"fee_plan": "Fee plan must belong to the same academic year."})
