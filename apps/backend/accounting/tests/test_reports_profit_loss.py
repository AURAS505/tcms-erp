from datetime import date
from decimal import Decimal

import pytest

from accounting.reports import FinancialReportFilters, ProfitLossReportService
from accounting.tests.conftest import create_entry


@pytest.mark.django_db
def test_profit_and_loss_calculates_revenue_and_expenses(organization, branch, academic_year, academic_period, accounts):
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

    result = ProfitLossReportService.get_profit_and_loss(filters=FinancialReportFilters(organization=organization))

    assert result.total_revenue == Decimal("1000.00")
    assert result.total_expenses == Decimal("250.00")
    assert result.net_profit_loss == Decimal("750.00")
