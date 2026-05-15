from datetime import date
from decimal import Decimal

import pytest

from accounting.reports import CashFlowReportService, FinancialReportFilters
from accounting.tests.conftest import create_entry


@pytest.mark.django_db
def test_cash_flow_summary_uses_cash_bank_wallet_accounts(organization, branch, academic_year, academic_period, accounts):
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
        credit_account=accounts["1120"],
        amount="250.00",
    )

    result = CashFlowReportService.get_cash_flow_summary(filters=FinancialReportFilters(organization=organization))

    assert result.inflows == Decimal("1000.00")
    assert result.outflows == Decimal("250.00")
    assert result.closing_balance == Decimal("750.00")
    assert {line.account_code for line in result.cash_accounts} == {"1110", "1120", "1130"}
