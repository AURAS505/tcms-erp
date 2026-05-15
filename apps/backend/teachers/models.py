from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from academic.models import AcademicYear
from common.models import BaseModel
from common.money import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS
from organizations.models import Branch, Organization


class Teacher(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        ON_LEAVE = "on_leave", "On Leave"
        RESIGNED = "resigned", "Resigned"
        TERMINATED = "terminated", "Terminated"

    class Gender(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"
        OTHER = "other", "Other"
        NOT_SPECIFIED = "not_specified", "Not Specified"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="teachers")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="teachers")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="teacher_profiles",
    )
    employee_number = models.CharField(max_length=50)
    full_name = models.CharField(max_length=255, db_index=True)
    preferred_name = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.NOT_SPECIFIED)
    date_of_birth_ad = models.DateField(null=True, blank=True)
    date_of_birth_bs = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=50, db_index=True)
    alternate_phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    qualification = models.CharField(max_length=255, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    experience_summary = models.TextField(blank=True)
    joining_date_ad = models.DateField(null=True, blank=True)
    joining_date_bs = models.CharField(max_length=10, blank=True)
    photo_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "employee_number"], name="unique_teacher_employee_number_per_org"),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["organization", "employee_number"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["full_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.employee_number} - {self.full_name}"

    def clean(self) -> None:
        super().clean()
        validate_teacher_scope(self.organization_id, self.branch)


class TeacherContract(BaseModel):
    class ContractType(models.TextChoices):
        MONTHLY_CUT_PERCENTAGE = "monthly_cut_percentage", "Monthly Cut Percentage"
        PACKAGE_COURSE = "package_course", "Package Course"
        FIXED_MONTHLY_SALARY = "fixed_monthly_salary", "Fixed Monthly Salary"

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="contracts")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="teacher_contracts")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="teacher_contracts")
    academic_year = models.ForeignKey(
        AcademicYear,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="teacher_contracts",
    )
    contract_type = models.CharField(max_length=40, choices=ContractType.choices)
    default_teacher_cut_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    package_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    fixed_monthly_salary = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    effective_from_ad = models.DateField()
    effective_from_bs = models.CharField(max_length=10, blank=True)
    effective_to_ad = models.DateField(null=True, blank=True)
    effective_to_bs = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["teacher", "-effective_from_ad"]
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "academic_year"],
                condition=models.Q(is_active=True),
                name="unique_active_teacher_contract_per_year",
            ),
            models.CheckConstraint(
                condition=models.Q(effective_to_ad__isnull=True) | models.Q(effective_from_ad__lte=models.F("effective_to_ad")),
                name="teacher_contract_effective_from_before_to",
            ),
        ]
        indexes = [
            models.Index(fields=["teacher", "is_active"]),
            models.Index(fields=["academic_year", "is_active"]),
            models.Index(fields=["contract_type"]),
            models.Index(fields=["organization", "branch"]),
        ]

    def __str__(self) -> str:
        return f"{self.teacher.employee_number} - {self.get_contract_type_display()}"

    def clean(self) -> None:
        super().clean()
        validate_teacher_related_scope(self.teacher, self.organization_id, self.branch, self.academic_year)


class TeacherActivity(BaseModel):
    class ActivityType(models.TextChoices):
        NOTE = "note", "Note"
        MEETING = "meeting", "Meeting"
        FOLLOW_UP = "follow_up", "Follow Up"
        PERFORMANCE = "performance", "Performance"
        DOCUMENT = "document", "Document"
        PAYMENT_RELATED = "payment_related", "Payment Related"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="activities")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="teacher_activities")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="teacher_activities")
    academic_year = models.ForeignKey(
        AcademicYear,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="teacher_activities",
    )
    activity_type = models.CharField(max_length=30, choices=ActivityType.choices, default=ActivityType.NOTE, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    activity_date_ad = models.DateField(null=True, blank=True)
    activity_date_bs = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_teacher_activities",
    )

    class Meta:
        ordering = ["teacher", "-created_at"]
        indexes = [
            models.Index(fields=["teacher", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["activity_type"]),
            models.Index(fields=["organization", "branch"]),
        ]

    def __str__(self) -> str:
        return f"{self.teacher.employee_number} - {self.title}"

    def clean(self) -> None:
        super().clean()
        validate_teacher_related_scope(self.teacher, self.organization_id, self.branch, self.academic_year)


class TeacherStatusHistory(BaseModel):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=20, choices=Teacher.Status.choices, blank=True)
    to_status = models.CharField(max_length=20, choices=Teacher.Status.choices)
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="changed_teacher_statuses",
    )
    changed_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["teacher", "-changed_at"]
        indexes = [
            models.Index(fields=["to_status", "changed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.teacher.employee_number}: {self.from_status or 'none'} -> {self.to_status}"


def validate_teacher_scope(organization_id, branch: Branch | None) -> None:
    if branch and organization_id != branch.organization_id:
        raise ValidationError({"branch": "Branch must belong to the same organization."})


def validate_teacher_related_scope(
    teacher: Teacher,
    organization_id,
    branch: Branch | None,
    academic_year: AcademicYear | None = None,
) -> None:
    if organization_id != teacher.organization_id:
        raise ValidationError({"organization": "Organization must match the teacher organization."})
    if branch and branch.id != teacher.branch_id:
        raise ValidationError({"branch": "Branch must match the teacher branch."})
    if academic_year and academic_year.organization_id != teacher.organization_id:
        raise ValidationError({"academic_year": "Academic year must belong to the teacher organization."})
