from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum

from academic.models import AcademicPeriod, AcademicYear
from accounting.models import Account, JournalEntry
from billing.models import BillStatus, FeePlan, StudentAdvanceBalance, StudentFeeDue, StudentInvoice, StudentPayment
from billing.services import PaymentAllocationInput, StudentPaymentService
from classes.models import ClassEnrollment, ClassRoom
from common.models import AuditLog
from organizations.models import Branch, Organization
from students.models import Student


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
        bs_end_date="2081-04-32",
        ad_start_date=date(2024, 7, 16),
        ad_end_date=date(2024, 8, 16),
    )


@pytest.fixture
def maker():
    return get_user_model().objects.create_user(email="maker@example.com", password="secure-password")


@pytest.fixture
def checker():
    return get_user_model().objects.create_user(email="checker@example.com", password="secure-password")


@pytest.fixture
def student(organization, branch, academic_year):
    return Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number="ADM-001",
        full_name="Sita Sharma",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )


@pytest.fixture
def class_room(organization, branch, academic_year):
    return ClassRoom.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        class_name="Grade 10",
        batch_name="Morning",
        section_name="A",
        status=ClassRoom.Status.ACTIVE,
    )


@pytest.fixture
def enrollment(organization, branch, academic_year, student, class_room):
    return ClassEnrollment.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        class_room=class_room,
        joined_date_ad=date(2024, 5, 1),
        status=ClassEnrollment.Status.ACTIVE,
    )


@pytest.fixture
def fee_plan(organization, branch, academic_year, class_room):
    return FeePlan.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        class_room=class_room,
        name="Monthly Plan",
    )


@pytest.fixture
def fee_due(organization, branch, academic_year, academic_period, student, class_room, enrollment, fee_plan):
    return StudentFeeDue.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        student=student,
        class_room=class_room,
        class_enrollment=enrollment,
        fee_plan=fee_plan,
        period_label="Shrawan 2081",
        due_date_ad=date(2024, 7, 20),
        original_amount=Decimal("2500.00"),
        discount_amount=Decimal("0.00"),
        fine_amount=Decimal("0.00"),
        net_amount=Decimal("2500.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("2500.00"),
        status=BillStatus.UNPAID,
    )


@pytest.fixture
def invoice(organization, branch, academic_year, academic_period, student):
    return StudentInvoice.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        student=student,
        invoice_number="INV-001",
        invoice_date_ad=date(2024, 7, 16),
        subtotal=Decimal("2500.00"),
        discount_amount=Decimal("0.00"),
        fine_amount=Decimal("0.00"),
        total_amount=Decimal("2500.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("2500.00"),
        status=BillStatus.UNPAID,
    )


@pytest.fixture
def configure_accounts(organization):
    Account.objects.create(
        organization=organization,
        code="1110",
        name="Cash in Hand",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
    )
    Account.objects.create(
        organization=organization,
        code="1120",
        name="Bank Account",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
    )
    Account.objects.create(
        organization=organization,
        code="1130",
        name="Online Wallet",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
    )
    Account.objects.create(
        organization=organization,
        code="1210",
        name="Student Receivable",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
    )
    Account.objects.create(
        organization=organization,
        code="2210",
        name="Student Advance Revenue",
        account_type=Account.AccountType.LIABILITY,
        normal_balance=Account.NormalBalance.CREDIT,
    )


@pytest.mark.django_db
def test_create_draft_cash_payment(organization, branch, academic_year, student, maker):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        created_by=maker,
    )
    assert payment.status == StudentPayment.Status.DRAFT
    assert payment.draft_receipt_number is not None


@pytest.mark.django_db
def test_draft_payment_does_not_create_journal_entry(organization, branch, academic_year, student, maker):
    StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        created_by=maker,
    )
    assert JournalEntry.objects.count() == 0


@pytest.mark.django_db
def test_create_draft_allocated_payment(organization, branch, academic_year, student, fee_due, maker):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("1000.00"))],
    )
    assert payment.allocations.count() == 1


@pytest.mark.django_db
def test_reject_allocation_greater_than_payment_amount(organization, branch, academic_year, student, fee_due, maker):
    with pytest.raises(ValidationError):
        StudentPaymentService.create_draft_payment(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            student=student,
            payment_date_ad=date(2024, 7, 20),
            payment_method=StudentPayment.PaymentMethod.CASH,
            amount=Decimal("1000.00"),
            created_by=maker,
            allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("1200.00"))],
        )


