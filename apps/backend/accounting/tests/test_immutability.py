from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from academic.models import AcademicPeriod, AcademicYear
from accounting.models import Account, JournalEntry, JournalEntryLine
from accounting.services import AccountingPostingService
from common.models import AuditLog
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
        entry_number="JV-IMM-001",
        entry_date_ad=date(2024, 7, 16),
        entry_date_bs="2081-04-01",
        description="Immutability test journal",
    )


def add_balanced_lines(entry, debit_account, credit_account):
    JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=entry.organization,
        branch=entry.branch,
        account=debit_account,
        debit_amount=Decimal("100.00"),
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        organization=entry.organization,
        branch=entry.branch,
        account=credit_account,
        credit_amount=Decimal("100.00"),
    )


@pytest.mark.django_db
def test_posting_balanced_journal_entry_creates_audit_log(journal_entry, debit_account, credit_account):
    add_balanced_lines(journal_entry, debit_account, credit_account)

    posted = AccountingPostingService.post_journal_entry(journal_entry)

    audit_log = AuditLog.objects.get(object_id=str(posted.id), action=AuditLog.Action.POST)
    assert audit_log.module == AuditLog.Module.ACCOUNTING
    assert audit_log.organization == posted.organization
    assert audit_log.branch == posted.branch
    assert audit_log.object_repr == posted.entry_number


@pytest.mark.django_db
def test_posted_journal_entry_cannot_be_changed_normally(journal_entry, debit_account, credit_account):
    add_balanced_lines(journal_entry, debit_account, credit_account)
    posted = AccountingPostingService.post_journal_entry(journal_entry)

    posted.description = "Changed after posting"
    with pytest.raises(ValidationError):
        posted.save()


@pytest.mark.django_db
def test_posted_journal_entry_cannot_be_deleted_normally(journal_entry, debit_account, credit_account):
    add_balanced_lines(journal_entry, debit_account, credit_account)
    posted = AccountingPostingService.post_journal_entry(journal_entry)

    with pytest.raises(ValidationError):
        posted.delete()


@pytest.mark.django_db
def test_posted_journal_entry_line_cannot_be_changed_normally(journal_entry, debit_account, credit_account):
    add_balanced_lines(journal_entry, debit_account, credit_account)
    posted = AccountingPostingService.post_journal_entry(journal_entry)
    line = posted.lines.first()

    line.description = "Changed after posting"
    with pytest.raises(ValidationError):
        line.save()


@pytest.mark.django_db
def test_draft_journal_entry_remains_editable(journal_entry):
    journal_entry.description = "Draft edit is allowed"
    journal_entry.save()

    journal_entry.refresh_from_db()
    assert journal_entry.description == "Draft edit is allowed"
