from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicPeriod, AcademicYear, AcademicYearRollover
from accounts.models import Role, UserBranchAssignment, UserRole
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
def accounts(organization):
    specs = [
        ("1110", "Cash in Hand", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
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


def user_with_role(role_code, *, branch=None, email_prefix=None):
    user = get_user_model().objects.create_user(
        email=f"{email_prefix or role_code}@example.com",
        password="secure-password",
    )
    role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role.RoleCode(role_code).label})
    UserRole.objects.create(user=user, role=role)
    if branch:
        UserBranchAssignment.objects.create(user=user, organization_id=branch.organization_id, branch_id=branch.id)
    return user


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def prepare_payload(organization, academic_year):
    return {
        "organization": str(organization.id),
        "from_academic_year": str(academic_year.id),
        "notes": "Year end rollover",
    }


def new_year_payload():
    return {
        "new_year_data": {
            "name": "2082/2083",
            "bs_start_year": 2082,
            "bs_end_year": 2083,
            "bs_start_date": "2082-01-01",
            "bs_end_date": "2082-12-30",
            "ad_start_date": "2025-04-14",
            "ad_end_date": "2026-04-13",
        },
        "hard_close": True,
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


@pytest.mark.django_db
def test_unauthenticated_user_cannot_prepare_rollover(organization, academic_year):
    response = APIClient().post("/api/v1/academic-year-rollovers/prepare/", prepare_payload(organization, academic_year), format="json")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
@pytest.mark.parametrize("role_code", [Role.RoleCode.RECEPTIONIST, Role.RoleCode.TEACHER, Role.RoleCode.AUDITOR])
def test_non_financial_roles_cannot_prepare_rollover(organization, academic_year, role_code):
    user = user_with_role(role_code)

    response = client_for(user).post("/api/v1/academic-year-rollovers/prepare/", prepare_payload(organization, academic_year), format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_branch_scoped_accountant_cannot_prepare_org_rollover(organization, branch, academic_year):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)

    response = client_for(accountant).post(
        "/api/v1/academic-year-rollovers/prepare/",
        prepare_payload(organization, academic_year),
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_accountant_can_prepare_and_validate_rollover(organization, academic_year, accounts):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, email_prefix="rollover-accountant")
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0001",
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="1000.00",
    )
    prepare_response = client_for(accountant).post(
        "/api/v1/academic-year-rollovers/prepare/",
        prepare_payload(organization, academic_year),
        format="json",
    )

    validate_response = client_for(accountant).post(
        f"/api/v1/academic-year-rollovers/{prepare_response.json()['data']['id']}/validate/",
        {},
        format="json",
    )

    assert prepare_response.status_code == 201
    assert validate_response.status_code == 200
    assert validate_response.json()["data"]["status"] == AcademicYearRollover.Status.READY
    assert validate_response.json()["data"]["trial_balance_validated"] is True


@pytest.mark.django_db
def test_execute_endpoint_posts_closing_and_opening_entries(organization, academic_year, accounts):
    super_admin = user_with_role(Role.RoleCode.SUPER_ADMIN, email_prefix="rollover-super")
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0001",
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="1000.00",
    )
    prepare_response = client_for(super_admin).post(
        "/api/v1/academic-year-rollovers/prepare/",
        prepare_payload(organization, academic_year),
        format="json",
    )
    rollover_id = prepare_response.json()["data"]["id"]
    client_for(super_admin).post(f"/api/v1/academic-year-rollovers/{rollover_id}/validate/", {}, format="json")

    execute_response = client_for(super_admin).post(
        f"/api/v1/academic-year-rollovers/{rollover_id}/execute/",
        new_year_payload(),
        format="json",
    )

    academic_year.refresh_from_db()
    assert execute_response.status_code == 200
    assert execute_response.json()["data"]["status"] == AcademicYearRollover.Status.EXECUTED
    assert academic_year.status == AcademicYear.Status.HARD_CLOSED
    assert JournalEntry.objects.filter(source_number__startswith="closing", status=JournalEntry.Status.POSTED).exists()
    assert JournalEntry.objects.filter(source_number="opening-balances", status=JournalEntry.Status.POSTED).exists()


