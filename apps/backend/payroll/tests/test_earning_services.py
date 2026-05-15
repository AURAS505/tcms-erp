from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum

from academic.models import AcademicPeriod, AcademicYear
from accounting.models import Account, JournalEntry
from common.models import AuditLog
from organizations.models import Branch, Organization
from payroll.models import TeacherEarning
from payroll.services import TeacherEarningService
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
    return get_user_model().objects.create_user(email="maker.earning@example.com", password="secure-password")


@pytest.fixture
def checker():
    return get_user_model().objects.create_user(email="checker.earning@example.com", password="secure-password")


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
def configure_accounts(organization):
    Account.objects.create(
        organization=organization,
        code="2110",
        name="Teacher Payable",
        account_type=Account.AccountType.LIABILITY,
        normal_balance=Account.NormalBalance.CREDIT,
    )
    Account.objects.create(
        organization=organization,
        code="5100",
        name="Teacher Salary Expense",
        account_type=Account.AccountType.EXPENSE,
        normal_balance=Account.NormalBalance.DEBIT,
    )


@pytest.mark.django_db
def test_create_approve_post_teacher_earning(organization, branch, academic_year, academic_period, teacher, maker, checker, configure_accounts):
    earning = TeacherEarningService.create_manual_earning(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        teacher=teacher,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("1000.00"),
        deduction_amount=Decimal("100.00"),
        created_by=maker,
    )
    assert earning.status == TeacherEarning.Status.DRAFT

    approved = TeacherEarningService.approve_earning(earning_id=earning.id, approved_by=checker)
    assert approved.status == TeacherEarning.Status.APPROVED

    posted = TeacherEarningService.post_earning(earning_id=earning.id, posted_by=checker)
    entry = JournalEntry.objects.get(source_model="TeacherEarning", source_object_id=earning.id)
    totals = entry.lines.aggregate(
        debit_total=Sum("debit_amount", default=Decimal("0.00")),
        credit_total=Sum("credit_amount", default=Decimal("0.00")),
    )
    debit_line = entry.lines.get(debit_amount=Decimal("900.00"))
    credit_line = entry.lines.get(credit_amount=Decimal("900.00"))

    assert posted.status == TeacherEarning.Status.POSTED
    assert totals["debit_total"] == totals["credit_total"] == Decimal("900.00")
    assert debit_line.account.code == "5100"
    assert credit_line.account.code == "2110"


@pytest.mark.django_db
def test_missing_account_configuration_raises_error(organization, branch, academic_year, teacher, maker, checker):
    earning = TeacherEarningService.create_manual_earning(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("1000.00"),
        deduction_amount=Decimal("100.00"),
        created_by=maker,
    )
    TeacherEarningService.approve_earning(earning_id=earning.id, approved_by=checker)
    with pytest.raises(ValidationError):
        TeacherEarningService.post_earning(earning_id=earning.id, posted_by=checker)


@pytest.mark.django_db
def test_maker_checker_blocks_self_approval(organization, branch, academic_year, teacher, maker):
    earning = TeacherEarningService.create_manual_earning(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("500.00"),
        deduction_amount=Decimal("0.00"),
        created_by=maker,
    )
    with pytest.raises(ValidationError):
        TeacherEarningService.approve_earning(earning_id=earning.id, approved_by=maker)


@pytest.mark.django_db
def test_audit_log_created_for_earning_post(organization, branch, academic_year, teacher, maker, checker, configure_accounts):
    earning = TeacherEarningService.create_manual_earning(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("600.00"),
        deduction_amount=Decimal("0.00"),
        created_by=maker,
    )
    TeacherEarningService.approve_earning(earning_id=earning.id, approved_by=checker)
    TeacherEarningService.post_earning(earning_id=earning.id, posted_by=checker)
    assert AuditLog.objects.filter(
        module=AuditLog.Module.PAYROLL,
        action=AuditLog.Action.POST,
        metadata__event="teacher_earning_posted",
    ).exists()
