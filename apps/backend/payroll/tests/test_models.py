from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from academic.models import AcademicPeriod, AcademicYear
from organizations.models import Branch, Organization
from payroll.models import (
    TeacherDeduction,
    TeacherEarning,
    TeacherPayment,
    TeacherPaymentAllocation,
    TeacherPaymentBatch,
)
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
    return get_user_model().objects.create_user(email="payroll-model@example.com", password="secure-password")


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
def test_create_teacher_earning(organization, branch, academic_year, academic_period, teacher, user):
    earning = TeacherEarning.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        teacher=teacher,
        earning_source=TeacherEarning.EarningSource.MANUAL_ADJUSTMENT,
        earning_date_ad=date(2024, 7, 20),
        gross_amount=Decimal("1000.00"),
        deduction_amount=Decimal("100.00"),
        net_amount=Decimal("900.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("900.00"),
        created_by=user,
    )
    assert "T-001" in str(earning)


@pytest.mark.django_db
def test_batch_number_unique_per_org(organization, branch, academic_year):
    TeacherPaymentBatch.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        batch_number="BATCH-001",
        batch_date_ad=date(2024, 7, 20),
        total_amount=Decimal("0.00"),
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            TeacherPaymentBatch.objects.create(
                organization=organization,
                branch=branch,
                academic_year=academic_year,
                batch_number="BATCH-001",
                batch_date_ad=date(2024, 7, 21),
                total_amount=Decimal("0.00"),
            )


@pytest.mark.django_db
def test_create_teacher_payment_and_allocation(organization, branch, academic_year, teacher):
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
        draft_voucher_number="TDV-000001",
        payment_date_ad=date(2024, 7, 21),
        payment_method=TeacherPayment.PaymentMethod.CASH,
        amount=Decimal("400.00"),
        deduction_amount=Decimal("0.00"),
        net_paid_amount=Decimal("400.00"),
    )
    allocation = TeacherPaymentAllocation.objects.create(
        teacher_payment=payment,
        teacher_earning=earning,
        amount_allocated=Decimal("400.00"),
    )
    assert "allocation" in str(allocation)


@pytest.mark.django_db
def test_allocation_must_be_positive(organization, branch, academic_year, teacher):
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
    )
    payment = TeacherPayment.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        draft_voucher_number="TDV-000001",
        payment_date_ad=date(2024, 7, 21),
        payment_method=TeacherPayment.PaymentMethod.CASH,
        amount=Decimal("400.00"),
        deduction_amount=Decimal("0.00"),
        net_paid_amount=Decimal("400.00"),
    )
    allocation = TeacherPaymentAllocation(
        teacher_payment=payment,
        teacher_earning=earning,
        amount_allocated=Decimal("0.00"),
    )
    with pytest.raises(ValidationError):
        allocation.full_clean()


@pytest.mark.django_db
def test_create_teacher_deduction(organization, branch, academic_year, teacher, user):
    deduction = TeacherDeduction.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        teacher=teacher,
        deduction_type=TeacherDeduction.DeductionType.ADJUSTMENT,
        amount=Decimal("100.00"),
        reason="Adjustment",
        status=TeacherDeduction.Status.APPROVED,
        approved_by=user,
    )
    assert deduction.amount == Decimal("100.00")
