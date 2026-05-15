from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from academic.models import AcademicPeriod, AcademicYear
from accounting.models import Account, AccountingDocument, JournalEntry, JournalEntryLine
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
def cash_account(organization):
    return Account.objects.create(
        organization=organization,
        code="1110",
        name="Cash in Hand",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
        is_system_account=True,
    )


@pytest.fixture
def receivable_account(organization):
    return Account.objects.create(
        organization=organization,
        code="1210",
        name="Student Receivables",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
        is_system_account=True,
    )


@pytest.fixture
def journal_entry(organization, branch, academic_year, academic_period):
    return JournalEntry.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        entry_number="JV-0001",
        entry_date_ad=date(2024, 7, 16),
        entry_date_bs="2081-04-01",
        description="Opening test journal",
        narration="Test double-entry foundation.",
    )


@pytest.mark.django_db
def test_create_account(cash_account):
    assert str(cash_account) == "1110 - Cash in Hand"
    assert cash_account.is_active is True
    assert cash_account.normal_balance == Account.NormalBalance.DEBIT


@pytest.mark.django_db
def test_enforce_unique_account_code_per_organization(organization, cash_account):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Account.objects.create(
                organization=organization,
                code=cash_account.code,
                name="Duplicate Cash",
                account_type=Account.AccountType.ASSET,
                normal_balance=Account.NormalBalance.DEBIT,
            )


@pytest.mark.django_db
def test_account_parent_must_share_organization(organization, cash_account):
    other = Organization.objects.create(legal_name="Other Pvt. Ltd.", display_name="Other")
    child = Account(
        organization=other,
        code="1111",
        name="Other Cash Child",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
        parent=cash_account,
    )

    with pytest.raises(ValidationError):
        child.full_clean()


@pytest.mark.django_db
def test_create_journal_entry(journal_entry):
    assert str(journal_entry) == "JV-0001"
    assert journal_entry.status == JournalEntry.Status.DRAFT
    assert journal_entry.is_posted is False


@pytest.mark.django_db
def test_create_debit_line(journal_entry, cash_account):
    line = JournalEntryLine.objects.create(
        journal_entry=journal_entry,
        organization=journal_entry.organization,
        branch=journal_entry.branch,
        account=cash_account,
        debit_amount=Decimal("100.00"),
    )

    assert str(line) == "JV-0001 - 1110"
    assert line.credit_amount == Decimal("0.00")


@pytest.mark.django_db
def test_create_credit_line(journal_entry, receivable_account):
    line = JournalEntryLine.objects.create(
        journal_entry=journal_entry,
        organization=journal_entry.organization,
        branch=journal_entry.branch,
        account=receivable_account,
        credit_amount=Decimal("100.00"),
    )

    assert line.debit_amount == Decimal("0.00")
    assert line.credit_amount == Decimal("100.00")


@pytest.mark.django_db
def test_reject_line_with_both_debit_and_credit(journal_entry, cash_account):
    line = JournalEntryLine(
        journal_entry=journal_entry,
        organization=journal_entry.organization,
        account=cash_account,
        debit_amount=Decimal("100.00"),
        credit_amount=Decimal("100.00"),
    )

    with pytest.raises(ValidationError):
        line.full_clean()


@pytest.mark.django_db
def test_reject_line_with_neither_debit_nor_credit(journal_entry, cash_account):
    line = JournalEntryLine(
        journal_entry=journal_entry,
        organization=journal_entry.organization,
        account=cash_account,
        debit_amount=Decimal("0.00"),
        credit_amount=Decimal("0.00"),
    )

    with pytest.raises(ValidationError):
        line.full_clean()


@pytest.mark.django_db
def test_create_accounting_document(journal_entry):
    document = AccountingDocument.objects.create(
        organization=journal_entry.organization,
        journal_entry=journal_entry,
        document_type=AccountingDocument.DocumentType.VOUCHER,
        reference_number="VCH-001",
        file_path="private/accounting/vch-001.pdf",
        description="Voucher placeholder.",
    )

    assert str(document) == "VCH-001"
    assert document.journal_entry == journal_entry
