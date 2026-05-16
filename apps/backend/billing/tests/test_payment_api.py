from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicPeriod, AcademicYear
from accounting.models import Account, JournalEntry
from billing.models import BillStatus, FeePlan, StudentFeeDue, StudentPayment
from classes.models import ClassEnrollment, ClassRoom
from organizations.models import Branch, Organization
from students.models import Student


@pytest.fixture
def maker():
    return get_user_model().objects.create_user(email="payment-maker@example.com", password="secure-password")


@pytest.fixture
def checker():
    return get_user_model().objects.create_user(email="payment-checker@example.com", password="secure-password")


@pytest.fixture
def maker_client(maker):
    client = APIClient()
    client.force_authenticate(user=maker)
    return client


@pytest.fixture
def checker_client(checker):
    client = APIClient()
    client.force_authenticate(user=checker)
    return client


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
def accounts(organization):
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


def draft_payload(organization, branch, academic_year, student, fee_due, amount="1000.00"):
    return {
        "organization": str(organization.id),
        "branch": str(branch.id),
        "academic_year": str(academic_year.id),
        "student": str(student.id),
        "payment_date_ad": "2024-07-20",
        "payment_method": StudentPayment.PaymentMethod.CASH,
        "amount": amount,
        "allocations": [
            {
                "fee_due": str(fee_due.id),
                "amount_allocated": amount,
            }
        ],
    }


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_draft_payment(organization, branch, academic_year, student, fee_due):
    response = APIClient().post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_authenticated_user_can_create_draft_payment(maker_client, organization, branch, academic_year, student, fee_due):
    response = maker_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["data"]["status"] == StudentPayment.Status.DRAFT
    assert StudentPayment.objects.get(id=response.json()["data"]["id"]).created_by.email == "payment-maker@example.com"


@pytest.mark.django_db
def test_draft_payment_endpoint_does_not_create_journal_entry(
    maker_client, organization, branch, academic_year, student, fee_due
):
    response = maker_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )

    assert response.status_code == 201
    assert JournalEntry.objects.count() == 0


@pytest.mark.django_db
def test_draft_payment_endpoint_validates_allocation_amount(
    maker_client, organization, branch, academic_year, student, fee_due
):
    response = maker_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due, amount="3000.00"),
        format="json",
    )

    assert response.status_code == 400
    assert StudentPayment.objects.count() == 0


@pytest.mark.django_db
def test_payment_approve_endpoint_posts_payment_and_updates_due(
    maker_client, checker_client, organization, branch, academic_year, student, fee_due, accounts
):
    draft_response = maker_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due, amount="2500.00"),
        format="json",
    )
    payment_id = draft_response.json()["data"]["id"]

    response = checker_client.post(f"/api/v1/student-payments/{payment_id}/approve/", {}, format="json")
    fee_due.refresh_from_db()

    assert response.status_code == 200
    assert response.json()["data"]["status"] == StudentPayment.Status.POSTED
    assert fee_due.status == BillStatus.PAID
    assert fee_due.balance_amount == Decimal("0.00")


@pytest.mark.django_db
def test_payment_approve_endpoint_creates_journal_entry(
    maker_client, checker_client, organization, branch, academic_year, student, fee_due, accounts
):
    draft_response = maker_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )
    payment_id = draft_response.json()["data"]["id"]

    response = checker_client.post(f"/api/v1/student-payments/{payment_id}/approve/", {}, format="json")

    assert response.status_code == 200
    assert JournalEntry.objects.filter(source_model="StudentPayment", source_object_id=payment_id).exists()


@pytest.mark.django_db
def test_payment_approve_endpoint_enforces_maker_checker(
    maker_client, organization, branch, academic_year, student, fee_due, accounts
):
    draft_response = maker_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )
    payment_id = draft_response.json()["data"]["id"]

    response = maker_client.post(f"/api/v1/student-payments/{payment_id}/approve/", {}, format="json")

    assert response.status_code == 400
    assert "Maker-checker" in str(response.json()["errors"])


@pytest.mark.django_db
def test_payment_approve_endpoint_assigns_receipt_number(
    maker_client, checker_client, organization, branch, academic_year, student, fee_due, accounts
):
    draft_response = maker_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )
    payment_id = draft_response.json()["data"]["id"]

    response = checker_client.post(f"/api/v1/student-payments/{payment_id}/approve/", {}, format="json")

    assert response.status_code == 200
    assert response.json()["data"]["receipt_number"].startswith("RC-")


@pytest.mark.django_db
def test_posted_payment_cannot_be_patched(
    maker_client, checker_client, organization, branch, academic_year, student, fee_due, accounts
):
    draft_response = maker_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )
    payment_id = draft_response.json()["data"]["id"]
    checker_client.post(f"/api/v1/student-payments/{payment_id}/approve/", {}, format="json")

    response = checker_client.patch(f"/api/v1/student-payments/{payment_id}/", {"notes": "changed"}, format="json")

    assert response.status_code == 405
