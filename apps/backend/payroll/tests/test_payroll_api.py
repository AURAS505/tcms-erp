from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicYear
from accounts.models import Role, UserBranchAssignment, UserRole
from accounting.models import Account, JournalEntry
from organizations.models import Branch, Organization
from payroll.models import TeacherEarning, TeacherPayment
from payroll.services import TeacherEarningService, TeacherPaymentAllocationInput, TeacherPaymentService
from teachers.models import Teacher


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
def teacher(organization, branch):
    return Teacher.objects.create(
        organization=organization,
        branch=branch,
        employee_number="T-001",
        full_name="Ram Sir",
        phone="9800000000",
        status=Teacher.Status.ACTIVE,
    )


@pytest.fixture
def accounts(organization):
    for code, name, account_type, normal_balance in [
        ("1110", "Cash in Hand", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1120", "Bank Account", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1130", "Online Wallet", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
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


def earning_payload(organization, branch, academic_year, teacher, gross="1000.00", deduction="100.00"):
    return {
        "organization": str(organization.id),
        "branch": str(branch.id),
        "academic_year": str(academic_year.id),
        "teacher": str(teacher.id),
        "earning_date_ad": "2024-07-20",
        "gross_amount": gross,
        "deduction_amount": deduction,
        "period_label": "Shrawan 2081",
    }


def payment_payload(organization, branch, academic_year, teacher, earning, amount="400.00"):
    return {
        "organization": str(organization.id),
        "branch": str(branch.id),
        "academic_year": str(academic_year.id),
        "teacher": str(teacher.id),
        "payment_date_ad": "2024-07-22",
        "payment_method": TeacherPayment.PaymentMethod.CASH,
        "amount": amount,
        "allocations": [{"teacher_earning": str(earning.id), "amount_allocated": amount}],
    }


def posted_earning(organization, branch, academic_year, teacher):
    return TeacherEarning.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        earning_source=TeacherEarning.EarningSource.MANUAL_ADJUSTMENT,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("1000.00"),
        deduction_amount=Decimal("0.00"),
        net_amount=Decimal("1000.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("1000.00"),
        status=TeacherEarning.Status.POSTED,
    )


@pytest.mark.django_db
def test_unauthenticated_user_cannot_call_payroll_mutation(organization, branch, academic_year, teacher):
    response = APIClient().post(
        "/api/v1/teacher-earnings/create-manual/",
        earning_payload(organization, branch, academic_year, teacher),
        format="json",
    )

    assert response.status_code in {401, 403}


@pytest.mark.django_db
@pytest.mark.parametrize("role_code", [Role.RoleCode.RECEPTIONIST, Role.RoleCode.TEACHER, Role.RoleCode.AUDITOR])
def test_non_financial_roles_cannot_create_payroll_records(organization, branch, academic_year, teacher, role_code):
    user = user_with_role(role_code, branch=branch)

    response = client_for(user).post(
        "/api/v1/teacher-earnings/create-manual/",
        earning_payload(organization, branch, academic_year, teacher),
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_accountant_can_create_manual_earning_in_assigned_branch(organization, branch, academic_year, teacher):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)

    response = client_for(accountant).post(
        "/api/v1/teacher-earnings/create-manual/",
        earning_payload(organization, branch, academic_year, teacher),
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["data"]["status"] == TeacherEarning.Status.DRAFT
    assert response.json()["data"]["net_amount"] == "900.00"


@pytest.mark.django_db
def test_earning_approve_and_post_endpoints_create_salary_journal(organization, branch, academic_year, teacher, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="checker")
    create_response = client_for(maker).post(
        "/api/v1/teacher-earnings/create-manual/",
        earning_payload(organization, branch, academic_year, teacher),
        format="json",
    )
    earning_id = create_response.json()["data"]["id"]

    approve_response = client_for(checker).post(f"/api/v1/teacher-earnings/{earning_id}/approve/", {}, format="json")
    post_response = client_for(checker).post(f"/api/v1/teacher-earnings/{earning_id}/post/", {}, format="json")
    entry = JournalEntry.objects.get(source_model="TeacherEarning", source_object_id=earning_id)
    debit_line = entry.lines.get(debit_amount=Decimal("900.00"))
    credit_line = entry.lines.get(credit_amount=Decimal("900.00"))

    assert approve_response.status_code == 200
    assert post_response.status_code == 200
    assert debit_line.account.code == "5100"
    assert credit_line.account.code == "2110"


@pytest.mark.django_db
def test_earning_maker_checker_prevents_self_approval(organization, branch, academic_year, teacher):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)
    create_response = client_for(maker).post(
        "/api/v1/teacher-earnings/create-manual/",
        earning_payload(organization, branch, academic_year, teacher),
        format="json",
    )
    earning_id = create_response.json()["data"]["id"]

    response = client_for(maker).post(f"/api/v1/teacher-earnings/{earning_id}/approve/", {}, format="json")

    assert response.status_code == 400
    assert "maker-checker" in str(response.json()["errors"]).lower()


@pytest.mark.django_db
def test_teacher_payment_draft_and_approval_posting_create_payment_journal(
    organization, branch, academic_year, teacher, accounts
):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="payroll-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="payroll-checker")
    earning = posted_earning(organization, branch, academic_year, teacher)

    draft_response = client_for(maker).post(
        "/api/v1/teacher-payments/create-draft/",
        payment_payload(organization, branch, academic_year, teacher, earning),
        format="json",
    )
    payment_id = draft_response.json()["data"]["id"]
    approve_response = client_for(checker).post(f"/api/v1/teacher-payments/{payment_id}/approve/", {}, format="json")
    entry = JournalEntry.objects.get(source_model="TeacherPayment", source_object_id=payment_id)
    debit_line = entry.lines.get(debit_amount=Decimal("400.00"))
    credit_line = entry.lines.get(credit_amount=Decimal("400.00"))

    assert draft_response.status_code == 201
    assert approve_response.status_code == 200
    assert approve_response.json()["data"]["status"] == TeacherPayment.Status.POSTED
    assert debit_line.account.code == "2110"
    assert credit_line.account.code == "1110"


@pytest.mark.django_db
def test_teacher_payment_direct_post_requires_approved_status(organization, branch, academic_year, teacher, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="payment-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="payment-checker")
    earning = posted_earning(organization, branch, academic_year, teacher)
    draft_response = client_for(maker).post(
        "/api/v1/teacher-payments/create-draft/",
        payment_payload(organization, branch, academic_year, teacher, earning),
        format="json",
    )

    response = client_for(checker).post(
        f"/api/v1/teacher-payments/{draft_response.json()['data']['id']}/post/",
        {},
        format="json",
    )

    assert response.status_code == 400
    assert "only approved" in str(response.json()["errors"]).lower()


@pytest.mark.django_db
def test_teacher_payment_maker_checker_prevents_self_approval(organization, branch, academic_year, teacher, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)
    earning = posted_earning(organization, branch, academic_year, teacher)
    draft_response = client_for(maker).post(
        "/api/v1/teacher-payments/create-draft/",
        payment_payload(organization, branch, academic_year, teacher, earning),
        format="json",
    )
    payment_id = draft_response.json()["data"]["id"]

    response = client_for(maker).post(f"/api/v1/teacher-payments/{payment_id}/approve/", {}, format="json")

    assert response.status_code == 400
    assert "maker-checker" in str(response.json()["errors"]).lower()


@pytest.mark.django_db
def test_posted_teacher_payment_cannot_be_patched(organization, branch, academic_year, teacher, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="patch-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="patch-checker")
    earning = posted_earning(organization, branch, academic_year, teacher)
    payment = TeacherPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        payment_date_ad=date(2024, 7, 22),
        payment_method=TeacherPayment.PaymentMethod.CASH,
        amount=Decimal("400.00"),
        created_by=maker,
        allocations=[TeacherPaymentAllocationInput(teacher_earning_id=str(earning.id), amount_allocated=Decimal("400.00"))],
    )
    TeacherPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)

    response = client_for(checker).patch(f"/api/v1/teacher-payments/{payment.id}/", {"notes": "changed"}, format="json")

    assert response.status_code == 405


@pytest.mark.django_db
def test_posted_teacher_earning_cannot_be_patched(organization, branch, academic_year, teacher, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="earning-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="earning-checker")
    earning = TeacherEarningService.create_manual_earning(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("1000.00"),
        deduction_amount=Decimal("0.00"),
        created_by=maker,
    )
    TeacherEarningService.approve_earning(earning_id=earning.id, approved_by=checker)
    TeacherEarningService.post_earning(earning_id=earning.id, posted_by=checker)

    response = client_for(checker).patch(f"/api/v1/teacher-earnings/{earning.id}/", {"notes": "changed"}, format="json")

    assert response.status_code == 405
