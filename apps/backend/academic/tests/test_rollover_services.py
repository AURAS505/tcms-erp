from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from academic.models import AcademicYear, AcademicYearRollover
from academic.services import AcademicYearRolloverService
from accounting.models import Account, JournalEntry, JournalEntryLine
from accounting.services import AccountingPostingService
from common.models import AuditLog
from organizations.models import Organization


@pytest.fixture
def organization():
    return Organization.objects.create(legal_name="Auras Education Pvt. Ltd.", display_name="Auras Education")


@pytest.fixture
def user():
    return get_user_model().objects.create_user(email="rollover@example.com", password="secure-password")


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
    specs = [
        ("1110", "Cash in Hand", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1120", "Bank Account", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("3200", "Retained Earnings", Account.AccountType.EQUITY, Account.NormalBalance.CREDIT),
        ("3300", "Income Summary", Account.AccountType.EQUITY, Account.NormalBalance.CREDIT),
        ("4100", "Tuition Fee Revenue", Account.AccountType.REVENUE, Account.NormalBalance.CREDIT),
        ("5100", "Teacher Salary Expense", Account.AccountType.EXPENSE, Account.NormalBalance.DEBIT),
    ]
    return {
        code: Account.objects.create(
            organization=organization,
            code=code,
            name=name,
            account_type=account_type,
            normal_balance=normal_balance,
            is_system_account=True,
        )
        for code, name, account_type, normal_balance in specs
    }


def post_entry(*, organization, academic_year, entry_number, debit_account, credit_account, amount):
    entry = JournalEntry.objects.create(
        organization=organization,
        academic_year=academic_year,
        entry_number=entry_number,
        entry_date_ad=date(2024, 7, 16),
        entry_date_bs="2081-04-01",
        description=entry_number,
        status=JournalEntry.Status.APPROVED,
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=organization,
        account=debit_account,
        debit_amount=Decimal(amount),
        credit_amount=Decimal("0.00"),
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=organization,
        account=credit_account,
        debit_amount=Decimal("0.00"),
        credit_amount=Decimal(amount),
    )
    return AccountingPostingService.post_journal_entry(entry)


def new_year_data():
    return {
        "name": "2082/2083",
        "bs_start_year": 2082,
        "bs_end_year": 2083,
        "bs_start_date": "2082-01-01",
        "bs_end_date": "2082-12-30",
        "ad_start_date": date(2025, 4, 14),
        "ad_end_date": date(2026, 4, 13),
    }


@pytest.mark.django_db
def test_prepare_rollover_record(organization, academic_year, user):
    rollover = AcademicYearRolloverService.prepare_rollover(
        organization=organization,
        from_academic_year=academic_year,
        prepared_by=user,
    )

    assert rollover.status == AcademicYearRollover.Status.DRAFT
    assert AuditLog.objects.filter(metadata__event="academic_year_rollover_prepared").exists()


@pytest.mark.django_db
def test_validate_balanced_trial_balance(organization, academic_year, accounts, user):
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0001",
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="1000.00",
    )
    rollover = AcademicYearRolloverService.prepare_rollover(organization=organization, from_academic_year=academic_year)

    validated = AcademicYearRolloverService.validate_rollover(rollover_id=rollover.id, validated_by=user)

    assert validated.trial_balance_validated is True
    assert validated.status == AcademicYearRollover.Status.READY


@pytest.mark.django_db
def test_reject_unbalanced_trial_balance_if_forced(organization, academic_year, accounts):
    entry = JournalEntry.objects.create(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-BAD",
        entry_date_ad=date(2024, 7, 16),
        entry_date_bs="2081-04-01",
        description="Bad data",
        status=JournalEntry.Status.POSTED,
    )
    debit = JournalEntryLine(
        journal_entry=entry,
        organization=organization,
        account=accounts["1110"],
        debit_amount=Decimal("100.00"),
        credit_amount=Decimal("0.00"),
    )
    debit._allow_immutable_update = True
    debit.save()
    credit = JournalEntryLine(
        journal_entry=entry,
        organization=organization,
        account=accounts["4100"],
        debit_amount=Decimal("0.00"),
        credit_amount=Decimal("90.00"),
    )
    credit._allow_immutable_update = True
    credit.save()
    rollover = AcademicYearRolloverService.prepare_rollover(organization=organization, from_academic_year=academic_year)

    with pytest.raises(ValidationError):
        AcademicYearRolloverService.validate_rollover(rollover_id=rollover.id)