@pytest.mark.django_db
def test_reject_allocation_greater_than_due_balance(organization, branch, academic_year, student, fee_due, maker):
    with pytest.raises(ValidationError):
        StudentPaymentService.create_draft_payment(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            student=student,
            payment_date_ad=date(2024, 7, 20),
            payment_method=StudentPayment.PaymentMethod.CASH,
            amount=Decimal("3000.00"),
            created_by=maker,
            allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("3000.00"))],
        )


@pytest.mark.django_db
def test_reject_self_approval_by_maker_checker_rule(
    organization, branch, academic_year, student, fee_due, maker, configure_accounts
):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("1000.00"))],
    )
    with pytest.raises(ValidationError):
        StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=maker)


@pytest.mark.django_db
def test_approve_post_cash_payment(
    organization, branch, academic_year, student, fee_due, invoice, maker, checker, configure_accounts
):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("2000.00"),
        created_by=maker,
        allocations=[
            PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("1000.00")),
            PaymentAllocationInput(invoice_id=str(invoice.id), amount_allocated=Decimal("1000.00")),
        ],
    )
    posted = StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)
    fee_due.refresh_from_db()
    invoice.refresh_from_db()

    assert posted.status == StudentPayment.Status.POSTED
    assert posted.receipt_number is not None
    assert fee_due.status == BillStatus.PARTIAL
    assert invoice.status == BillStatus.PARTIAL


@pytest.mark.django_db
def test_approve_post_bank_payment(
    organization, branch, academic_year, student, fee_due, maker, checker, configure_accounts
):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.BANK,
        amount=Decimal("2500.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("2500.00"))],
    )
    posted = StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)
    assert posted.status == StudentPayment.Status.POSTED


@pytest.mark.django_db
def test_posting_creates_balanced_journal_entry(
    organization, branch, academic_year, student, fee_due, maker, checker, configure_accounts
):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("1000.00"))],
    )
    StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)
    entry = JournalEntry.objects.get(source_object_id=payment.id)
    totals = entry.lines.aggregate(
        debit_total=Sum("debit_amount", default=Decimal("0.00")),
        credit_total=Sum("credit_amount", default=Decimal("0.00")),
    )
    assert totals["debit_total"] == totals["credit_total"]


@pytest.mark.django_db
def test_due_status_partial_and_paid(
    organization, branch, academic_year, student, fee_due, maker, checker, configure_accounts
):
    partial = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("1000.00"))],
    )
    StudentPaymentService.approve_payment(payment_id=partial.id, approved_by=checker)
    fee_due.refresh_from_db()
    assert fee_due.status == BillStatus.PARTIAL

    remaining = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 21),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1500.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("1500.00"))],
    )
    StudentPaymentService.approve_payment(payment_id=remaining.id, approved_by=checker)
    fee_due.refresh_from_db()
    assert fee_due.status == BillStatus.PAID


@pytest.mark.django_db
def test_advance_payment_credits_advance_revenue_and_updates_balance(
    organization, branch, academic_year, student, maker, checker, configure_accounts
):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 22),
        payment_method=StudentPayment.PaymentMethod.BANK,
        amount=Decimal("3000.00"),
        created_by=maker,
        is_advance_payment=True,
    )
    posted = StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)
    advance = StudentAdvanceBalance.objects.get(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
    )
    entry = JournalEntry.objects.get(source_object_id=payment.id)
    credit_line = entry.lines.filter(credit_amount=Decimal("3000.00")).first()

    assert posted.status == StudentPayment.Status.POSTED
    assert advance.received_amount == Decimal("3000.00")
    assert advance.balance_amount == Decimal("3000.00")
    assert credit_line.account.code == "2210"


@pytest.mark.django_db
def test_receipt_number_assigned_on_posting(
    organization, branch, academic_year, student, fee_due, maker, checker, configure_accounts
):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("500.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("500.00"))],
    )
    posted = StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)
    assert posted.receipt_number.startswith("RC-")


@pytest.mark.django_db
def test_missing_account_configuration_raises_error(
    organization, branch, academic_year, student, fee_due, maker, checker
):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("500.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("500.00"))],
    )
    with pytest.raises(ValidationError):
        StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)


@pytest.mark.django_db
def test_audit_log_created_after_posting(
    organization, branch, academic_year, student, fee_due, maker, checker, configure_accounts
):
    payment = StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("500.00"),
        created_by=maker,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("500.00"))],
    )
    StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)
    assert AuditLog.objects.filter(module=AuditLog.Module.BILLING, action=AuditLog.Action.POST, object_id=str(payment.id)).exists()
