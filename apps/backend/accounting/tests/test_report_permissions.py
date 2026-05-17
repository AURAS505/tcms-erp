from datetime import date
from decimal import Decimal

import pytest

from accounts.models import Role
from accounting.tests.conftest import create_entry
from accounting.tests.test_journal_mutation_api import client_for, user_with_role


@pytest.mark.django_db
def test_branch_scoped_report_defaults_to_only_assigned_branch(
    organization, branch, other_branch, academic_year, academic_period, accounts
):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="report-branch-accountant")
    create_entry(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-BRANCH",
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
        entry_number="JV-OTHER-BRANCH",
        entry_date_ad=date(2024, 7, 16),
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="500.00",
    )

    response = client_for(accountant).get(f"/api/v1/reports/trial-balance/?organization={organization.id}")

    assert response.status_code == 200
    assert Decimal(str(response.json()["data"]["total_debit"])) == Decimal("1000.00")
    assert Decimal(str(response.json()["data"]["total_credit"])) == Decimal("1000.00")


@pytest.mark.django_db
def test_branch_scoped_report_cannot_request_unassigned_branch(
    organization, branch, other_branch, academic_year, academic_period, accounts
):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="report-denied-accountant")

    response = client_for(accountant).get(
        f"/api/v1/reports/trial-balance/?organization={organization.id}&branch={other_branch.id}"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_branch_scoped_report_denies_user_without_branch_assignment(organization):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, email_prefix="report-no-branch-accountant")

    response = client_for(accountant).get(f"/api/v1/reports/trial-balance/?organization={organization.id}")

    assert response.status_code == 403
