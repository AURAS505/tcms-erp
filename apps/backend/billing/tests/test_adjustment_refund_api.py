from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicPeriod, AcademicYear
from accounts.models import Role, UserBranchAssignment, UserRole
from accounting.models import Account, JournalEntry
from billing.models import (
    BillStatus,
    BillingDiscount,
    BillingFine,
    BillingWaiver,
    StudentAdvanceBalance,
    StudentFeeDue,
    StudentInvoice,
    StudentPayment,
    StudentRefund,
)
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
def academic_period(organization, academic_year):
    return AcademicPeriod.objects.create(
        organization=organization,
        academic_year=academic_year,
        name="Shrawan 2081",
        period_order=1,
        bs_month=4,
        bs_month_name="Shrawan",
        bs_year=2081,
        bs_start_date="2081-04-01",
        bs_end_date="2081-04-32",
        ad_start_date=date(2024, 7, 16),
        ad_end_date=date(2024, 8, 16),
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
def due(organization, branch, academic_year, academic_period, student):
    return StudentFeeDue.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        student=student,
        period_label="Shrawan 2081",
        due_date_ad=date(2024, 7, 20),
        original_amount=Decimal("2500.00"),
        net_amount=Decimal("2500.00"),
        balance_amount=Decimal("2500.00"),
        status=BillStatus.UNPAID,
    )


@pytest.fixture
def invoice(organization, branch, academic_year, academic_period, student):
    return StudentInvoice.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        student=student,
        invoice_number="INV-001",
        invoice_date_ad=date(2024, 7, 20),
        subtotal=Decimal("1500.00"),
        total_amount=Decimal("1500.00"),
        balance_amount=Decimal("1500.00"),
        status=BillStatus.UNPAID,
    )


@pytest.fixture
def accounts(organization):
    for code, name, account_type, normal_balance in [
        ("1110", "Cash in Hand", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1210", "Student Receivable", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("2210", "Student Advance Revenue", Account.AccountType.LIABILITY, Account.NormalBalance.CREDIT),
        ("4400", "Fine Income", Account.AccountType.REVENUE, Account.NormalBalance.CREDIT),
        ("5700", "Discount Allowed", Account.AccountType.EXPENSE, Account.NormalBalance.DEBIT),
        ("5800", "Bad Debt Expense", Account.AccountType.EXPENSE, Account.NormalBalance.DEBIT),
    ]:
        Account.objects.create(
            organization=organization,
            code=code,
            name=name,
            account_type=account_type,
            normal_balance=normal_balance,
        )


def user_with_role(role_code, *, branch=None):
    user = get_user_model().objects.create_user(email=f"{role_code}@example.com", password="secure-password")
    role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role.RoleCode(role_code).label})
    UserRole.objects.create(user=user, role=role)
    if branch:
        UserBranchAssignment.objects.create(user=user, organization_id=branch.organization_id, branch_id=branch.id)
    return user


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def accountant(branch):
    return user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)


@pytest.fixture
def teacher(branch):
    return user_with_role(Role.RoleCode.TEACHER, branch=branch)


@pytest.fixture
def advance_balance(organization, branch, academic_year, student):
    return StudentAdvanceBalance.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        received_amount=Decimal("3000.00"),
        balance_amount=Decimal("3000.00"),
    )


@pytest.fixture
def advance_payment(student):
    return StudentPayment.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        receipt_number="RC-ADV",
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("3000.00"),
        net_received_amount=Decimal("3000.00"),
        is_advance_payment=True,
        status=StudentPayment.Status.POSTED,
    )


def discount_for(student, due):
    return BillingDiscount.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        fee_due=due,
        discount_type=BillingDiscount.DiscountType.SCHOLARSHIP,
        discount_amount=Decimal("500.00"),
        reason="Scholarship",
        status=BillingDiscount.Status.PENDING_APPROVAL,
    )


def waiver_for(student, due):
    return BillingWaiver.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        fee_due=due,
        waiver_amount=Decimal("500.00"),
        reason="Write-off",
        status=BillingWaiver.Status.PENDING_APPROVAL,
    )


def fine_for(student, due):
    return BillingFine.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        fee_due=due,
        fine_type=BillingFine.FineType.LATE_FEE,
        amount=Decimal("200.00"),
        reason="Late fee",
        status=BillingFine.Status.PENDING_APPROVAL,
    )


