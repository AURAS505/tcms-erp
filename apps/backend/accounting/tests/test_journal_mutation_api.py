from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicYear
from accounts.models import Role, UserBranchAssignment, UserRole
from accounting.models import AccountingDocument, JournalEntry
from accounting.reports import FinancialReportFilters, GeneralLedgerReportService
from common.models import AuditLog


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


def journal_payload(organization, branch, academic_year, academic_period, accounts, *, debit="1000.00", credit="1000.00"):
    return {
        "organization": str(organization.id),
        "branch": str(branch.id),
        "academic_year": str(academic_year.id),
        "academic_period": str(academic_period.id),
        "entry_date_ad": "2024-07-20",
        "entry_date_bs": "2081-04-05",
        "description": "Manual cash adjustment",
        "narration": "Opening correction",
        "lines": [
            {
                "account": str(accounts["1110"].id),
                "description": "Cash debit",
                "debit_amount": debit,
                "credit_amount": "0.00",
            },
            {
                "account": str(accounts["3100"].id),
                "description": "Capital credit",
                "debit_amount": "0.00",
                "credit_amount": credit,
            },
        ],
    }


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_manual_journal(organization, branch, academic_year, academic_period, accounts):
    response = APIClient().post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )

    assert response.status_code in {401, 403}


@pytest.mark.django_db
@pytest.mark.parametrize("role_code", [Role.RoleCode.RECEPTIONIST, Role.RoleCode.TEACHER, Role.RoleCode.AUDITOR])
def test_non_financial_roles_cannot_create_manual_journal(
    organization, branch, academic_year, academic_period, accounts, role_code
):
    user = user_with_role(role_code, branch=branch)

    response = client_for(user).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_accountant_can_create_balanced_draft_journal_in_assigned_branch(
    organization, branch, academic_year, academic_period, accounts
):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)

    response = client_for(accountant).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )

    journal = JournalEntry.objects.get(id=response.json()["data"]["id"])
    ledger = GeneralLedgerReportService.get_account_ledger(
        filters=FinancialReportFilters(organization=organization, account=accounts["1110"]),
    )

    assert response.status_code == 201
    assert response.json()["data"]["status"] == JournalEntry.Status.DRAFT
    assert journal.lines.count() == 2
    assert ledger.total_debit == Decimal("0.00")
    assert AuditLog.objects.filter(metadata__event="manual_journal_created", object_id=str(journal.id)).exists()


@pytest.mark.django_db
def test_accountant_cannot_create_manual_journal_for_unassigned_branch(
    organization, branch, other_branch, academic_year, academic_period, accounts
):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)
    payload = journal_payload(organization, other_branch, academic_year, academic_period, accounts)

    response = client_for(accountant).post("/api/v1/journal-entries/create-manual/", payload, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_unbalanced_manual_journal_is_rejected(organization, branch, academic_year, academic_period, accounts):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)

    response = client_for(accountant).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts, debit="1000.00", credit="900.00"),
        format="json",
    )

    assert response.status_code == 400
    assert "debits and credits" in str(response.json()["errors"]).lower()


@pytest.mark.django_db
def test_journal_approval_and_maker_checker(organization, branch, academic_year, academic_period, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="journal-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="journal-checker")
    create_response = client_for(maker).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )
    journal_id = create_response.json()["data"]["id"]

    self_approval = client_for(maker).post(f"/api/v1/journal-entries/{journal_id}/approve/", {}, format="json")
    approval = client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/approve/", {}, format="json")

    assert self_approval.status_code == 400
    assert "maker-checker" in str(self_approval.json()["errors"]).lower()
    assert approval.status_code == 200
    assert approval.json()["data"]["status"] == JournalEntry.Status.APPROVED
    assert JournalEntry.objects.get(id=journal_id).posted_at is None


@pytest.mark.django_db
def test_journal_posting_uses_ledger_and_audit_log(organization, branch, academic_year, academic_period, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="post-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="post-checker")
    create_response = client_for(maker).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )
    journal_id = create_response.json()["data"]["id"]
    client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/approve/", {}, format="json")

    post_response = client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/post/", {}, format="json")
    ledger = GeneralLedgerReportService.get_account_ledger(
        filters=FinancialReportFilters(organization=organization, account=accounts["1110"]),
    )

    assert post_response.status_code == 200
    assert post_response.json()["data"]["status"] == JournalEntry.Status.POSTED
    assert ledger.total_debit == Decimal("1000.00")
    assert AuditLog.objects.filter(metadata__event="journal_entry_posted", object_id=str(journal_id)).exists()


@pytest.mark.django_db
def test_posting_blocks_hard_closed_academic_year(organization, branch, academic_year, academic_period, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="closed-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="closed-checker")
    create_response = client_for(maker).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )
    journal_id = create_response.json()["data"]["id"]
    client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/approve/", {}, format="json")
    academic_year.status = AcademicYear.Status.HARD_CLOSED
    academic_year._allow_hard_closed_update = True
    academic_year.save(update_fields=["status"])

    response = client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/post/", {}, format="json")

    assert response.status_code == 400
    assert "hard-closed academic year" in str(response.json()["errors"]).lower()


@pytest.mark.django_db
def test_posted_journal_cannot_be_patched(organization, branch, academic_year, academic_period, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="patch-maker")
    checker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="patch-checker")
    create_response = client_for(maker).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )
    journal_id = create_response.json()["data"]["id"]
    client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/approve/", {}, format="json")
    client_for(checker).post(f"/api/v1/journal-entries/{journal_id}/post/", {}, format="json")

    response = client_for(checker).patch(f"/api/v1/journal-entries/{journal_id}/", {"description": "changed"}, format="json")

    assert response.status_code == 405


@pytest.mark.django_db
def test_document_reference_can_be_attached_to_journal(organization, branch, academic_year, academic_period, accounts):
    maker = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch, email_prefix="document-maker")
    create_response = client_for(maker).post(
        "/api/v1/journal-entries/create-manual/",
        journal_payload(organization, branch, academic_year, academic_period, accounts),
        format="json",
    )
    journal_id = create_response.json()["data"]["id"]

    response = client_for(maker).post(
        f"/api/v1/journal-entries/{journal_id}/documents/",
        {
            "document_type": AccountingDocument.DocumentType.VOUCHER,
            "reference_number": "VCH-001",
            "file_path": "documents/accounting/VCH-001.pdf",
            "description": "Voucher reference",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["data"]["journal_entry"] == journal_id
    assert AccountingDocument.objects.filter(journal_entry_id=journal_id, reference_number="VCH-001").exists()