@pytest.mark.django_db
def test_reject_when_income_summary_or_retained_earnings_missing(organization, academic_year):
    Account.objects.create(
        organization=organization,
        code="3300",
        name="Income Summary",
        account_type=Account.AccountType.EQUITY,
        normal_balance=Account.NormalBalance.CREDIT,
    )
    rollover = AcademicYearRolloverService.prepare_rollover(organization=organization, from_academic_year=academic_year)
    with pytest.raises(ValidationError):
        AcademicYearRolloverService.validate_rollover(rollover_id=rollover.id)


@pytest.mark.django_db
def test_execute_rollover_posts_closing_opening_and_updates_years(organization, academic_year, accounts, user):
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0001",
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="1000.00",
    )
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0002",
        debit_account=accounts["5100"],
        credit_account=accounts["1110"],
        amount="250.00",
    )
    rollover = AcademicYearRolloverService.prepare_rollover(organization=organization, from_academic_year=academic_year)
    AcademicYearRolloverService.validate_rollover(rollover_id=rollover.id, validated_by=user)

    executed = AcademicYearRolloverService.execute_rollover(
        rollover_id=rollover.id,
        executed_by=user,
        new_year_data=new_year_data(),
    )

    academic_year.refresh_from_db()
    assert executed.status == AcademicYearRollover.Status.EXECUTED
    assert executed.revenue_expense_closing_completed is True
    assert executed.opening_balances_posted is True
    assert academic_year.status == AcademicYear.Status.HARD_CLOSED
    assert AcademicYear.objects.get(name="2082/2083").is_active is True
    assert JournalEntry.objects.filter(source_number__startswith="closing", status=JournalEntry.Status.POSTED).exists()
    assert JournalEntry.objects.filter(source_number="opening-balances", academic_year=executed.to_academic_year).exists()


@pytest.mark.django_db
def test_revenue_expense_do_not_carry_forward_and_balance_sheet_accounts_do(organization, academic_year, accounts, user):
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0001",
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="1000.00",
    )
    rollover = AcademicYearRolloverService.prepare_rollover(organization=organization, from_academic_year=academic_year)
    AcademicYearRolloverService.validate_rollover(rollover_id=rollover.id)
    executed = AcademicYearRolloverService.execute_rollover(
        rollover_id=rollover.id,
        executed_by=user,
        new_year_data=new_year_data(),
        hard_close=False,
    )
    opening = JournalEntry.objects.get(source_number="opening-balances", academic_year=executed.to_academic_year)
    carried_codes = set(opening.lines.values_list("account__code", flat=True))

    assert "1110" in carried_codes
    assert "3200" in carried_codes
    assert "4100" not in carried_codes
    assert "5100" not in carried_codes


@pytest.mark.django_db
def test_hard_closed_year_blocks_future_posting(organization, academic_year, accounts, user):
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0001",
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="100.00",
    )
    rollover = AcademicYearRolloverService.prepare_rollover(organization=organization, from_academic_year=academic_year)
    AcademicYearRolloverService.validate_rollover(rollover_id=rollover.id)
    AcademicYearRolloverService.execute_rollover(rollover_id=rollover.id, executed_by=user, new_year_data=new_year_data())
    entry = JournalEntry.objects.create(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-LATE",
        entry_date_ad=date(2025, 1, 1),
        entry_date_bs="2081-09-17",
        description="Late",
        status=JournalEntry.Status.APPROVED,
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=organization,
        account=accounts["1110"],
        debit_amount=Decimal("10.00"),
        credit_amount=Decimal("0.00"),
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=organization,
        account=accounts["4100"],
        debit_amount=Decimal("0.00"),
        credit_amount=Decimal("10.00"),
    )

    with pytest.raises(ValidationError):
        AccountingPostingService.post_journal_entry(entry)


@pytest.mark.django_db
def test_audit_logs_created_for_rollover_execution(organization, academic_year, accounts, user):
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0001",
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="100.00",
    )
    rollover = AcademicYearRolloverService.prepare_rollover(organization=organization, from_academic_year=academic_year)
    AcademicYearRolloverService.validate_rollover(rollover_id=rollover.id)
    AcademicYearRolloverService.execute_rollover(rollover_id=rollover.id, executed_by=user, new_year_data=new_year_data())

    assert AuditLog.objects.filter(metadata__event="academic_year_closing_entries_posted").exists()
    assert AuditLog.objects.filter(metadata__event="academic_year_opening_entries_posted").exists()
    assert AuditLog.objects.filter(metadata__event="academic_year_rollover_executed").exists()
