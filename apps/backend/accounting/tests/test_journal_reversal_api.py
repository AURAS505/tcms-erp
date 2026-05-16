from decimal import Decimal

import pytest

from accounting.models import JournalEntry
from accounting.reports import FinancialReportFilters, GeneralLedgerReportService
from common.models import AuditLog

from .test_journal_mutation_api import client_for, journal_payload, user_with_role
from accounts.models import Role


@pytest.mark.django_db
def test_reversal_creates_opposite_posted_journal_and_references_original(
    organization, branch, academic_year, academic_period, accounts
):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="reverse-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="reverse-checker")
    create_response = client_for(maker).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )
    journal_id = create_response.json()["data"]["id"]
    client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/approve/", {}, format="json")
    client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/post/", {}, format="json")

    response = client_for(checker).post(
        f"/api/v1/journal-entries/{journal_id}/reverse/",
        {"reversal_date_ad": "2024-07-21", "narration": "Correcting reversal"},
        format="json",
    )

    original = JournalEntry.objects.get(id=journal_id)
    reversal = JournalEntry.objects.get(id=response.json()["data"]["id"])
    original_debit_line = original.lines.get(debit_amount=Decimal("1000.00"))
    original_credit_line = original.lines.get(credit_amount=Decimal("1000.00"))
    reversal_cash_line = reversal.lines.get(account=original_debit_line.account)
    reversal_capital_line = reversal.lines.get(account=original_credit_line.account)
    ledger = GeneralLedgerReportService.get_account_ledger(
        filters=FinancialReportFilters(organization=organization, account=accounts["1110"]),
    )

    assert response.status_code == 201
    assert reversal.status == JournalEntry.Status.POSTED
    assert reversal.source_type == JournalEntry.SourceType.REVERSAL
    assert reversal.reversed_entry_id == original.id
    assert original.status == JournalEntry.Status.POSTED
    assert reversal_cash_line.credit_amount == Decimal("1000.00")
    assert reversal_capital_line.debit_amount == Decimal("1000.00")
    assert ledger.total_debit == Decimal("1000.00")
    assert ledger.total_credit == Decimal("1000.00")
    assert ledger.closing_balance == Decimal("0.00")
    assert AuditLog.objects.filter(metadata__event="journal_entry_reversed", object_id=str(original.id)).exists()


@pytest.mark.django_db
def test_only_posted_journals_can_be_reversed(organization, branch, academic_year, academic_period, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="reverse-draft-maker")
    create_response = client_for(maker).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )
    journal_id = create_response.json()["data"]["id"]

    response = client_for(maker).post(f"/api/v1/journal-entries/{journal_id}/reverse/", {}, format="json")

    assert response.status_code == 400
    assert "only posted" in str(response.json()["errors"]).lower()


@pytest.mark.django_db
def test_original_creator_cannot_reverse_own_posted_journal(organization, branch, academic_year, academic_period, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="reverse-self-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="reverse-self-checker")
    create_response = client_for(maker).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )
    journal_id = create_response.json()["data"]["id"]
    client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/approve/", {}, format="json")
    client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/post/", {}, format="json")

    response = client_for(maker).post(f"/api/v1/journal-entries/{journal_id}/reverse/", {}, format="json")

    assert response.status_code == 400
    assert "maker-checker" in str(response.json()["errors"]).lower()
