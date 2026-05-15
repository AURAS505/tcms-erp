from datetime import date
from decimal import Decimal

import pytest

from academic.models import AcademicPeriod, AcademicYear
from accounting.models import Account, JournalEntry, JournalEntryLine
from accounting.services import AccountingPostingService
from organizations.models import Branch, Organization


@pytest.fixture
def organization():
    return Organization.objects.create(legal_name="Auras Education Pvt. Ltd.", display_name="Auras Education")


@pytest.fixture
def branch(organization):
    return Branch.objects.create(organization=organization, code="MAIN", name="Main Branch", is_main_branch=True)


@pytest.fixture
def other_branch(organization):
    return Branch.objects.create(organization=organization, code="B2", name="Second Branch")


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
        bs_end_date="2081-04-31",
        ad_start_date=date(2024, 7, 16),
        ad_end_date=date(2024, 8, 15),
    )


@pytest.fixture
def accounts(organization):
    specs = [
        ("1110", "Cash in Hand", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1120", "Bank Account", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1130", "Online Wallet", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1210", "Student Receivables", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("2110", "Teacher Payables", Account.AccountType.LIABILITY, Account.NormalBalance.CREDIT),
        ("3100", "Owner Capital", Account.AccountType.EQUITY, Account.NormalBalance.CREDIT),
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
        )
        for code, name, account_type, normal_balance in specs
    }


def create_entry(
    *,
    organization,
    branch,
    academic_year,
    academic_period=None,
    entry_number,
    entry_date_ad,
    debit_account,
    credit_account,
    amount,
    status=JournalEntry.Status.POSTED,
):
    entry = JournalEntry.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number=entry_number,
        entry_date_ad=entry_date_ad,
        entry_date_bs="2081-04-01",
        description=f"Entry {entry_number}",
        status=JournalEntry.Status.APPROVED if status == JournalEntry.Status.POSTED else status,
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=organization,
        branch=branch,
        account=debit_account,
        debit_amount=Decimal(amount),
        credit_amount=Decimal("0.00"),
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=organization,
        branch=branch,
        account=credit_account,
        debit_amount=Decimal("0.00"),
        credit_amount=Decimal(amount),
    )
    if status == JournalEntry.Status.POSTED:
        entry = AccountingPostingService.post_journal_entry(entry)
    return entry
