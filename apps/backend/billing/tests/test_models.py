from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from academic.models import AcademicPeriod, AcademicYear
from billing.models import (
    BillStatus,
    BillingDiscount,
    BillingFine,
    BillingWaiver,
    FeePlan,
    FeePlanItem,
    FeeType,
    StudentAdvanceBalance,
    StudentFeeDue,
    StudentInvoice,
    StudentInvoiceItem,
    StudentPayment,
    StudentPaymentAllocation,
    StudentRefund,
)
from classes.models import ClassEnrollment, ClassRoom
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
def user():
    return get_user_model().objects.create_user(email="billing@example.com", password="secure-password")


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
        class_name="Grade 10 Mathematics",
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
        name="Grade 10 Monthly Tuition",
        fee_plan_type=FeePlan.PlanType.MONTHLY,
        billing_frequency=FeePlan.BillingFrequency.MONTHLY,
        payment_due_rule=FeePlan.PaymentDueRule.FIXED_BS_DAY,
        due_day=5,
    )


@pytest.fixture
def fee_due(organization, branch, academic_year, academic_period, student, class_room, enrollment, fee_plan, user):
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
        due_date_bs="2081-04-05",
        original_amount=Decimal("2500.00"),
        discount_amount=Decimal("100.00"),
        fine_amount=Decimal("0.00"),
        net_amount=Decimal("2400.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("2400.00"),
        status=BillStatus.APPROVED,
        approved_by=user,
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
        invoice_date_bs="2081-04-01",
        due_date_ad=date(2024, 7, 20),
        due_date_bs="2081-04-05",
        subtotal=Decimal("2500.00"),
        discount_amount=Decimal("100.00"),
        fine_amount=Decimal("0.00"),
        total_amount=Decimal("2400.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("2400.00"),
        status=BillStatus.APPROVED,
    )


@pytest.fixture
def payment(organization, branch, academic_year, student, user):
    return StudentPayment.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        draft_receipt_number="DR-001",
        payment_date_ad=date(2024, 7, 20),
        payment_date_bs="2081-04-05",
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        net_received_amount=Decimal("1000.00"),
        status=StudentPayment.Status.DRAFT,
        created_by=user,
    )


@pytest.mark.django_db
def test_create_fee_plan(fee_plan):
    assert str(fee_plan) == "Grade 10 Monthly Tuition"
    assert fee_plan.is_active is True


@pytest.mark.django_db
def test_create_fee_plan_item(fee_plan):
    item = FeePlanItem.objects.create(
        fee_plan=fee_plan,
        item_name="Monthly tuition",
        fee_type=FeeType.TUITION,
        amount=Decimal("2500.00"),
        is_recurring=True,
        sort_order=1,
    )

    assert str(item) == "Grade 10 Monthly Tuition - Monthly tuition"
    assert item.amount == Decimal("2500.00")


@pytest.mark.django_db
def test_create_student_fee_due(fee_due):
    assert str(fee_due) == "ADM-001 - Shrawan 2081"
    assert fee_due.calculated_net_amount() == Decimal("2400.00")
    assert fee_due.balance_amount == Decimal("2400.00")


@pytest.mark.django_db
def test_create_invoice(invoice):
    assert str(invoice) == "INV-001"
    assert invoice.calculated_total_amount() == Decimal("2400.00")
    assert invoice.balance_amount == Decimal("2400.00")


@pytest.mark.django_db
def test_create_invoice_item(invoice, fee_due):
    item = StudentInvoiceItem.objects.create(
        invoice=invoice,
        fee_due=fee_due,
        description="Shrawan tuition",
        fee_type=FeeType.TUITION,
        quantity=Decimal("1.00"),
        unit_amount=Decimal("2500.00"),
        discount_amount=Decimal("100.00"),
        line_total=Decimal("2400.00"),
    )

    assert str(item) == "INV-001 - Shrawan tuition"
    assert item.calculated_line_total() == Decimal("2400.0000")


@pytest.mark.django_db
def test_create_draft_student_payment(payment):
    assert str(payment) == "DR-001"
    assert payment.payment_method == StudentPayment.PaymentMethod.CASH
    assert payment.status == StudentPayment.Status.DRAFT


@pytest.mark.django_db
def test_create_payment_allocation(payment, fee_due, invoice):
    allocation = StudentPaymentAllocation.objects.create(
        payment=payment,
        fee_due=fee_due,
        invoice=invoice,
        amount_allocated=Decimal("1000.00"),
    )

    assert str(allocation) == "DR-001 allocation 1000.00"
    assert allocation.payment == payment


