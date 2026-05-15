from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from academic.models import AcademicYear
from accounting.models import Account, JournalEntry
from billing.models import StudentAdvanceBalance, StudentPayment, StudentRefund
from billing.services import StudentRefundService
from common.models import AuditLog
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
def maker():
    return get_user_model().objects.create_user(email="maker.refund@example.com", password="secure-password")


@pytest.fixture
def checker():
    return get_user_model().objects.create_user(email="checker.refund@example.com", password="secure-password")


@pytest.fixture
def cashier():
    return get_user_model().objects.create_user(email="cashier.refund@example.com", password="secure-password")


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
def advance_payment(student, maker):
    return StudentPayment.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        receipt_number="RC-000001",
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("3000.00"),
        net_received_amount=Decimal("3000.00"),
        is_advance_payment=True,
        status=StudentPayment.Status.POSTED,
        created_by=maker,
    )


@pytest.fixture
def revenue_payment(student, maker):
    return StudentPayment.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        receipt_number="RC-000002",
        payment_date_ad=date(2024, 7, 21),
        payment_method=StudentPayment.PaymentMethod.BANK,
        amount=Decimal("500.00"),
        net_received_amount=Decimal("500.00"),
        is_advance_payment=False,
        status=StudentPayment.Status.POSTED,
        created_by=maker,
    )


@pytest.fixture
def advance_balance(student):
    return StudentAdvanceBalance.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        opening_amount=Decimal("0.00"),
        received_amount=Decimal("3000.00"),
        applied_amount=Decimal("0.00"),
        refunded_amount=Decimal("0.00"),
        balance_amount=Decimal("3000.00"),
    )


@pytest.fixture
def configure_accounts(organization):
    accounts = [
        ("1110", "Cash in Hand", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1120", "Bank Account", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1130", "Online Wallet", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("2210", "Student Advance Revenue", Account.AccountType.LIABILITY, Account.NormalBalance.CREDIT),
    ]
    for code, name, account_type, normal_balance in accounts:
        Account.objects.create(
            organization=organization,
            code=code,
            name=name,
            account_type=account_type,
            normal_balance=normal_balance,
        )


@pytest.mark.django_db
def test_approve_and_pay_refund_from_advance(
    student, maker, checker, cashier, advance_payment, advance_balance, configure_accounts
):
    refund = StudentRefund.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        original_payment=advance_payment,
        refund_voucher_number="RF-001",
        refund_date_ad=date(2024, 8, 1),
        refund_amount=Decimal("1000.00"),
        refund_reason="Advance refund",
        status=StudentRefund.Status.PENDING_APPROVAL,
        requested_by=maker,
    )

    approved = StudentRefundService.approve_refund(refund_id=refund.id, approved_by=checker)
    paid = StudentRefundService.pay_refund(refund_id=approved.id, paid_by=cashier)
    advance_balance.refresh_from_db()
    entry = JournalEntry.objects.get(source_model="StudentRefund", source_object_id=refund.id)

    assert paid.status == StudentRefund.Status.PAID
    assert advance_balance.refunded_amount == Decimal("1000.00")
    assert advance_balance.balance_amount == Decimal("2000.00")
    debit_line = entry.lines.get(debit_amount=Decimal("1000.00"))
    credit_line = entry.lines.get(credit_amount=Decimal("1000.00"))
    assert debit_line.account.code == "2210"
    assert credit_line.account.code == "1110"


@pytest.mark.django_db
def test_reject_refund_greater_than_advance_balance(student, maker, checker, cashier, advance_payment, advance_balance, configure_accounts):
    refund = StudentRefund.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        original_payment=advance_payment,
        refund_amount=Decimal("3500.00"),
        refund_reason="Too much",
        status=StudentRefund.Status.PENDING_APPROVAL,
        requested_by=maker,
    )

    approved = StudentRefundService.approve_refund(refund_id=refund.id, approved_by=checker)
    with pytest.raises(ValidationError):
        StudentRefundService.pay_refund(refund_id=approved.id, paid_by=cashier)


@pytest.mark.django_db
def test_reject_recognized_revenue_refund_when_policy_unclear(student, maker, checker, revenue_payment):
    refund = StudentRefund.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        original_payment=revenue_payment,
        refund_amount=Decimal("100.00"),
        refund_reason="Revenue refund",
        status=StudentRefund.Status.PENDING_APPROVAL,
        requested_by=maker,
    )
    with pytest.raises(ValidationError):
        StudentRefundService.approve_refund(refund_id=refund.id, approved_by=checker)


@pytest.mark.django_db
def test_maker_checker_prevents_self_approval(student, maker, advance_payment, advance_balance):
    refund = StudentRefund.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        original_payment=advance_payment,
        refund_amount=Decimal("100.00"),
        refund_reason="Self approval check",
        status=StudentRefund.Status.PENDING_APPROVAL,
        requested_by=maker,
    )
    with pytest.raises(ValidationError):
        StudentRefundService.approve_refund(refund_id=refund.id, approved_by=maker)


@pytest.mark.django_db
def test_refund_flow_creates_audit_logs(
    student, maker, checker, cashier, advance_payment, advance_balance, configure_accounts
):
    refund = StudentRefund.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        original_payment=advance_payment,
        refund_voucher_number="RF-002",
        refund_amount=Decimal("200.00"),
        refund_reason="Audit check",
        status=StudentRefund.Status.PENDING_APPROVAL,
        requested_by=maker,
    )
    StudentRefundService.approve_refund(refund_id=refund.id, approved_by=checker)
    StudentRefundService.pay_refund(refund_id=refund.id, paid_by=cashier)

    assert AuditLog.objects.filter(
        module=AuditLog.Module.BILLING,
        action=AuditLog.Action.POST,
        metadata__event="refund_paid",
    ).exists()