@pytest.mark.django_db
def test_execute_endpoint_enforces_trial_balance_validation(organization, academic_year, accounts):
    super_admin = user_with_role(Role.RoleCode.SUPER_ADMIN, email_prefix="rollover-bad-super")
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
    prepare_response = client_for(super_admin).post(
        "/api/v1/academic-year-rollovers/prepare/",
        prepare_payload(organization, academic_year),
        format="json",
    )

    response = client_for(super_admin).post(
        f"/api/v1/academic-year-rollovers/{prepare_response.json()['data']['id']}/execute/",
        new_year_payload(),
        format="json",
    )

    assert response.status_code == 400
    assert "trial balance" in str(response.json()["errors"]).lower()


@pytest.mark.django_db
def test_cancel_endpoint_works_for_draft_rollover(organization, academic_year):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, email_prefix="rollover-cancel-accountant")
    prepare_response = client_for(accountant).post(
        "/api/v1/academic-year-rollovers/prepare/",
        prepare_payload(organization, academic_year),
        format="json",
    )

    response = client_for(accountant).post(
        f"/api/v1/academic-year-rollovers/{prepare_response.json()['data']['id']}/cancel/",
        {"reason": "Not ready"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == AcademicYearRollover.Status.CANCELLED


@pytest.mark.django_db
def test_summary_endpoint_returns_rollover_state(organization, academic_year):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, email_prefix="rollover-summary-accountant")
    prepare_response = client_for(accountant).post(
        "/api/v1/academic-year-rollovers/prepare/",
        prepare_payload(organization, academic_year),
        format="json",
    )

    response = client_for(accountant).get(f"/api/v1/academic-year-rollovers/{prepare_response.json()['data']['id']}/summary/")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == AcademicYearRollover.Status.DRAFT


@pytest.mark.django_db
def test_executed_rollover_cannot_be_patched(organization, academic_year, accounts):
    super_admin = user_with_role(Role.RoleCode.SUPER_ADMIN, email_prefix="rollover-patch-super")
    post_entry(
        organization=organization,
        academic_year=academic_year,
        entry_number="JV-0001",
        debit_account=accounts["1110"],
        credit_account=accounts["4100"],
        amount="100.00",
    )
    prepare_response = client_for(super_admin).post(
        "/api/v1/academic-year-rollovers/prepare/",
        prepare_payload(organization, academic_year),
        format="json",
    )
    rollover_id = prepare_response.json()["data"]["id"]
    client_for(super_admin).post(f"/api/v1/academic-year-rollovers/{rollover_id}/validate/", {}, format="json")
    client_for(super_admin).post(f"/api/v1/academic-year-rollovers/{rollover_id}/execute/", new_year_payload(), format="json")

    response = client_for(super_admin).patch(f"/api/v1/academic-year-rollovers/{rollover_id}/", {"notes": "changed"}, format="json")

    assert response.status_code == 405


@pytest.mark.django_db
def test_hard_close_restricted_to_super_admin_or_owner(organization, academic_year):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, email_prefix="hard-close-accountant")
    super_admin = user_with_role(Role.RoleCode.SUPER_ADMIN, email_prefix="hard-close-super")

    denied = client_for(accountant).post(f"/api/v1/academic-years/{academic_year.id}/hard-close/", {}, format="json")
    allowed = client_for(super_admin).post(f"/api/v1/academic-years/{academic_year.id}/hard-close/", {}, format="json")

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["data"]["status"] == AcademicYear.Status.HARD_CLOSED


@pytest.mark.django_db
def test_hard_closed_year_blocks_future_posting_through_accounting_service(organization, academic_year, accounts):
    super_admin = user_with_role(Role.RoleCode.SUPER_ADMIN, email_prefix="hard-close-post-super")
    response = client_for(super_admin).post(f"/api/v1/academic-years/{academic_year.id}/hard-close/", {}, format="json")
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

    assert response.status_code == 200
    with pytest.raises(Exception, match="hard-closed academic year"):
        AccountingPostingService.post_journal_entry(entry)
