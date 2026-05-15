from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from academic.models import AcademicPeriod, AcademicYear
from billing.models import StudentPayment
from classes.models import ClassEnrollment, ClassRoom
from common.models import BaseModel
from common.money import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS, ZERO_MONEY
from organizations.models import Branch, Organization
from students.models import Student
from teachers.models import Teacher


def amount_field(*, default=ZERO_MONEY, null=False, blank=False):
    return models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=default,
        null=null,
        blank=blank,
        validators=[MinValueValidator(0)],
    )


class TeacherEarning(BaseModel):
    class EarningSource(models.TextChoices):
        STUDENT_PAYMENT = "student_payment", "Student Payment"
        MANUAL_ADJUSTMENT = "manual_adjustment", "Manual Adjustment"
        FIXED_SALARY = "fixed_salary", "Fixed Salary"
        PACKAGE_COURSE = "package_course", "Package Course"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        POSTED = "posted", "Posted"
        PARTIAL = "partial", "Partial"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        REVERSED = "reversed", "Reversed"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="teacher_earnings")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="teacher_earnings")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="teacher_earnings")
    academic_period = models.ForeignKey(
        AcademicPeriod,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="teacher_earnings",
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="earnings")
    student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.PROTECT, related_name="teacher_earnings")
    class_room = models.ForeignKey(ClassRoom, null=True, blank=True, on_delete=models.PROTECT, related_name="teacher_earnings")
    class_enrollment = models.ForeignKey(
        ClassEnrollment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="teacher_earnings",
    )
    student_payment = models.ForeignKey(
        StudentPayment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="teacher_earnings",
    )
    earning_source = models.CharField(max_length=30, choices=EarningSource.choices, default=EarningSource.OTHER, db_index=True)
    earning_date_ad = models.DateField(db_index=True)
    earning_date_bs = models.CharField(max_length=10, blank=True)
    period_label = models.CharField(max_length=100, blank=True)
    gross_amount = amount_field()
    deduction_amount = amount_field()
    net_amount = amount_field()
    paid_amount = amount_field()
    balance_amount = amount_field()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_teacher_earnings",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_teacher_earnings",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["teacher", "-earning_date_ad", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["teacher", "status"]),
            models.Index(fields=["earning_source", "status"]),
            models.Index(fields=["earning_date_ad"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(gross_amount__gte=0), name="teacher_earning_gross_non_negative"),
            models.CheckConstraint(condition=models.Q(deduction_amount__gte=0), name="teacher_earning_deduction_non_negative"),
            models.CheckConstraint(condition=models.Q(net_amount__gte=0), name="teacher_earning_net_non_negative"),
            models.CheckConstraint(condition=models.Q(paid_amount__gte=0), name="teacher_earning_paid_non_negative"),
            models.CheckConstraint(condition=models.Q(balance_amount__gte=0), name="teacher_earning_balance_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.teacher.employee_number} earning {self.net_amount}"

    @property
    def is_immutable(self) -> bool:
        return self.status in {self.Status.POSTED, self.Status.PAID, self.Status.CANCELLED, self.Status.REVERSED}

    def save(self, *args, **kwargs):
        if not self._state.adding:
            existing_status = type(self).objects.only("status").get(pk=self.pk).status
            if existing_status in {self.Status.POSTED, self.Status.PAID, self.Status.CANCELLED, self.Status.REVERSED} and not getattr(
                self, "_allow_immutable_update", False
            ):
                raise ValidationError("Posted/paid/cancelled/reversed teacher earnings are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_immutable:
            raise ValidationError("Posted/paid/cancelled/reversed teacher earnings cannot be deleted.")
        return super().delete(*args, **kwargs)

    def clean(self):
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year, self.academic_period)
        validate_teacher_scope(self.teacher, self.organization_id, self.branch)
        if self.student_id:
            validate_student_scope(self.student, self.organization_id, self.branch, self.academic_year)
        if self.class_room_id:
            validate_class_scope(self.class_room, self.organization_id, self.branch, self.academic_year)
        if self.class_enrollment_id:
            if self.student_id and self.class_enrollment.student_id != self.student_id:
                raise ValidationError({"class_enrollment": "Class enrollment must belong to the selected student."})
            validate_enrollment_scope(self.class_enrollment, self.organization_id, self.branch, self.academic_year)
        if self.student_payment_id:
            validate_payment_scope(self.student_payment, self.organization_id, self.branch, self.academic_year)


class TeacherPaymentBatch(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        POSTED = "posted", "Posted"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="teacher_payment_batches")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="teacher_payment_batches")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="teacher_payment_batches")
    academic_period = models.ForeignKey(
        AcademicPeriod,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="teacher_payment_batches",
    )
    batch_number = models.CharField(max_length=100)
    batch_date_ad = models.DateField(db_index=True)
    batch_date_bs = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)
    total_amount = amount_field()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_teacher_payment_batches",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_teacher_payment_batches",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-batch_date_ad", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "batch_number"], name="unique_teacher_batch_number_per_org"),
            models.CheckConstraint(condition=models.Q(total_amount__gte=0), name="teacher_batch_total_non_negative"),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["batch_number"]),
            models.Index(fields=["batch_date_ad"]),
        ]

    def __str__(self) -> str:
        return self.batch_number

    @property
    def is_immutable(self) -> bool:
        return self.status == self.Status.POSTED

    def save(self, *args, **kwargs):
        if not self._state.adding:
            existing_status = type(self).objects.only("status").get(pk=self.pk).status
            if existing_status == self.Status.POSTED and not getattr(self, "_allow_immutable_update", False):
                raise ValidationError("Posted teacher payment batches are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_immutable:
            raise ValidationError("Posted teacher payment batches cannot be deleted.")
        return super().delete(*args, **kwargs)

    def clean(self):
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year, self.academic_period)


