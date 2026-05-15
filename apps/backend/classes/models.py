from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from academic.models import AcademicYear
from common.models import BaseModel
from common.money import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS
from organizations.models import Branch, Organization
from students.models import Student
from teachers.models import Teacher


class Subject(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="subjects")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.PROTECT, related_name="subjects")
    academic_year = models.ForeignKey(
        AcademicYear,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="subjects",
    )
    subject_code = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["subject_name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "subject_code"], name="unique_subject_code_per_org"),
        ]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["branch", "is_active"]),
            models.Index(fields=["academic_year", "is_active"]),
            models.Index(fields=["subject_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.subject_code} - {self.subject_name}"

    def clean(self) -> None:
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year)


class ClassRoom(BaseModel):
    class TeacherPaymentType(models.TextChoices):
        MONTHLY_CUT_PERCENTAGE = "monthly_cut_percentage", "Monthly Cut Percentage"
        PACKAGE_COURSE = "package_course", "Package Course"
        FIXED_MONTHLY_SALARY = "fixed_monthly_salary", "Fixed Monthly Salary"

    class PaymentDueRule(models.TextChoices):
        FIXED_BS_DAY = "fixed_bs_day", "Fixed BS Day"
        END_OF_BS_MONTH = "end_of_bs_month", "End Of BS Month"
        MANUAL = "manual", "Manual"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="class_rooms")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="class_rooms")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="class_rooms")
    class_name = models.CharField(max_length=150)
    batch_name = models.CharField(max_length=100)
    section_name = models.CharField(max_length=100, blank=True, default="")
    primary_teacher = models.ForeignKey(
        Teacher,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_class_rooms",
    )
    subjects = models.ManyToManyField(Subject, blank=True, related_name="class_rooms")
    start_date_ad = models.DateField(null=True, blank=True)
    start_date_bs = models.CharField(max_length=10, blank=True)
    expected_end_date_ad = models.DateField(null=True, blank=True)
    expected_end_date_bs = models.CharField(max_length=10, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    monthly_fee = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    teacher_cut_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    teacher_payment_type = models.CharField(
        max_length=40,
        choices=TeacherPaymentType.choices,
        default=TeacherPaymentType.MONTHLY_CUT_PERCENTAGE,
    )
    payment_due_rule = models.CharField(max_length=30, choices=PaymentDueRule.choices, default=PaymentDueRule.FIXED_BS_DAY)
    due_day = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(32)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["academic_year", "class_name", "batch_name", "section_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "academic_year", "class_name", "batch_name", "section_name"],
                name="unique_class_batch_section_per_scope",
            ),
            models.CheckConstraint(
                condition=models.Q(expected_end_date_ad__isnull=True)
                | models.Q(start_date_ad__isnull=True)
                | models.Q(start_date_ad__lte=models.F("expected_end_date_ad")),
                name="class_room_start_before_expected_end",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["primary_teacher", "status"]),
            models.Index(fields=["class_name", "batch_name", "section_name"]),
        ]

    def __str__(self) -> str:
        section = f" - {self.section_name}" if self.section_name else ""
        return f"{self.class_name} - {self.batch_name}{section}"

    def clean(self) -> None:
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year)
        if self.primary_teacher_id:
            validate_teacher_scope(self.primary_teacher, self.organization_id, self.branch)


