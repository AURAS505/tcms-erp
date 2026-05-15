from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from academic.models import AcademicYear
from accounting.models import Account
from billing.models import StudentPayment
from billing.services import PaymentAllocationInput, StudentPaymentService
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
def maker():
    return get_user_model().objects.create_user(email="maker2@example.com", password="secure-password")


@pytest.fixture
def checker():
    return get_user_model().objects.create_user(email="checker2@example.com", password="secure-password")


@pytest.fixture
def student(organization, branch, academic_year):
    return Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number="ADM-009",
        full_name="Rita Sharma",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )


@pytest.fixture
def class_room(organization, branch, academic_year):
    return ClassRoom.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        class_name="Grade 8",
        batch_name="Day",
        section_name="B",
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
def fee_due(organization, branch, academic_year, student, class_room, enrollment):
    from billing.models import BillStatus, StudentFeeDue

    return StudentFeeDue.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        class_room=class_room,
        class_enrollment=enrollment,
        period_label="Shrawan 2081",
        due_date_ad=date(2024, 7, 20),
        original_amount=Decimal("1000.00"),
        discount_amount=Decimal("0.00"),
        fine_amount=Decimal("0.00"),
        net_amount=Decimal("1000.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("1000.00"),
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
        code="1210",
        name="Student Receivable",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
    )


@pytest.fixture
def posted_payment(organization, branch, academic_year, student, fee_due, maker, checker, configure_accounts):
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
    return StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=checker)


@pytest.mark.django_db
def test_posted_payment_cannot_be_edited(posted_payment):
    posted_payment = StudentPayment.objects.get(id=posted_payment.id)
    posted_payment.notes = "updated"
    with pytest.raises(ValidationError):
        posted_payment.save()


@pytest.mark.django_db
def test_posted_payment_cannot_be_deleted(posted_payment):
    with pytest.raises(ValidationError):
        posted_payment.delete()


@pytest.mark.django_db
def test_posted_payment_allocation_cannot_be_edited_or_deleted(posted_payment):
    allocation = posted_payment.allocations.first()
    allocation.notes = "updated"
    with pytest.raises(ValidationError):
        allocation.save()
    with pytest.raises(ValidationError):
        allocation.delete()
