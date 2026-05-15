from django.db import models
from django.core.exceptions import ValidationError

from common.models import BaseModel
from organizations.models import Branch, Organization
from students.models import Student, validate_scope


class Family(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="families")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="families")
    family_code = models.CharField(max_length=50)
    primary_contact_name = models.CharField(max_length=255)
    primary_contact_number = models.CharField(max_length=50, db_index=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["family_code"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "family_code"], name="unique_family_code_per_org"),
        ]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["branch", "is_active"]),
            models.Index(fields=["family_code"]),
        ]

    def __str__(self) -> str:
        return f"{self.family_code} - {self.primary_contact_name}"

    def clean(self) -> None:
        super().clean()
        validate_scope(self.organization_id, self.branch)


class Guardian(BaseModel):
    class RelationshipType(models.TextChoices):
        FATHER = "father", "Father"
        MOTHER = "mother", "Mother"
        LOCAL_GUARDIAN = "local_guardian", "Local Guardian"
        GRANDPARENT = "grandparent", "Grandparent"
        SIBLING = "sibling", "Sibling"
        OTHER = "other", "Other"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="guardians")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="guardians")
    family = models.ForeignKey(Family, null=True, blank=True, on_delete=models.SET_NULL, related_name="guardians")
    full_name = models.CharField(max_length=255, db_index=True)
    relationship_type = models.CharField(max_length=30, choices=RelationshipType.choices)
    phone = models.CharField(max_length=50, db_index=True)
    alternate_phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)
    is_primary_contact = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["branch", "is_active"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["full_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.get_relationship_type_display()})"

    def clean(self) -> None:
        super().clean()
        validate_scope(self.organization_id, self.branch)
        if self.family_id and self.family.organization_id != self.organization_id:
            raise ValidationError({"family": "Family must belong to the same organization."})


class StudentGuardian(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="guardian_links")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name="student_links")
    relationship_type = models.CharField(max_length=30, choices=Guardian.RelationshipType.choices)
    is_primary = models.BooleanField(default=False)
    can_receive_notifications = models.BooleanField(default=True)
    can_make_payments = models.BooleanField(default=True)
    can_request_refunds = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "-is_primary", "guardian__full_name"]
        constraints = [
            models.UniqueConstraint(fields=["student", "guardian"], name="unique_student_guardian_link"),
        ]
        indexes = [
            models.Index(fields=["student", "is_primary"]),
            models.Index(fields=["guardian"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.admission_number} - {self.guardian.full_name}"

    def clean(self) -> None:
        super().clean()
        if self.student_id and self.guardian_id:
            if self.student.organization_id != self.guardian.organization_id:
                raise ValidationError({"guardian": "Guardian must belong to the same organization as the student."})
            if self.student.branch_id != self.guardian.branch_id:
                raise ValidationError({"guardian": "Guardian must belong to the same branch as the student."})
