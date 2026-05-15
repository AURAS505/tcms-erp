from datetime import date
from decimal import Decimal

import pytest

from accounting.models import JournalEntry
from accounting.reports import FinancialReportFilters, GeneralLedgerReportService
from accounting.tests.conftest import create_entry


@pytest.mark.django_db
def test_general_ledger_includes_posted_entries_only(organization, branch, academic_year, academic_period, accounts):
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
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="500.00",
        status=JournalEntry.Status.DRAFT,
    )

    ledger = GeneralLedgerReportService.get_account_ledger(
        filters=FinancialReportFilters(organization=organization, account=accounts["1110"]),
    )

    assert ledger.total_debit == Decimal("1000.00")
    assert len(ledger.transactions) == 1


@pytest.mark.django_db
def test_general_ledger_calculates_running_balance(organization, branch, academic_year, academic_period, accounts):
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

    ledger = GeneralLedgerReportService.get_account_ledger(
        filters=FinancialReportFilters(organization=organization, account=accounts["1110"]),
    )

    assert [txn.running_balance for txn in ledger.transactions] == [Decimal("1000.00"), Decimal("750.00")]
    assert ledger.closing_balance == Decimal("750.00")


@pytest.mark.django_db
def test_general_ledger_branch_academic_year_and_date_filters(
    organization, branch, other_branch, academic_year, academic_period, accounts
):
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
        branch=other_branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0002",
        entry_date_ad=date(2024, 7, 18),
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="500.00",
    )

    ledger = GeneralLedgerReportService.get_account_ledger(
        filters=FinancialReportFilters(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            date_from=date(2024, 7, 16),
            date_to=date(2024, 7, 16),
            account=accounts["1110"],
        ),
    )

    assert ledger.total_debit == Decimal("1000.00")
    assert len(ledger.transactions) == 1
