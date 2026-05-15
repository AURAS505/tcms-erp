from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum

from academic.models import AcademicPeriod, AcademicYear
from accounting.models import Account, JournalEntry
from billing.models import BillStatus, StudentAdvanceBalance, StudentFeeDue, StudentInvoice
from billing.services import AdvanceApplicationService
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
def user():
    return get_user_model().objects.create_user(email="approver@example.com", password="secure-password")


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
        discount_amount=Decimal("0.00"),
        fine_amount=Decimal("0.00"),
        net_amount=Decimal("2500.00"),
        paid_amount=Decimal("0.00"),
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
        invoice_date_ad=date(2024, 7, 16),
        subtotal=Decimal("2500.00"),
        discount_amount=Decimal("0.00"),
        fine_amount=Decimal("0.00"),
        total_amount=Decimal("2500.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("2500.00"),
        status=BillStatus.UNPAID,
    )


@pytest.fixture
def advance_balance(organization, branch, academic_year, student):
    return StudentAdvanceBalance.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
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
        ("1210", "Student Receivable", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
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
def test_apply_advance_to_due(student, due, advance_balance, user, configure_accounts):
    updated_due = AdvanceApplicationService.apply_advance_to_due(
        student=student,
        due_id=due.id,
        amount=Decimal("1000.00"),
        applied_by=user,
    )
    advance_balance.refresh_from_db()

    assert updated_due.paid_amount == Decimal("1000.00")
    assert updated_due.balance_amount == Decimal("1500.00")
    assert updated_due.status == BillStatus.PARTIAL
    assert advance_balance.applied_amount == Decimal("1000.00")
    assert advance_balance.balance_amount == Decimal("2000.00")


@pytest.mark.django_db
def test_apply_advance_to_invoice(student, invoice, advance_balance, user, configure_accounts):
    updated_invoice = AdvanceApplicationService.apply_advance_to_invoice(
        student=student,
        invoice_id=invoice.id,
        amount=Decimal("2500.00"),
        applied_by=user,
    )
    advance_balance.refresh_from_db()

    assert updated_invoice.balance_amount == Decimal("0.00")
    assert updated_invoice.status == BillStatus.PAID
    assert advance_balance.applied_amount == Decimal("2500.00")
    assert advance_balance.balance_amount == Decimal("500.00")


@pytest.mark.django_db
def test_reject_advance_application_greater_than_available_balance(student, due, advance_balance, user, configure_accounts):
    with pytest.raises(ValidationError):
        AdvanceApplicationService.apply_advance_to_due(
            student=student,
            due_id=due.id,
            amount=Decimal("3500.00"),
            applied_by=user,
        )


@pytest.mark.django_db
def test_reject_advance_application_greater_than_due_balance(student, due, advance_balance, user, configure_accounts):
    with pytest.raises(ValidationError):
        AdvanceApplicationService.apply_advance_to_due(
            student=student,
            due_id=due.id,
            amount=Decimal("2600.00"),
            applied_by=user,
        )


@pytest.mark.django_db
def test_advance_application_creates_balanced_journal_and_audit(
    student, due, advance_balance, user, configure_accounts
):
    AdvanceApplicationService.apply_advance_to_due(
        student=student,
        due_id=due.id,
        amount=Decimal("1000.00"),
        applied_by=user,
    )

    entry = JournalEntry.objects.get(source_model="AdvanceApplication")
    totals = entry.lines.aggregate(
        debit_total=Sum("debit_amount", default=Decimal("0.00")),
        credit_total=Sum("credit_amount", default=Decimal("0.00")),
    )
    assert totals["debit_total"] == totals["credit_total"] == Decimal("1000.00")
    assert AuditLog.objects.filter(
        module=AuditLog.Module.BILLING,
        action=AuditLog.Action.POST,
        metadata__event="advance_applied_to_due",
    ).exists()
