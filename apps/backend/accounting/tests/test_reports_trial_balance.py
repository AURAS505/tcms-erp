from datetime import date
from decimal import Decimal

import pytest

from accounting.models import JournalEntry, JournalEntryLine
from accounting.reports import FinancialReportFilters, TrialBalanceReportService
from accounting.tests.conftest import create_entry


@pytest.mark.django_db
def test_trial_balance_balances_after_balanced_journal_entries(organization, branch, academic_year, academic_period, accounts):
    create_entry(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0001",
        entry_date_ad=date(2024, 7, 16),
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="1000.00",
    )
    create_entry(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0002",
        entry_date_ad=date(2024, 7, 17),
        debit_account=accounts["5100"],
        credit_account=accounts["1110"],
        amount="250.00",
    )

    result = TrialBalanceReportService.get_trial_balance(filters=FinancialReportFilters(organization=organization))

    assert result.is_balanced is True
    assert result.total_debit == result.total_credit == Decimal("1000.00")


@pytest.mark.django_db
def test_trial_balance_detects_imbalance_when_forced(organization, branch, academic_year, accounts):
    entry = JournalEntry.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        entry_number="JV-BAD",
        entry_date_ad=date(2024, 7, 16),
        entry_date_bs="2081-04-01",
        description="Forced bad data",
        status=JournalEntry.Status.POSTED,
    )
    debit_line = JournalEntryLine(
        journal_entry=entry,
        organization=organization,
        branch=branch,
        account=accounts["1110"],
        debit_amount=Decimal("100.00"),
        credit_amount=Decimal("0.00"),
    )
    debit_line._allow_immutable_update = True
    debit_line.save()
    credit_line = JournalEntryLine(
        journal_entry=entry,
        organization=organization,
        branch=branch,
        account=accounts["4100"],
        debit_amount=Decimal("0.00"),
        credit_amount=Decimal("90.00"),
    )
    credit_line._allow_immutable_update = True
    credit_line.save()

    result = TrialBalanceReportService.get_trial_balance(filters=FinancialReportFilters(organization=organization))

    assert result.is_balanced is False
    assert result.difference == Decimal("10.00")
