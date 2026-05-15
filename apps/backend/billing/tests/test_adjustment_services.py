from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from academic.models import AcademicPeriod, AcademicYear
from accounting.models import Account, JournalEntry
from billing.models import BillStatus, BillingDiscount, BillingFine, BillingWaiver, StudentFeeDue
from billing.services import BillingAdjustmentService
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
def maker():
    return get_user_model().objects.create_user(email="maker.adjust@example.com", password="secure-password")


@pytest.fixture
def checker():
    return get_user_model().objects.create_user(email="checker.adjust@example.com", password="secure-password")


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
def configure_accounts(organization):
    accounts = [
        ("1210", "Student Receivable", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("4400", "Fine Income", Account.AccountType.REVENUE, Account.NormalBalance.CREDIT),
        ("5700", "Discount Allowed", Account.AccountType.EXPENSE, Account.NormalBalance.DEBIT),
        ("5800", "Bad Debt Expense", Account.AccountType.EXPENSE, Account.NormalBalance.DEBIT),
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
def test_approve_discount_against_due_and_post_journal(student, due, maker, checker, configure_accounts):
    discount = BillingDiscount.objects.create(
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

    approved = BillingAdjustmentService.approve_discount(discount_id=discount.id, approved_by=checker)
    due.refresh_from_db()
    entry = JournalEntry.objects.get(source_model="BillingDiscount", source_number=str(discount.id))

    assert approved.status == BillingDiscount.Status.APPROVED
    assert due.discount_amount == Decimal("500.00")
    assert due.balance_amount == Decimal("2000.00")
    debit_line = entry.lines.get(debit_amount=Decimal("500.00"))
    credit_line = entry.lines.get(credit_amount=Decimal("500.00"))
    assert debit_line.account.code == "5700"
    assert credit_line.account.code == "1210"


@pytest.mark.django_db
def test_reject_discount_greater_than_due_balance(student, due, checker, configure_accounts):
    discount = BillingDiscount.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        fee_due=due,
        discount_type=BillingDiscount.DiscountType.SCHOLARSHIP,
        discount_amount=Decimal("2600.00"),
        reason="Invalid discount",
        status=BillingDiscount.Status.PENDING_APPROVAL,
    )
    with pytest.raises(ValidationError):
        BillingAdjustmentService.approve_discount(discount_id=discount.id, approved_by=checker)


@pytest.mark.django_db
def test_approve_waiver_writeoff(student, due, checker, configure_accounts):
    waiver = BillingWaiver.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        fee_due=due,
        waiver_amount=Decimal("2500.00"),
        reason="Write-off",
        status=BillingWaiver.Status.PENDING_APPROVAL,
    )

    approved = BillingAdjustmentService.approve_waiver(waiver_id=waiver.id, approved_by=checker)
    due.refresh_from_db()
    entry = JournalEntry.objects.get(source_model="BillingWaiver", source_number=str(waiver.id))

    assert approved.status == BillingWaiver.Status.APPROVED
    assert due.status == BillStatus.WRITTEN_OFF
    debit_line = entry.lines.get(debit_amount=Decimal("2500.00"))
    credit_line = entry.lines.get(credit_amount=Decimal("2500.00"))
    assert debit_line.account.code == "5800"
    assert credit_line.account.code == "1210"


@pytest.mark.django_db
def test_approve_fine(student, due, checker, configure_accounts):
    fine = BillingFine.objects.create(
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

    approved = BillingAdjustmentService.approve_fine(fine_id=fine.id, approved_by=checker)
    due.refresh_from_db()
    entry = JournalEntry.objects.get(source_model="BillingFine", source_number=str(fine.id))

    assert approved.status == BillingFine.Status.APPROVED
    assert due.fine_amount == Decimal("200.00")
    assert due.balance_amount == Decimal("2700.00")
    debit_line = entry.lines.get(debit_amount=Decimal("200.00"))
    credit_line = entry.lines.get(credit_amount=Decimal("200.00"))
    assert debit_line.account.code == "1210"
    assert credit_line.account.code == "4400"


@pytest.mark.django_db
def test_adjustments_create_audit_logs(student, due, checker, configure_accounts):
    fine = BillingFine.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        fee_due=due,
        fine_type=BillingFine.FineType.LATE_FEE,
        amount=Decimal("100.00"),
        reason="Late fee",
        status=BillingFine.Status.PENDING_APPROVAL,
    )
    BillingAdjustmentService.approve_fine(fine_id=fine.id, approved_by=checker)

    assert AuditLog.objects.filter(
        module=AuditLog.Module.BILLING,
        action=AuditLog.Action.APPROVE,
        metadata__event="fine_approved",
    ).exists()
