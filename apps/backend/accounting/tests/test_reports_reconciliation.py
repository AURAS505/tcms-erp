from datetime import date
from decimal import Decimal

import pytest

from accounting.reports import FinancialReportFilters, ReconciliationReportService
from accounting.tests.conftest import create_entry
from billing.models import BillStatus, StudentFeeDue
from payroll.models import TeacherEarning
from students.models import Student
from teachers.models import Teacher


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
def teacher(organization, branch):
    return Teacher.objects.create(
        organization=organization,
        branch=branch,
        employee_number="T-001",
        full_name="Ram Sir",
        phone="9800000000",
        status=Teacher.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_reconciliation_returns_billing_receivable_comparison(
    organization, branch, academic_year, academic_period, accounts, student
):
    StudentFeeDue.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        student=student,
        period_label="Shrawan 2081",
        original_amount=Decimal("1000.00"),
        net_amount=Decimal("1000.00"),
        balance_amount=Decimal("1000.00"),
        status=BillStatus.UNPAID,
    )
    create_entry(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0001",
        entry_date_ad=date(2024, 7, 16),
        debit_account=accounts["1210"],
        credit_account=accounts["4100"],
        amount="1000.00",
    )

    result = ReconciliationReportService.compare_billing_receivables_to_ledger(
        filters=FinancialReportFilters(organization=organization, academic_year=academic_year),
    )

    assert result.ledger_balance == Decimal("1000.00")
    assert result.operational_balance == Decimal("1000.00")
    assert result.is_reconciled is True


@pytest.mark.django_db
def test_reconciliation_returns_teacher_payable_comparison(
    organization, branch, academic_year, academic_period, accounts, teacher
):
    TeacherEarning.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        teacher=teacher,
        earning_source=TeacherEarning.EarningSource.MANUAL_ADJUSTMENT,
        earning_date_ad=date(2024, 7, 16),
        gross_amount=Decimal("500.00"),
        net_amount=Decimal("500.00"),
        balance_amount=Decimal("500.00"),
        status=TeacherEarning.Status.POSTED,
    )
    create_entry(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0001",
        entry_date_ad=date(2024, 7, 16),
        debit_account=accounts["5100"],
        credit_account=accounts["2110"],
        amount="500.00",
    )

    result = ReconciliationReportService.compare_teacher_payables_to_ledger(
        filters=FinancialReportFilters(organization=organization, academic_year=academic_year),
    )

    assert result.ledger_balance == Decimal("500.00")
    assert result.operational_balance == Decimal("500.00")
    assert result.is_reconciled is True