class TeacherPayment(BaseModel):
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

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="teacher_payments")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="teacher_payments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="teacher_payments")
    academic_period = models.ForeignKey(
        AcademicPeriod,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="teacher_payments",
    )
    payment_batch = models.ForeignKey(
        TeacherPaymentBatch,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="payments")
    voucher_number = models.CharField(max_length=100, null=True, blank=True)
    draft_voucher_number = models.CharField(max_length=100, null=True, blank=True)
    payment_date_ad = models.DateField(db_index=True)
    payment_date_bs = models.CharField(max_length=10, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, db_index=True)
    amount = amount_field()
    deduction_amount = amount_field()
    net_paid_amount = amount_field()
    reference_number = models.CharField(max_length=150, blank=True)
    acknowledgement_file_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_teacher_payments",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_teacher_payments",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="voided_teacher_payments",
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    void_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-payment_date_ad", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "voucher_number"],
                condition=models.Q(voucher_number__isnull=False),
                name="unique_teacher_voucher_number_per_org_when_set",
            ),
            models.UniqueConstraint(
                fields=["organization", "draft_voucher_number"],
                condition=models.Q(draft_voucher_number__isnull=False),
                name="unique_teacher_draft_voucher_number_per_org_when_set",
            ),
            models.CheckConstraint(condition=models.Q(amount__gte=0), name="teacher_payment_amount_non_negative"),
            models.CheckConstraint(condition=models.Q(deduction_amount__gte=0), name="teacher_payment_deduction_non_negative"),
            models.CheckConstraint(condition=models.Q(net_paid_amount__gte=0), name="teacher_payment_net_non_negative"),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["teacher", "status"]),
            models.Index(fields=["payment_method", "status"]),
            models.Index(fields=["voucher_number"]),
            models.Index(fields=["draft_voucher_number"]),
            models.Index(fields=["payment_date_ad"]),
        ]

    def __str__(self) -> str:
        return self.voucher_number or self.draft_voucher_number or f"Teacher payment {self.id}"

    @property
    def is_immutable(self) -> bool:
        return self.status in {self.Status.POSTED, self.Status.VOIDED}

    def save(self, *args, **kwargs):
        if not self._state.adding:
            existing_status = type(self).objects.only("status").get(pk=self.pk).status
            if existing_status in {self.Status.POSTED, self.Status.VOIDED} and not getattr(
                self, "_allow_immutable_update", False
            ):
                raise ValidationError("Posted and voided teacher payments are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_immutable:
            raise ValidationError("Posted and voided teacher payments cannot be deleted.")
        return super().delete(*args, **kwargs)

    def clean(self):
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year, self.academic_period)
        validate_teacher_scope(self.teacher, self.organization_id, self.branch)
        if self.payment_batch_id and self.payment_batch.organization_id != self.organization_id:
            raise ValidationError({"payment_batch": "Payment batch must belong to the same organization."})


