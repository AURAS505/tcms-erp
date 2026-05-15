from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from academic.models import AcademicYear
from organizations.models import Branch, Organization
from students.models import (
    Student,
    StudentAcademicRecord,
    StudentDocument,
    StudentInquiry,
    StudentNote,
    StudentSchoolHistory,
    StudentStatusHistory,
)


@pytest.fixture
def organization():
    return Organization.objects.create(legal_name="Auras Education Pvt. Ltd.", display_name="Auras Education")


@pytest.fixture
def branch(organization):
    return Branch.objects.create(organization=organization, code="MAIN", name="Main Branch", is_main_branch=True)


@pytest.fixture
def academic_year(organization):
    return AcademicYear.objects.create(
        organization=organization,
        name="2081/2082",
        bs_start_year=2081,
        bs_end_year=2082,
        bs_start_date="2081-01-01",
        bs_end_date="2081-12-30",
        ad_start_date=date(2024, 4, 13),
        ad_end_date=date(2025, 4, 13),
        status=AcademicYear.Status.ACTIVE,
        is_active=True,
    )


@pytest.fixture
def user():
    return get_user_model().objects.create_user(email="staff@example.com", password="secure-password")


@pytest.fixture
def student(organization, branch, academic_year):
    return Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number="ADM-001",
        full_name="Sita Sharma",
        gender=Student.Gender.FEMALE,
        permanent_address="Kathmandu",
        status=Student.Status.PENDING,
    )


@pytest.mark.django_db
def test_create_student_inquiry(organization, branch, academic_year, user):
    inquiry = StudentInquiry.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student_full_name="Ram Sharma",
        guardian_name="Hari Sharma",
        contact_number="9800000000",
        email="guardian@example.com",
        interested_class_subject="Grade 10 Math",
        inquiry_source="phone",
        created_by=user,
    )

    assert str(inquiry) == "Ram Sharma (New)"
    assert inquiry.status == StudentInquiry.Status.NEW
    assert inquiry.branch == branch


@pytest.mark.django_db
def test_create_pending_student(student):
    assert str(student) == "ADM-001 - Sita Sharma"
    assert student.status == Student.Status.PENDING
    assert student.can_be_enrolled is False


@pytest.mark.django_db
def test_create_active_student(organization, branch, academic_year, user):
    student = Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number="ADM-002",
        full_name="Gita Thapa",
        permanent_address="Lalitpur",
        status=Student.Status.ACTIVE,
        admission_date_ad=date(2024, 7, 1),
        admission_date_bs="2081-03-17",
        approved_by=user,
        approved_at=timezone.now(),
    )

    assert student.can_be_enrolled is True
    assert student.approved_by == user


@pytest.mark.django_db
def test_enforce_unique_admission_number_per_organization(student, organization, branch, academic_year):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Student.objects.create(
                organization=organization,
                branch=branch,
                academic_year=academic_year,
                admission_number="ADM-001",
                full_name="Duplicate",
                permanent_address="Kathmandu",
            )


@pytest.mark.django_db
def test_allow_same_admission_number_across_organizations(student):
    other = Organization.objects.create(legal_name="Other Institute Pvt. Ltd.", display_name="Other")
    other_branch = Branch.objects.create(organization=other, code="MAIN", name="Main")
    other_year = AcademicYear.objects.create(
        organization=other,
        name="2081/2082",
        bs_start_year=2081,
        bs_end_year=2082,
        bs_start_date="2081-01-01",
        bs_end_date="2081-12-30",
        ad_start_date=date(2024, 4, 13),
        ad_end_date=date(2025, 4, 13),
        status=AcademicYear.Status.ACTIVE,
        is_active=True,
    )

    other_student = Student.objects.create(
        organization=other,
        branch=other_branch,
        academic_year=other_year,
        admission_number="ADM-001",
        full_name="Same Number",
        permanent_address="Pokhara",
    )

    assert other_student.organization == other


@pytest.mark.django_db
def test_create_student_document(student, user):
    document = StudentDocument.objects.create(
        student=student,
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        document_type=StudentDocument.DocumentType.MARKSHEET,
        file_path="private/students/adm-001/marksheet.pdf",
        file_name="marksheet.pdf",
        uploaded_by=user,
    )

    assert str(document) == "ADM-001 - Marksheet"
    assert document.uploaded_by == user


@pytest.mark.django_db
def test_create_academic_record(student):
    record = StudentAcademicRecord.objects.create(
        student=student,
        institution_name="ABC School",
        board_university="NEB",
        level_grade="Grade 9",
        result_type="GPA",
        gpa_percentage_grade="3.6",
        passed_year_bs=2080,
        passed_year_ad=2024,
    )

    assert str(record) == "ADM-001 - Grade 9"


@pytest.mark.django_db
def test_create_school_history(student):
    history = StudentSchoolHistory.objects.create(
        student=student,
        school_college_name="ABC School",
        level_class_attended="Grade 8",
        start_date_ad=date(2022, 4, 14),
        start_date_bs="2079-01-01",
        end_date_ad=date(2023, 4, 13),
        end_date_bs="2079-12-30",
    )

    assert str(history) == "ADM-001 - ABC School"


@pytest.mark.django_db
def test_create_status_history(student, user):
    history = StudentStatusHistory.objects.create(
        student=student,
        from_status=Student.Status.INQUIRY,
        to_status=Student.Status.PENDING,
        reason="Profile created after inquiry.",
        changed_by=user,
        metadata={"source": "test"},
    )

    assert str(history) == "ADM-001: inquiry -> pending"
    assert history.changed_by == user


@pytest.mark.django_db
def test_create_student_note(student, user):
    note = StudentNote.objects.create(
        student=student,
        category=StudentNote.Category.ACADEMIC,
        title="Admission note",
        note="Bring original documents for verification.",
        created_by=user,
    )

    assert str(note) == "ADM-001 - Admission note"
