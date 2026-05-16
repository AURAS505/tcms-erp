from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicYear
from accounts.models import Role, UserBranchAssignment, UserRole
from accounting.models import Account
from billing.models import BillStatus, BillingDiscount, StudentAdvanceBalance, StudentFeeDue
from organizations.models import Branch, Organization
from students.models import Student


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
        ("1210", "Student Receivable", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("2210", "Student Advance Revenue", Account.AccountType.LIABILITY, Account.NormalBalance.CREDIT),
        ("5700", "Discount Allowed", Account.AccountType.EXPENSE, Account.NormalBalance.DEBIT),
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


def branch_records(organization, branch, academic_year, suffix):
    student = Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number=f"ADM-{suffix}",
        full_name=f"Student {suffix}",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )
    due = StudentFeeDue.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        period_label="Shrawan 2081",
        original_amount=Decimal("2500.00"),
        net_amount=Decimal("2500.00"),
        balance_amount=Decimal("2500.00"),
        status=BillStatus.UNPAID,
    )
    discount = BillingDiscount.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        fee_due=due,
        discount_type=BillingDiscount.DiscountType.SCHOLARSHIP,
        discount_amount=Decimal("500.00"),
        reason="Scholarship",
        status=BillingDiscount.Status.PENDING_APPROVAL,
    )
    StudentAdvanceBalance.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        received_amount=Decimal("1000.00"),
        balance_amount=Decimal("1000.00"),
    )
    return student, due, discount


@pytest.fixture
def branch_context(organization, branches, academic_year):
    branch_a, branch_b = branches
    student_a, due_a, discount_a = branch_records(organization, branch_a, academic_year, "A")
    student_b, due_b, discount_b = branch_records(organization, branch_b, academic_year, "B")
    return {
        "branch_a": branch_a,
        "branch_b": branch_b,
        "student_a": student_a,
        "student_b": student_b,
        "due_a": due_a,
        "due_b": due_b,
        "discount_a": discount_a,
        "discount_b": discount_b,
    }


@pytest.mark.django_db
def test_branch_accountant_can_approve_same_branch_discount(branch_context, accounts):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch_context["branch_a"])

    response = client_for(accountant).post(
        f"/api/v1/billing-discounts/{branch_context['discount_a'].id}/approve/",
        {},
        format="json",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_branch_accountant_cannot_approve_other_branch_discount(branch_context, accounts):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch_context["branch_a"])

    response = client_for(accountant).post(
        f"/api/v1/billing-discounts/{branch_context['discount_b'].id}/approve/",
        {},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_branch_accountant_without_assignment_cannot_approve_discount(branch_context, accounts):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT)

    response = client_for(accountant).post(
        f"/api/v1/billing-discounts/{branch_context['discount_a'].id}/approve/",
        {},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_branch_accountant_cannot_apply_advance_to_other_branch_due(branch_context, accounts):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch_context["branch_a"])

    response = client_for(accountant).post(
        "/api/v1/student-advance-balances/apply-to-due/",
        {
            "student": str(branch_context["student_b"].id),
            "due": str(branch_context["due_b"].id),
            "amount": "500.00",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_super_admin_can_approve_any_branch_discount(branch_context, accounts):
    super_admin = get_user_model().objects.create_superuser(email="owner@example.com", password="secure-password")

    response = client_for(super_admin).post(
        f"/api/v1/billing-discounts/{branch_context['discount_b'].id}/approve/",
        {},
        format="json",
    )

    assert response.status_code == 200
