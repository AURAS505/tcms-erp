from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum

from academic.models import AcademicYear
from accounting.models import Account, JournalEntry
from common.models import AuditLog
from organizations.models import Branch, Organization
from payroll.models import TeacherEarning, TeacherPayment
from payroll.services import TeacherPaymentAllocationInput, TeacherPaymentService
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
def maker():
    return get_user_model().objects.create_user(email="maker.payment@example.com", password="secure-password")


@pytest.fixture
def checker():
    return get_user_model().objects.create_user(email="checker.payment@example.com", password="secure-password")


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
def earning(organization, branch, academic_year, teacher):
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


@pytest.fixture
def configure_accounts(organization):
    accounts = [
        ("1110", "Cash in Hand", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1120", "Bank Account", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1130", "Online Wallet", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("2110", "Teacher Payable", Account.AccountType.LIABILITY, Account.NormalBalance.CREDIT),
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
def test_create_draft_teacher_payment_no_journal(organization, branch, academic_year, teacher, earning, maker):
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
    assert payment.status == TeacherPayment.Status.DRAFT
    assert JournalEntry.objects.count() == 0


@pytest.mark.django_db
def test_reject_allocation_greater_than_payment_amount(organization, branch, academic_year, teacher, earning, maker):
    with pytest.raises(ValidationError):
        TeacherPaymentService.create_draft_payment(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            teacher=teacher,
            payment_date_ad=date(2024, 7, 22),
            payment_method=TeacherPayment.PaymentMethod.CASH,
            amount=Decimal("400.00"),
            created_by=maker,
            allocations=[TeacherPaymentAllocationInput(teacher_earning_id=str(earning.id), amount_allocated=Decimal("500.00"))],
        )


@pytest.mark.django_db
def test_reject_allocation_greater_than_earning_balance(organization, branch, academic_year, teacher, earning, maker):
    with pytest.raises(ValidationError):
        TeacherPaymentService.create_draft_payment(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            teacher=teacher,
            payment_date_ad=date(2024, 7, 22),
            payment_method=TeacherPayment.PaymentMethod.CASH,
            amount=Decimal("1200.00"),
            created_by=maker,
            allocations=[TeacherPaymentAllocationInput(teacher_earning_id=str(earning.id), amount_allocated=Decimal("1200.00"))],
        )


@pytest.mark.django_db
def test_post_cash_teacher_payment(organization, branch, academic_year, teacher, earning, maker, checker, configure_accounts):
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
    posted = TeacherPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)
    entry = JournalEntry.objects.get(source_model="TeacherPayment", source_object_id=payment.id)
    debit_line = entry.lines.get(debit_amount=Decimal("400.00"))
    credit_line = entry.lines.get(credit_amount=Decimal("400.00"))
    earning.refresh_from_db()
    assert posted.status == TeacherPayment.Status.POSTED
    assert debit_line.account.code == "2110"
    assert credit_line.account.code == "1110"
    assert earning.status == TeacherEarning.Status.PARTIAL


@pytest.mark.django_db
def test_post_bank_teacher_payment_and_full_paid_status(
    organization, branch, academic_year, teacher, earning, maker, checker, configure_accounts
):
    payment = TeacherPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        payment_date_ad=date(2024, 7, 23),
        payment_method=TeacherPayment.PaymentMethod.BANK,
        amount=Decimal("1000.00"),
        created_by=maker,
        allocations=[TeacherPaymentAllocationInput(teacher_earning_id=str(earning.id), amount_allocated=Decimal("1000.00"))],
    )
    posted = TeacherPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)
    entry = JournalEntry.objects.get(source_model="TeacherPayment", source_object_id=payment.id)
    totals = entry.lines.aggregate(
        debit_total=Sum("debit_amount", default=Decimal("0.00")),
        credit_total=Sum("credit_amount", default=Decimal("0.00")),
    )
    credit_line = entry.lines.get(credit_amount=Decimal("1000.00"))
    earning.refresh_from_db()
    assert posted.voucher_number.startswith("TV-")
    assert totals["debit_total"] == totals["credit_total"] == Decimal("1000.00")
    assert credit_line.account.code == "1120"
    assert earning.paid_amount == Decimal("1000.00")
    assert earning.balance_amount == Decimal("0.00")
    assert earning.status == TeacherEarning.Status.PAID


@pytest.mark.django_db
def test_maker_checker_blocks_self_approval(organization, branch, academic_year, teacher, earning, maker, configure_accounts):
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
    with pytest.raises(ValidationError):
        TeacherPaymentService.approve_payment(payment_id=payment.id, approved_by=maker)


@pytest.mark.django_db
def test_audit_log_created_for_teacher_payment_post(
    organization, branch, academic_year, teacher, earning, maker, checker, configure_accounts
):
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
    assert AuditLog.objects.filter(
        module=AuditLog.Module.PAYROLL,
        action=AuditLog.Action.POST,
        metadata__event="teacher_payment_posted",
    ).exists()
