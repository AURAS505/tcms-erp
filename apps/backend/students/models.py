from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from academic.models import AcademicYear
from common.models import BaseModel
from organizations.models import Branch, Organization


class StudentInquiry(BaseModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        APPOINTMENT_SCHEDULED = "appointment_scheduled", "Appointment Scheduled"
        CONVERTED = "converted", "Converted"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="student_inquiries")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="student_inquiries")
    academic_year = models.ForeignKey(
        AcademicYear,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="student_inquiries",
    )
    student_full_name = models.CharField(max_length=255)
    guardian_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=50, db_index=True)
    email = models.EmailField(blank=True)
    interested_class_subject = models.CharField(max_length=255, blank=True)
    inquiry_source = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW, db_index=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_student_inquiries",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["student_full_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.student_full_name} ({self.get_status_display()})"

    def clean(self) -> None:
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year)


class Student(BaseModel):
    class Status(models.TextChoices):
        INQUIRY = "inquiry", "Inquiry"
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        ON_BREAK = "on_break", "On Break"
        LEFT = "left", "Left"
        GRADUATED = "graduated", "Graduated"
        REJECTED = "rejected", "Rejected"

    class Gender(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"
        OTHER = "other", "Other"
        NOT_SPECIFIED = "not_specified", "Not Specified"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="students")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="students")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="students")
    admission_number = models.CharField(max_length=50)
    full_name = models.CharField(max_length=255, db_index=True)
    preferred_name = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.NOT_SPECIFIED)
    date_of_birth_ad = models.DateField(null=True, blank=True)
    date_of_birth_bs = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=50, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    permanent_address = models.TextField()
    temporary_address = models.TextField(blank=True)
    school_college_name = models.CharField(max_length=255, blank=True)
    current_grade_class = models.CharField(max_length=100, blank=True)
    photo_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    admission_date_ad = models.DateField(null=True, blank=True)
    admission_date_bs = models.CharField(max_length=10, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_students",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "admission_number"], name="unique_admission_number_per_org"),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["academic_year", "status"]),
            models.Index(fields=["organization", "admission_number"]),
            models.Index(fields=["full_name"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self) -> str:
        return f"{self.admission_number} - {self.full_name}"

    @property
    def can_be_enrolled(self) -> bool:
        return self.status == self.Status.ACTIVE

    def clean(self) -> None:
        super().clean()
        validate_scope(self.organization_id, self.branch, self.academic_year)


class StudentDocument(BaseModel):
    class DocumentType(models.TextChoices):
        PHOTO = "photo", "Photo"
        BIRTH_CERTIFICATE = "birth_certificate", "Birth Certificate"
        MARKSHEET = "marksheet", "Marksheet"
        CITIZENSHIP = "citizenship", "Citizenship"
        TRANSFER_CERTIFICATE = "transfer_certificate", "Transfer Certificate"
        OTHER = "other", "Other"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="student_documents")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="student_documents")
    academic_year = models.ForeignKey(
        AcademicYear,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="student_documents",
    )
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file_path = models.CharField(max_length=500, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_student_documents",
    )

    class Meta:
        ordering = ["student", "document_type", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "document_type"]),
            models.Index(fields=["branch", "document_type"]),
            models.Index(fields=["academic_year", "document_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} - {self.get_document_type_display()}"

    def clean(self) -> None:
        super().clean()
        validate_student_scope(self.student, self.organization_id, self.branch, self.academic_year)


class StudentAcademicRecord(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="academic_records")
    institution_name = models.CharField(max_length=255)
    board_university = models.CharField(max_length=255, blank=True)
    level_grade = models.CharField(max_length=100)
    result_type = models.CharField(max_length=100)
    gpa_percentage_grade = models.CharField(max_length=100, blank=True)
    passed_year_bs = models.PositiveSmallIntegerField(null=True, blank=True)
    passed_year_ad = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "-passed_year_ad", "-passed_year_bs"]

    def __str__(self) -> str:
        return f"{self.student.admission_number} - {self.level_grade}"


class StudentSchoolHistory(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="school_history")
    school_college_name = models.CharField(max_length=255)
    level_class_attended = models.CharField(max_length=100)
    start_date_ad = models.DateField(null=True, blank=True)
    start_date_bs = models.CharField(max_length=10, blank=True)
    end_date_ad = models.DateField(null=True, blank=True)
    end_date_bs = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "-start_date_ad"]

    def __str__(self) -> str:
        return f"{self.student.admission_number} - {self.school_college_name}"


class StudentStatusHistory(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=20, choices=Student.Status.choices, blank=True)
    to_status = models.CharField(max_length=20, choices=Student.Status.choices)
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="changed_student_statuses",
    )
    changed_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["student", "-changed_at"]
        indexes = [
            models.Index(fields=["to_status", "changed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number}: {self.from_status or 'none'} -> {self.to_status}"


class StudentNote(BaseModel):
    class Category(models.TextChoices):
        GENERAL = "general", "General"
        ACADEMIC = "academic", "Academic"
        BEHAVIOR = "behavior", "Behavior"
        HEALTH = "health", "Health"
        FINANCE = "finance", "Finance"
        OTHER = "other", "Other"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_notes")
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.GENERAL, db_index=True)
    title = models.CharField(max_length=255)
    note = models.TextField()
    attachment_path = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_student_notes",
    )

    class Meta:
        ordering = ["student", "-created_at"]
        indexes = [
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} - {self.title}"


def validate_scope(organization_id, branch: Branch | None, academic_year: AcademicYear | None = None) -> None:
    if branch and organization_id != branch.organization_id:
        raise ValidationError({"branch": "Branch must belong to the same organization."})
    if academic_year and organization_id != academic_year.organization_id:
        raise ValidationError({"academic_year": "Academic year must belong to the same organization."})


def validate_student_scope(student: Student, organization_id, branch: Branch | None, academic_year: AcademicYear | None = None) -> None:
    if organization_id != student.organization_id:
        raise ValidationError({"organization": "Organization must match the student organization."})
    if branch and branch.id != student.branch_id:
        raise ValidationError({"branch": "Branch must match the student branch."})
    if academic_year and academic_year.organization_id != student.organization_id:
        raise ValidationError({"academic_year": "Academic year must belong to the student organization."})
