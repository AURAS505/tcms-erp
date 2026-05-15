from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

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
def debit_account(organization):
    return Account.objects.create(
        organization=organization,
        code="1110",
        name="Cash in Hand",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
    )


@pytest.fixture
def credit_account(organization):
    return Account.objects.create(
        organization=organization,
        code="4100",
        name="Tuition Fee Revenue",
        account_type=Account.AccountType.REVENUE,
        normal_balance=Account.NormalBalance.CREDIT,
    )


@pytest.fixture
def journal_entry(organization, branch, academic_year, academic_period):
    return JournalEntry.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0002",
        entry_date_ad=date(2024, 7, 16),
        entry_date_bs="2081-04-01",
        description="Service test journal",
    )


def add_line(entry, account, *, debit="0.00", credit="0.00"):
    return JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=entry.organization,
        branch=entry.branch,
        account=account,
        debit_amount=Decimal(debit),
        credit_amount=Decimal(credit),
    )


@pytest.mark.django_db
def test_validate_balanced_journal_entry(journal_entry, debit_account, credit_account):
    add_line(journal_entry, debit_account, debit="100.00")
    add_line(journal_entry, credit_account, credit="100.00")

    debit_total, credit_total = AccountingPostingService.validate_balanced(journal_entry)

    assert debit_total == Decimal("100.00")
    assert credit_total == Decimal("100.00")


@pytest.mark.django_db
def test_reject_unbalanced_journal_entry_posting(journal_entry, debit_account, credit_account):
    add_line(journal_entry, debit_account, debit="100.00")
    add_line(journal_entry, credit_account, credit="90.00")

    with pytest.raises(ValidationError):
        AccountingPostingService.post_journal_entry(journal_entry)


@pytest.mark.django_db
def test_post_balanced_journal_entry(journal_entry, debit_account, credit_account):
    add_line(journal_entry, debit_account, debit="100.00")
    add_line(journal_entry, credit_account, credit="100.00")

    posted = AccountingPostingService.post_journal_entry(journal_entry)

    assert posted.status == JournalEntry.Status.POSTED
    assert posted.posted_at is not None
    assert posted.posting_date_ad is not None


@pytest.mark.django_db
def test_reject_journal_entry_with_less_than_two_lines(journal_entry, debit_account):
    add_line(journal_entry, debit_account, debit="100.00")

    with pytest.raises(ValidationError):
        AccountingPostingService.post_journal_entry(journal_entry)


@pytest.mark.django_db
def test_block_posting_to_hard_closed_academic_year(journal_entry, academic_year, debit_account, credit_account):
    add_line(journal_entry, debit_account, debit="100.00")
    add_line(journal_entry, credit_account, credit="100.00")
    academic_year.status = AcademicYear.Status.HARD_CLOSED
    academic_year.save(update_fields=["status"])

    with pytest.raises(ValidationError):
        AccountingPostingService.post_journal_entry(journal_entry)


@pytest.mark.django_db
def test_block_posting_to_hard_closed_academic_period(journal_entry, academic_period, debit_account, credit_account):
    add_line(journal_entry, debit_account, debit="100.00")
    add_line(journal_entry, credit_account, credit="100.00")
    academic_period.status = AcademicPeriod.Status.HARD_CLOSED
    academic_period.save(update_fields=["status"])

    with pytest.raises(ValidationError):
        AccountingPostingService.post_journal_entry(journal_entry)