class TeacherPaymentAllocation(BaseModel):
    teacher_payment = models.ForeignKey(TeacherPayment, on_delete=models.CASCADE, related_name="allocations")
    teacher_earning = models.ForeignKey(TeacherEarning, on_delete=models.PROTECT, related_name="payment_allocations")
    amount_allocated = amount_field(default=Decimal("0.00"))
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["teacher_payment", "created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount_allocated__gt=0), name="teacher_payment_allocation_positive"),
        ]
        indexes = [
            models.Index(fields=["teacher_payment"]),
            models.Index(fields=["teacher_earning"]),
        ]

    def __str__(self) -> str:
        return f"{self.teacher_payment} allocation {self.amount_allocated}"

    def save(self, *args, **kwargs):
        if self.teacher_payment_id and self.teacher_payment.status in {TeacherPayment.Status.POSTED, TeacherPayment.Status.VOIDED} and not getattr(
            self, "_allow_immutable_update", False
        ):
            raise ValidationError("Allocations for posted/voided teacher payments are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.teacher_payment.status in {TeacherPayment.Status.POSTED, TeacherPayment.Status.VOIDED}:
            raise ValidationError("Allocations for posted/voided teacher payments cannot be deleted.")
        return super().delete(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.teacher_payment_id and self.teacher_earning_id:
            if self.teacher_payment.organization_id != self.teacher_earning.organization_id:
                raise ValidationError({"teacher_earning": "Allocation earning must match payment organization."})
            if self.teacher_payment.teacher_id != self.teacher_earning.teacher_id:
                raise ValidationError({"teacher_earning": "Allocation earning must belong to the same teacher."})


class TeacherDeduction(BaseModel):
    class DeductionType(models.TextChoices):
        ADVANCE_RECOVERY = "advance_recovery", "Advance Recovery"
        TAX = "tax", "Tax"
        ABSENCE = "absence", "Absence"
        ADJUSTMENT = "adjustment", "Adjustment"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="teacher_deductions")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="teacher_deductions")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="teacher_deductions")
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="deductions")
    teacher_earning = models.ForeignKey(
        TeacherEarning,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="deductions",
    )
    teacher_payment = models.ForeignKey(
        TeacherPayment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="deductions",
    )
    deduction_type = models.CharField(max_length=30, choices=DeductionType.choices, default=DeductionType.OTHER)
    amount = amount_field()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_teacher_deductions",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["teacher", "-created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gte=0), name="teacher_deduction_amount_non_negative"),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["teacher", "status"]),
            models.Index(fields=["deduction_type", "status"]),
        ]

    def __str__(self):
        return f"{self.teacher.employee_number} deduction {self.amount}"

    @property
    def is_immutable(self) -> bool:
        return self.status == self.Status.APPROVED

    def save(self, *args, **kwargs):
        if not self._state.adding:
            existing_status = type(self).objects.only("status").get(pk=self.pk).status
            if existing_status == self.Status.APPROVED and not getattr(self, "_allow_immutable_update", False):
                raise ValidationError("Approved teacher deductions are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_immutable:
            raise ValidationError("Approved teacher deductions cannot be deleted.")
        return super().delete(*args, **kwargs)

    def clean(self):
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year)
        validate_teacher_scope(self.teacher, self.organization_id, self.branch)
        if self.teacher_earning_id and self.teacher_earning.teacher_id != self.teacher_id:
            raise ValidationError({"teacher_earning": "Teacher earning must belong to the same teacher."})
        if self.teacher_payment_id and self.teacher_payment.teacher_id != self.teacher_id:
            raise ValidationError({"teacher_payment": "Teacher payment must belong to the same teacher."})


def validate_scope(
    organization_id,
    branch: Branch | None,
    academic_year: AcademicYear | None = None,
    academic_period: AcademicPeriod | None = None,
):
    if branch and organization_id != branch.organization_id:
        raise ValidationError({"branch": "Branch must belong to the same organization."})
    if academic_year and organization_id != academic_year.organization_id:
        raise ValidationError({"academic_year": "Academic year must belong to the same organization."})
    if academic_period:
        if organization_id != academic_period.organization_id:
            raise ValidationError({"academic_period": "Academic period must belong to the same organization."})
        if academic_year and academic_period.academic_year_id != academic_year.id:
            raise ValidationError({"academic_period": "Academic period must belong to the selected academic year."})


def validate_teacher_scope(teacher: Teacher, organization_id, branch: Branch | None):
    if teacher.organization_id != organization_id:
        raise ValidationError({"teacher": "Teacher must belong to the same organization."})
    if branch and teacher.branch_id != branch.id:
        raise ValidationError({"teacher": "Teacher must belong to the same branch."})


def validate_student_scope(student: Student, organization_id, branch: Branch | None, academic_year: AcademicYear):
    if student.organization_id != organization_id:
        raise ValidationError({"student": "Student must belong to the same organization."})
    if branch and student.branch_id != branch.id:
        raise ValidationError({"student": "Student must belong to the same branch."})
    if student.academic_year_id != academic_year.id:
        raise ValidationError({"academic_year": "Student academic year must match earning academic year."})


def validate_class_scope(class_room: ClassRoom, organization_id, branch: Branch | None, academic_year: AcademicYear):
    if class_room.organization_id != organization_id:
        raise ValidationError({"class_room": "Class must belong to the same organization."})
    if branch and class_room.branch_id != branch.id:
        raise ValidationError({"class_room": "Class must belong to the same branch."})
    if class_room.academic_year_id != academic_year.id:
        raise ValidationError({"class_room": "Class must belong to the same academic year."})


def validate_enrollment_scope(enrollment: ClassEnrollment, organization_id, branch: Branch | None, academic_year: AcademicYear):
    if enrollment.organization_id != organization_id:
        raise ValidationError({"class_enrollment": "Enrollment must belong to the same organization."})
    if branch and enrollment.branch_id != branch.id:
        raise ValidationError({"class_enrollment": "Enrollment must belong to the same branch."})
    if enrollment.academic_year_id != academic_year.id:
        raise ValidationError({"class_enrollment": "Enrollment must belong to the same academic year."})


def validate_payment_scope(payment: StudentPayment, organization_id, branch: Branch | None, academic_year: AcademicYear):
    if payment.organization_id != organization_id:
        raise ValidationError({"student_payment": "Student payment must belong to the same organization."})
    if branch and payment.branch_id != branch.id:
        raise ValidationError({"student_payment": "Student payment must belong to the same branch."})
    if payment.academic_year_id != academic_year.id:
        raise ValidationError({"student_payment": "Student payment must belong to the same academic year."})