class ClassSchedule(BaseModel):
    class DayOfWeek(models.TextChoices):
        SUNDAY = "sunday", "Sunday"
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"

    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.CharField(max_length=20, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["class_room", "day_of_week", "start_time"]
        constraints = [
            models.CheckConstraint(condition=models.Q(start_time__lt=models.F("end_time")), name="class_schedule_start_before_end"),
        ]
        indexes = [
            models.Index(fields=["class_room", "is_active"]),
            models.Index(fields=["day_of_week", "start_time"]),
        ]

    def __str__(self) -> str:
        return f"{self.class_room} - {self.get_day_of_week_display()} {self.start_time}"


class ClassEnrollment(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_BREAK = "on_break", "On Break"
        COMPLETED = "completed", "Completed"
        LEFT = "left", "Left"
        CANCELLED = "cancelled", "Cancelled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="class_enrollments")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="class_enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="class_enrollments")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="class_enrollments")
    class_room = models.ForeignKey(ClassRoom, on_delete=models.PROTECT, related_name="enrollments")
    joined_date_ad = models.DateField()
    joined_date_bs = models.CharField(max_length=10, blank=True)
    end_date_ad = models.DateField(null=True, blank=True)
    end_date_bs = models.CharField(max_length=10, blank=True)
    left_date_ad = models.DateField(null=True, blank=True)
    left_date_bs = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    enrollment_discount_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    enrollment_discount_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    teacher_cut_percentage_override = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "class_room", "-joined_date_ad"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "class_room"],
                condition=models.Q(status__in=["active", "on_break"]),
                name="unique_active_student_class_enrollment",
            ),
            models.CheckConstraint(
                condition=models.Q(end_date_ad__isnull=True) | models.Q(joined_date_ad__lte=models.F("end_date_ad")),
                name="class_enrollment_joined_before_end",
            ),
            models.CheckConstraint(
                condition=models.Q(left_date_ad__isnull=True) | models.Q(joined_date_ad__lte=models.F("left_date_ad")),
                name="class_enrollment_joined_before_left",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["class_room", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} -> {self.class_room}"

    def clean(self) -> None:
        super().clean()
        validate_enrollment_scope(self.student, self.class_room, self.organization_id, self.branch, self.academic_year)
        if self.student_id and self.student.status != Student.Status.ACTIVE:
            raise ValidationError({"student": "Only active students can be enrolled."})


class ClassEnrollmentBreak(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    enrollment = models.ForeignKey(ClassEnrollment, on_delete=models.CASCADE, related_name="breaks")
    break_start_date_ad = models.DateField()
    break_start_date_bs = models.CharField(max_length=10, blank=True)
    expected_return_date_ad = models.DateField(null=True, blank=True)
    expected_return_date_bs = models.CharField(max_length=10, blank=True)
    actual_return_date_ad = models.DateField(null=True, blank=True)
    actual_return_date_bs = models.CharField(max_length=10, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_enrollment_breaks",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["enrollment", "-break_start_date_ad"]
        indexes = [
            models.Index(fields=["enrollment", "status"]),
            models.Index(fields=["break_start_date_ad"]),
        ]

    def __str__(self) -> str:
        return f"{self.enrollment} break from {self.break_start_date_ad}"


class ClassEnrollmentDiscount(BaseModel):
    class DiscountType(models.TextChoices):
        SCHOLARSHIP = "scholarship", "Scholarship"
        SIBLING = "sibling", "Sibling"
        MERIT = "merit", "Merit"
        HARDSHIP = "hardship", "Hardship"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    enrollment = models.ForeignKey(ClassEnrollment, on_delete=models.CASCADE, related_name="discounts")
    discount_type = models.CharField(max_length=30, choices=DiscountType.choices)
    discount_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    discount_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    effective_from_ad = models.DateField(null=True, blank=True)
    effective_from_bs = models.CharField(max_length=10, blank=True)
    effective_to_ad = models.DateField(null=True, blank=True)
    effective_to_bs = models.CharField(max_length=10, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_enrollment_discounts",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["enrollment", "-created_at"]
        indexes = [
            models.Index(fields=["enrollment", "status"]),
            models.Index(fields=["discount_type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.enrollment} - {self.get_discount_type_display()}"


class StudentWithdrawal(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_REVIEW = "pending_review", "Pending Review"
        APPROVED = "approved", "Approved"
        CANCELLED = "cancelled", "Cancelled"

    enrollment = models.ForeignKey(ClassEnrollment, on_delete=models.PROTECT, related_name="withdrawals")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="withdrawals")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="student_withdrawals")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="student_withdrawals")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="student_withdrawals")
    last_attendance_date_ad = models.DateField()
    last_attendance_date_bs = models.CharField(max_length=10, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_student_withdrawals",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_student_withdrawals",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "-last_attendance_date_ad"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} withdrawal from {self.enrollment.class_room}"

    def clean(self) -> None:
        super().clean()
        validate_enrollment_scope(self.student, self.enrollment.class_room, self.organization_id, self.branch, self.academic_year)
        if self.enrollment_id and self.student_id and self.enrollment.student_id != self.student_id:
            raise ValidationError({"student": "Withdrawal student must match the enrollment student."})


class ClassTeacherTransfer(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        CANCELLED = "cancelled", "Cancelled"

    class_room = models.ForeignKey(ClassRoom, on_delete=models.PROTECT, related_name="teacher_transfers")
    from_teacher = models.ForeignKey(
        Teacher,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transfers_from",
    )
    to_teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="transfers_to")
    effective_date_ad = models.DateField()
    effective_date_bs = models.CharField(max_length=10, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_class_teacher_transfers",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["class_room", "-effective_date_ad"]
        indexes = [
            models.Index(fields=["class_room", "status"]),
            models.Index(fields=["from_teacher", "status"]),
            models.Index(fields=["to_teacher", "status"]),
            models.Index(fields=["effective_date_ad"]),
        ]

    def __str__(self) -> str:
        return f"{self.class_room} teacher transfer to {self.to_teacher.employee_number}"

    def clean(self) -> None:
        super().clean()
        if self.class_room_id:
            if self.from_teacher_id:
                validate_teacher_scope(self.from_teacher, self.class_room.organization_id, self.class_room.branch)
            if self.to_teacher_id:
                validate_teacher_scope(self.to_teacher, self.class_room.organization_id, self.class_room.branch)


def validate_scope(organization_id, branch: Branch | None, academic_year: AcademicYear | None = None) -> None:
    if branch and organization_id != branch.organization_id:
        raise ValidationError({"branch": "Branch must belong to the same organization."})
    if academic_year and organization_id != academic_year.organization_id:
        raise ValidationError({"academic_year": "Academic year must belong to the same organization."})


def validate_teacher_scope(teacher: Teacher, organization_id, branch: Branch | None) -> None:
    if teacher.organization_id != organization_id:
        raise ValidationError({"teacher": "Teacher must belong to the same organization."})
    if branch and teacher.branch_id != branch.id:
        raise ValidationError({"teacher": "Teacher must belong to the same branch."})


def validate_class_room_scope(class_room: ClassRoom, organization_id, branch: Branch | None, academic_year: AcademicYear) -> None:
    if class_room.organization_id != organization_id:
        raise ValidationError({"class_room": "Class must belong to the same organization."})
    if branch and class_room.branch_id != branch.id:
        raise ValidationError({"class_room": "Class must belong to the same branch."})
    if class_room.academic_year_id != academic_year.id:
        raise ValidationError({"class_room": "Class must belong to the same academic year."})


def validate_enrollment_scope(
    student: Student,
    class_room: ClassRoom,
    organization_id,
    branch: Branch | None,
    academic_year: AcademicYear,
) -> None:
    if student.organization_id != organization_id:
        raise ValidationError({"student": "Student must belong to the same organization."})
    if branch and student.branch_id != branch.id:
        raise ValidationError({"student": "Student must belong to the same branch."})
    validate_class_room_scope(class_room, organization_id, branch, academic_year)
