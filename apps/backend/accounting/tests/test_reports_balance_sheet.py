from datetime import date
from decimal import Decimal

import pytest

from accounting.reports import BalanceSheetReportService, FinancialReportFilters
from accounting.tests.conftest import create_entry


@pytest.mark.django_db
def test_balance_sheet_calculates_assets_liabilities_equity_and_current_profit(
    organization, branch, academic_year, academic_period, accounts
):
    create_entry(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0001",
        entry_date_ad=date(2024, 7, 16),
        debit_account=accounts["1110"],
        credit_account=accounts["3100"],
        amount="500.00",
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
        amount="1000.00",
    )
    create_entry(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0003",
        entry_date_ad=date(2024, 7, 18),
        debit_account=accounts["5100"],
        credit_account=accounts["1110"],
        amount="250.00",
    )

    result = BalanceSheetReportService.get_balance_sheet(filters=FinancialReportFilters(organization=organization))

    assert result.current_year_profit_loss == Decimal("750.00")
    assert result.total_assets == Decimal("1250.00")
    assert result.total_equity == Decimal("1250.00")
    assert result.is_balanced is True