@pytest.mark.django_db
def test_unauthenticated_user_cannot_call_mutation_endpoint(student, due):
    discount = discount_for(student, due)

    response = APIClient().post(f"/api/v1/billing-discounts/{discount.id}/approve/", {}, format="json")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_unauthorized_role_cannot_approve_discount(student, due, teacher):
    discount = discount_for(student, due)

    response = client_for(teacher).post(f"/api/v1/billing-discounts/{discount.id}/approve/", {}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_financial_approver_can_approve_discount_and_post_journal(student, due, accountant, accounts):
    discount = discount_for(student, due)

    response = client_for(accountant).post(f"/api/v1/billing-discounts/{discount.id}/approve/", {}, format="json")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == BillingDiscount.Status.APPROVED
    assert JournalEntry.objects.filter(source_model="BillingDiscount", source_number=str(discount.id)).exists()


@pytest.mark.django_db
def test_waiver_approval_posts_journal(student, due, accountant, accounts):
    waiver = waiver_for(student, due)

    response = client_for(accountant).post(f"/api/v1/billing-waivers/{waiver.id}/approve/", {}, format="json")

    assert response.status_code == 200
    assert JournalEntry.objects.filter(source_model="BillingWaiver", source_number=str(waiver.id)).exists()


@pytest.mark.django_db
def test_fine_approval_posts_journal(student, due, accountant, accounts):
    fine = fine_for(student, due)

    response = client_for(accountant).post(f"/api/v1/billing-fines/{fine.id}/approve/", {}, format="json")

    assert response.status_code == 200
    assert JournalEntry.objects.filter(source_model="BillingFine", source_number=str(fine.id)).exists()


@pytest.mark.django_db
def test_advance_application_to_due_posts_journal(student, due, advance_balance, accountant, accounts):
    response = client_for(accountant).post(
        "/api/v1/student-advance-balances/apply-to-due/",
        {"student": str(student.id), "due": str(due.id), "amount": "500.00"},
        format="json",
    )

    assert response.status_code == 200
    assert JournalEntry.objects.filter(source_model="AdvanceApplication", source_number=f"ADV-APPLY-DUE-{due.id}").exists()


@pytest.mark.django_db
def test_advance_application_to_invoice_posts_journal(student, invoice, advance_balance, accountant, accounts):
    response = client_for(accountant).post(
        "/api/v1/student-advance-balances/apply-to-invoice/",
        {"student": str(student.id), "invoice": str(invoice.id), "amount": "500.00"},
        format="json",
    )

    assert response.status_code == 200
    assert JournalEntry.objects.filter(
        source_model="AdvanceApplication",
        source_number=f"ADV-APPLY-INV-{invoice.id}",
    ).exists()


@pytest.mark.django_db
def test_refund_approval_and_payment_from_advance_post_journal(
    student, accountant, advance_payment, advance_balance, accounts
):
    refund = StudentRefund.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        original_payment=advance_payment,
        refund_amount=Decimal("1000.00"),
        refund_reason="Advance refund",
        status=StudentRefund.Status.PENDING_APPROVAL,
    )

    approve_response = client_for(accountant).post(f"/api/v1/student-refunds/{refund.id}/approve/", {}, format="json")
    pay_response = client_for(accountant).post(f"/api/v1/student-refunds/{refund.id}/pay/", {}, format="json")

    assert approve_response.status_code == 200
    assert pay_response.status_code == 200
    assert pay_response.json()["data"]["status"] == StudentRefund.Status.PAID
    assert JournalEntry.objects.filter(source_model="StudentRefund", source_object_id=refund.id).exists()


@pytest.mark.django_db
def test_recognized_revenue_refund_remains_blocked(student, accountant):
    payment = StudentPayment.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        receipt_number="RC-REV",
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("500.00"),
        net_received_amount=Decimal("500.00"),
        is_advance_payment=False,
        status=StudentPayment.Status.POSTED,
    )
    refund = StudentRefund.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        original_payment=payment,
        refund_amount=Decimal("100.00"),
        refund_reason="Revenue refund",
        status=StudentRefund.Status.PENDING_APPROVAL,
    )

    response = client_for(accountant).post(f"/api/v1/student-refunds/{refund.id}/approve/", {}, format="json")

    assert response.status_code == 400
    assert "recognized revenue" in str(response.json()["errors"]).lower()


@pytest.mark.django_db
def test_approved_discount_remains_read_only_via_api(student, due, accountant, accounts):
    discount = discount_for(student, due)
    client_for(accountant).post(f"/api/v1/billing-discounts/{discount.id}/approve/", {}, format="json")

    response = client_for(accountant).patch(
        f"/api/v1/billing-discounts/{discount.id}/",
        {"reason": "changed"},
        format="json",
    )

    assert response.status_code == 405
