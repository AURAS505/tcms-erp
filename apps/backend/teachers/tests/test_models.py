from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from academic.models import AcademicYear
from organizations.models import Branch, Organization
from teachers.models import Teacher, TeacherActivity, TeacherContract, TeacherStatusHistory


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
    return get_user_model().objects.create_user(email="teacher@example.com", password="secure-password")


@pytest.fixture
def teacher(organization, branch):
    return Teacher.objects.create(
        organization=organization,
        branch=branch,
        employee_number="TCH-001",
        full_name="Anita Shrestha",
        gender=Teacher.Gender.FEMALE,
        phone="9800000001",
        qualification="MSc Mathematics",
        specialization="Mathematics",
        status=Teacher.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_create_teacher(teacher):
    assert str(teacher) == "TCH-001 - Anita Shrestha"
    assert teacher.status == Teacher.Status.ACTIVE
    assert teacher.branch.name == "Main Branch"


@pytest.mark.django_db
def test_enforce_unique_employee_number_per_organization(teacher, organization, branch):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Teacher.objects.create(
                organization=organization,
                branch=branch,
                employee_number="TCH-001",
                full_name="Duplicate Teacher",
                phone="9800000002",
            )


@pytest.mark.django_db
def test_allow_same_employee_number_across_organizations(teacher):
    other = Organization.objects.create(legal_name="Other Institute Pvt. Ltd.", display_name="Other")
    other_branch = Branch.objects.create(organization=other, code="MAIN", name="Main")

    other_teacher = Teacher.objects.create(
        organization=other,
        branch=other_branch,
        employee_number="TCH-001",
        full_name="Same Number",
        phone="9811111111",
    )

    assert other_teacher.organization == other


@pytest.mark.django_db
def test_create_teacher_linked_to_user(organization, branch, user):
    teacher = Teacher.objects.create(
        organization=organization,
        branch=branch,
        user=user,
        employee_number="TCH-002",
        full_name="Bikash Karki",
        phone="9800000003",
    )

    assert teacher.user == user
    assert user.teacher_profiles.get() == teacher


@pytest.mark.django_db
def test_create_monthly_cut_percentage_contract(teacher, academic_year):
    contract = TeacherContract.objects.create(
        teacher=teacher,
        organization=teacher.organization,
        branch=teacher.branch,
        academic_year=academic_year,
        contract_type=TeacherContract.ContractType.MONTHLY_CUT_PERCENTAGE,
        default_teacher_cut_percentage=Decimal("40.0000"),
        effective_from_ad=date(2024, 4, 13),
        effective_from_bs="2081-01-01",
    )

    assert str(contract) == "TCH-001 - Monthly Cut Percentage"
    assert contract.default_teacher_cut_percentage == Decimal("40.0000")


@pytest.mark.django_db
def test_create_package_course_contract(teacher):
    contract = TeacherContract.objects.create(
        teacher=teacher,
        organization=teacher.organization,
        branch=teacher.branch,
        contract_type=TeacherContract.ContractType.PACKAGE_COURSE,
        package_amount=Decimal("25000.00"),
        effective_from_ad=date(2024, 5, 1),
    )

    assert contract.package_amount == Decimal("25000.00")
    assert contract.is_active is True


@pytest.mark.django_db
def test_create_fixed_monthly_salary_contract(teacher):
    contract = TeacherContract.objects.create(
        teacher=teacher,
        organization=teacher.organization,
        branch=teacher.branch,
        contract_type=TeacherContract.ContractType.FIXED_MONTHLY_SALARY,
        fixed_monthly_salary=Decimal("45000.00"),
        effective_from_ad=date(2024, 5, 1),
    )

    assert contract.fixed_monthly_salary == Decimal("45000.00")


@pytest.mark.django_db
def test_create_teacher_activity(teacher, academic_year, user):
    activity = TeacherActivity.objects.create(
        teacher=teacher,
        organization=teacher.organization,
        branch=teacher.branch,
        academic_year=academic_year,
        activity_type=TeacherActivity.ActivityType.MEETING,
        title="Monthly review",
        description="Discussed class progress.",
        activity_date_ad=date(2024, 7, 1),
        activity_date_bs="2081-03-17",
        created_by=user,
    )

    assert str(activity) == "TCH-001 - Monthly review"
    assert activity.status == TeacherActivity.Status.OPEN
    assert activity.created_by == user


@pytest.mark.django_db
def test_create_teacher_status_history(teacher, user):
    history = TeacherStatusHistory.objects.create(
        teacher=teacher,
        from_status=Teacher.Status.PENDING,
        to_status=Teacher.Status.ACTIVE,
        reason="Documents verified.",
        changed_by=user,
        metadata={"source": "test"},
    )

    assert str(history) == "TCH-001: pending -> active"
    assert history.changed_by == user


@pytest.mark.django_db
def test_branch_and_organization_relationships(teacher):
    assert teacher.branch.organization == teacher.organization
    assert teacher.organization.display_name == "Auras Education"