@pytest.mark.django_db
def test_create_advance_balance(organization, branch, academic_year, student):
    balance = StudentAdvanceBalance.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        opening_amount=Decimal("0.00"),
        received_amount=Decimal("5000.00"),
        applied_amount=Decimal("1000.00"),
        refunded_amount=Decimal("0.00"),
        balance_amount=Decimal("4000.00"),
    )

    assert str(balance) == "ADM-001 advance balance"
    assert balance.calculated_balance_amount() == Decimal("4000.00")


@pytest.mark.django_db
def test_create_billing_discount(organization, branch, academic_year, student, enrollment, fee_due, invoice, user):
    discount = BillingDiscount.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        class_enrollment=enrollment,
        fee_due=fee_due,
        invoice=invoice,
        discount_type=BillingDiscount.DiscountType.SCHOLARSHIP,
        discount_percentage=Decimal("10.0000"),
        discount_amount=Decimal("250.00"),
        reason="Scholarship approved.",
        status=BillingDiscount.Status.APPROVED,
        approved_by=user,
    )

    assert str(discount) == "ADM-001 - Scholarship"
    assert discount.approved_by == user


@pytest.mark.django_db
def test_create_waiver(organization, branch, academic_year, student, fee_due, invoice, user):
    waiver = BillingWaiver.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        fee_due=fee_due,
        invoice=invoice,
        waiver_amount=Decimal("500.00"),
        reason="Management waiver.",
        status=BillingWaiver.Status.APPROVED,
        approved_by=user,
    )

    assert str(waiver) == "ADM-001 waiver 500.00"


@pytest.mark.django_db
def test_create_fine(organization, branch, academic_year, student, fee_due, invoice, user):
    fine = BillingFine.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        fee_due=fee_due,
        invoice=invoice,
        fine_type=BillingFine.FineType.LATE_FEE,
        amount=Decimal("100.00"),
        reason="Late payment.",
        status=BillingFine.Status.APPROVED,
        approved_by=user,
    )

    assert str(fine) == "ADM-001 fine 100.00"


@pytest.mark.django_db
def test_create_refund(organization, branch, academic_year, student, payment, user):
    refund = StudentRefund.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        original_payment=payment,
        refund_voucher_number="RF-001",
        refund_date_ad=date(2024, 8, 1),
        refund_date_bs="2081-04-17",
        refund_amount=Decimal("500.00"),
        refund_reason="Advance refund request.",
        status=StudentRefund.Status.PENDING_APPROVAL,
        requested_by=user,
    )

    assert str(refund) == "RF-001"
    assert refund.original_payment == payment


@pytest.mark.django_db
def test_enforce_invoice_number_uniqueness(invoice, organization, branch, academic_year, academic_period, student):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            StudentInvoice.objects.create(
                organization=organization,
                branch=branch,
                academic_year=academic_year,
                academic_period=academic_period,
                student=student,
                invoice_number="INV-001",
                invoice_date_ad=date(2024, 7, 17),
                subtotal=Decimal("100.00"),
                total_amount=Decimal("100.00"),
                balance_amount=Decimal("100.00"),
            )


@pytest.mark.django_db
def test_enforce_receipt_number_uniqueness(payment, organization, branch, academic_year, student):
    payment.receipt_number = "RC-001"
    payment.save(update_fields=["receipt_number"])

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            StudentPayment.objects.create(
                organization=organization,
                branch=branch,
                academic_year=academic_year,
                student=student,
                receipt_number="RC-001",
                payment_date_ad=date(2024, 7, 21),
                payment_method=StudentPayment.PaymentMethod.CASH,
                amount=Decimal("100.00"),
                net_received_amount=Decimal("100.00"),
            )


@pytest.mark.django_db
def test_non_negative_amount_validation(fee_plan):
    item = FeePlanItem(
        fee_plan=fee_plan,
        item_name="Invalid",
        fee_type=FeeType.TUITION,
        amount=Decimal("-1.00"),
    )

    with pytest.raises(ValidationError):
        item.full_clean()


@pytest.mark.django_db
def test_organization_branch_academic_year_student_relationships(fee_due, invoice, payment):
    assert fee_due.organization == fee_due.student.organization
    assert fee_due.branch == fee_due.student.branch
    assert invoice.academic_year == fee_due.academic_year
    assert payment.student == fee_due.student
