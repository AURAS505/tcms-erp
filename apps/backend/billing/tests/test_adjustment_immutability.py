from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from academic.models import AcademicYear
from billing.models import BillingDiscount, BillingFine, BillingWaiver, StudentRefund
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
def user():
    return get_user_model().objects.create_user(email="immutability@example.com", password="secure-password")


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


@pytest.mark.django_db
def test_approved_discount_is_immutable(student, user):
    discount = BillingDiscount.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        discount_type=BillingDiscount.DiscountType.SCHOLARSHIP,
        discount_amount=Decimal("100.00"),
        reason="Approved discount",
        status=BillingDiscount.Status.APPROVED,
        approved_by=user,
    )
    discount.reason = "Changed"
    with pytest.raises(ValidationError):
        discount.save()
    with pytest.raises(ValidationError):
        discount.delete()


@pytest.mark.django_db
def test_approved_waiver_is_immutable(student, user):
    waiver = BillingWaiver.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        waiver_amount=Decimal("100.00"),
        reason="Approved waiver",
        status=BillingWaiver.Status.APPROVED,
        approved_by=user,
    )
    waiver.reason = "Changed"
    with pytest.raises(ValidationError):
        waiver.save()
    with pytest.raises(ValidationError):
        waiver.delete()


@pytest.mark.django_db
def test_approved_fine_is_immutable(student, user):
    fine = BillingFine.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        fine_type=BillingFine.FineType.LATE_FEE,
        amount=Decimal("100.00"),
        reason="Approved fine",
        status=BillingFine.Status.APPROVED,
        approved_by=user,
    )
    fine.reason = "Changed"
    with pytest.raises(ValidationError):
        fine.save()
    with pytest.raises(ValidationError):
        fine.delete()


@pytest.mark.django_db
def test_paid_refund_is_immutable(student, user):
    refund = StudentRefund.objects.create(
        organization=student.organization,
        branch=student.branch,
        academic_year=student.academic_year,
        student=student,
        refund_amount=Decimal("100.00"),
        refund_reason="Paid refund",
        status=StudentRefund.Status.PAID,
        paid_by=user,
    )
    refund.refund_reason = "Changed"
    with pytest.raises(ValidationError):
        refund.save()
    with pytest.raises(ValidationError):
        refund.delete()
