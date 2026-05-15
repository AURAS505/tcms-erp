from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from academic.models import AcademicYear
from organizations.models import Branch, Organization
from payroll.models import TeacherDeduction, TeacherEarning, TeacherPayment, TeacherPaymentAllocation, TeacherPaymentBatch
from teachers.models import Teacher


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
def teacher(organization, branch):
    return Teacher.objects.create(
        organization=organization,
        branch=branch,
        employee_number="T-001",
        full_name="Ram Sir",
        phone="9800000000",
        status=Teacher.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_posted_teacher_earning_is_immutable(organization, branch, academic_year, teacher):
    earning = TeacherEarning.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        earning_source=TeacherEarning.EarningSource.MANUAL_ADJUSTMENT,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("900.00"),
        deduction_amount=Decimal("0.00"),
        net_amount=Decimal("900.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("900.00"),
        status=TeacherEarning.Status.POSTED,
    )
    earning.notes = "changed"
    with pytest.raises(ValidationError):
        earning.save()
    with pytest.raises(ValidationError):
        earning.delete()


@pytest.mark.django_db
def test_posted_teacher_payment_and_allocations_are_immutable(organization, branch, academic_year, teacher):
    earning = TeacherEarning.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        earning_source=TeacherEarning.EarningSource.MANUAL_ADJUSTMENT,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("900.00"),
        deduction_amount=Decimal("0.00"),
        net_amount=Decimal("900.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("900.00"),
        status=TeacherEarning.Status.POSTED,
    )
    payment = TeacherPayment.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        voucher_number="TV-000001",
        payment_date_ad=date(2024, 7, 21),
        payment_method=TeacherPayment.PaymentMethod.CASH,
        amount=Decimal("500.00"),
        deduction_amount=Decimal("0.00"),
        net_paid_amount=Decimal("500.00"),
        status=TeacherPayment.Status.DRAFT,
    )
    allocation = TeacherPaymentAllocation.objects.create(
        teacher_payment=payment,
        teacher_earning=earning,
        amount_allocated=Decimal("500.00"),
    )
    payment.status = TeacherPayment.Status.POSTED
    payment._allow_immutable_update = True
    payment.save(update_fields=["status", "updated_at"])
    del payment._allow_immutable_update
    payment.notes = "changed"
    with pytest.raises(ValidationError):
        payment.save()
    with pytest.raises(ValidationError):
        payment.delete()
    allocation.notes = "changed"
    with pytest.raises(ValidationError):
        allocation.save()
    with pytest.raises(ValidationError):
        allocation.delete()


@pytest.mark.django_db
def test_posted_batch_immutable_and_approved_deduction_immutable(organization, branch, academic_year, teacher):
    batch = TeacherPaymentBatch.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        batch_number="BATCH-001",
        batch_date_ad=date(2024, 7, 21),
        total_amount=Decimal("500.00"),
        status=TeacherPaymentBatch.Status.POSTED,
    )
    with pytest.raises(ValidationError):
        batch.delete()

    deduction = TeacherDeduction.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        deduction_type=TeacherDeduction.DeductionType.ADJUSTMENT,
        amount=Decimal("100.00"),
        status=TeacherDeduction.Status.APPROVED,
    )
    deduction.reason = "changed"
    with pytest.raises(ValidationError):
        deduction.save()
    with pytest.raises(ValidationError):
        deduction.delete()
