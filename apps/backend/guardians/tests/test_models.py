from datetime import date

import pytest
from django.db import IntegrityError, transaction

from academic.models import AcademicYear
from guardians.models import Family, Guardian, StudentGuardian
from organizations.models import Branch, Organization
from students.models import Student


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
def student(organization, branch, academic_year):
    return Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number="ADM-001",
        full_name="Sita Sharma",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )


@pytest.fixture
def family(organization, branch):
    return Family.objects.create(
        organization=organization,
        branch=branch,
        family_code="FAM-001",
        primary_contact_name="Hari Sharma",
        primary_contact_number="9800000000",
        address="Kathmandu",
    )


@pytest.fixture
def guardian(organization, branch, family):
    return Guardian.objects.create(
        organization=organization,
        branch=branch,
        family=family,
        full_name="Hari Sharma",
        relationship_type=Guardian.RelationshipType.FATHER,
        phone="9800000000",
        email="hari@example.com",
        occupation="Business",
        is_primary_contact=True,
    )


@pytest.mark.django_db
def test_create_family(family):
    assert str(family) == "FAM-001 - Hari Sharma"
    assert family.is_active is True


@pytest.mark.django_db
def test_unique_family_code_per_organization(family, organization, branch):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Family.objects.create(
                organization=organization,
                branch=branch,
                family_code="FAM-001",
                primary_contact_name="Duplicate",
                primary_contact_number="9811111111",
            )


@pytest.mark.django_db
def test_create_guardian(guardian):
    assert str(guardian) == "Hari Sharma (Father)"
    assert guardian.is_primary_contact is True
    assert guardian.is_active is True


@pytest.mark.django_db
def test_link_guardian_to_student(student, guardian):
    link = StudentGuardian.objects.create(
        student=student,
        guardian=guardian,
        relationship_type=Guardian.RelationshipType.FATHER,
        is_primary=True,
        can_receive_notifications=True,
        can_make_payments=True,
        can_request_refunds=False,
    )

    assert str(link) == "ADM-001 - Hari Sharma"
    assert link.student == student
    assert link.guardian == guardian


@pytest.mark.django_db
def test_prevent_duplicate_student_guardian_link(student, guardian):
    StudentGuardian.objects.create(
        student=student,
        guardian=guardian,
        relationship_type=Guardian.RelationshipType.FATHER,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            StudentGuardian.objects.create(
                student=student,
                guardian=guardian,
                relationship_type=Guardian.RelationshipType.FATHER,
            )


@pytest.mark.django_db
def test_branch_and_organization_relationships(student, guardian, family):
    link = StudentGuardian.objects.create(
        student=student,
        guardian=guardian,
        relationship_type=Guardian.RelationshipType.FATHER,
    )

    assert guardian.organization == student.organization
    assert guardian.branch == student.branch
    assert guardian.family == family
    assert link.guardian.family.organization == student.organization
