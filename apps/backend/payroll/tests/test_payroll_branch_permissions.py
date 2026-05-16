from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicYear
from accounts.models import Role, UserBranchAssignment, UserRole
from accounting.models import Account
from organizations.models import Branch, Organization
from payroll.models import TeacherEarning
from payroll.services import TeacherEarningService
from teachers.models import Teacher


@pytest.fixture
def organization():
    return Organization.objects.create(legal_name="Auras Education Pvt. Ltd.", display_name="Auras Education")


@pytest.fixture
def branches(organization):
    return (
        Branch.objects.create(organization=organization, code="A", name="Branch A", is_main_branch=True),
        Branch.objects.create(organization=organization, code="B", name="Branch B"),
    )


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
def accounts(organization):
    for code, name, account_type, normal_balance in [
        ("2110", "Teacher Payable", Account.AccountType.LIABILITY, Account.NormalBalance.CREDIT),
        ("5100", "Teacher Salary Expense", Account.AccountType.EXPENSE, Account.NormalBalance.DEBIT),
    ]:
        Account.objects.create(
            organization=organization,
            code=code,
            name=name,
            account_type=account_type,
            normal_balance=normal_balance,
        )


def user_with_role(role_code, *, branch=None, email_prefix=None):
    user = get_user_model().objects.create_user(
        email=f"{email_prefix or role_code}@example.com",
        password="secure-password",
    )
    role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role.RoleCode(role_code).label})
    UserRole.objects.create(user=user, role=role)
    if branch:
        UserBranchAssignment.objects.create(user=user, organization_id=branch.organization_id, branch_id=branch.id)
    return user


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def create_teacher(organization, branch, suffix):
    return Teacher.objects.create(
        organization=organization,
        branch=branch,
        employee_number=f"T-{suffix}",
        full_name=f"Teacher {suffix}",
        phone=f"98000000{suffix}",
        status=Teacher.Status.ACTIVE,
    )


def earning_payload(organization, branch, academic_year, teacher):
    return {
        "organization": str(organization.id),
        "branch": str(branch.id),
        "academic_year": str(academic_year.id),
        "teacher": str(teacher.id),
        "earning_date_ad": "2024-07-20",
        "gross_amount": "1000.00",
        "deduction_amount": "0.00",
    }


@pytest.fixture
def branch_context(organization, branches, academic_year):
    branch_a, branch_b = branches
    teacher_a = create_teacher(organization, branch_a, "A")
    teacher_b = create_teacher(organization, branch_b, "B")
    earning_b = TeacherEarning.objects.create(
        organization=organization,
        branch=branch_b,
        academic_year=academic_year,
        teacher=teacher_b,
        earning_source=TeacherEarning.EarningSource.MANUAL_ADJUSTMENT,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("1000.00"),
        deduction_amount=Decimal("0.00"),
        net_amount=Decimal("1000.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("1000.00"),
        status=TeacherEarning.Status.DRAFT,
    )
    return {
        "branch_a": branch_a,
        "branch_b": branch_b,
        "teacher_a": teacher_a,
        "teacher_b": teacher_b,
        "earning_b": earning_b,
    }


@pytest.mark.django_db
def test_accountant_cannot_create_manual_earning_for_other_branch(organization, academic_year, branch_context):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch_context["branch_a"])

    response = client_for(accountant).post(
        "/api/v1/teacher-earnings/create-manual/",
        earning_payload(organization, branch_context["branch_b"], academic_year, branch_context["teacher_b"]),
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_accountant_without_assignment_cannot_create_manual_earning(organization, academic_year, branch_context):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT)

    response = client_for(accountant).post(
        "/api/v1/teacher-earnings/create-manual/",
        earning_payload(organization, branch_context["branch_a"], academic_year, branch_context["teacher_a"]),
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_accountant_cannot_approve_other_branch_earning(branch_context, accounts):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch_context["branch_a"])

    response = client_for(accountant).post(
        f"/api/v1/teacher-earnings/{branch_context['earning_b'].id}/approve/",
        {},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_super_admin_can_approve_any_branch_earning(branch_context, accounts):
    super_admin = get_user_model().objects.create_superuser(email="super@example.com", password="secure-password")

    response = client_for(super_admin).post(
        f"/api/v1/teacher-earnings/{branch_context['earning_b'].id}/approve/",
        {},
        format="json",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_super_admin_can_post_any_branch_earning(branch_context, accounts):
    super_admin = get_user_model().objects.create_superuser(email="super-post@example.com", password="secure-password")
    TeacherEarningService.approve_earning(earning_id=branch_context["earning_b"].id, approved_by=super_admin)

    response = client_for(super_admin).post(
        f"/api/v1/teacher-earnings/{branch_context['earning_b'].id}/post/",
        {},
        format="json",
    )

    assert response.status_code == 200
