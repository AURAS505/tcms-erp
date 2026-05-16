from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicPeriod, AcademicYear
from accounts.models import Role, UserBranchAssignment, UserRole
from accounting.models import Account
from billing.models import BillStatus, FeePlan, StudentFeeDue, StudentPayment
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


def user_with_role(role_code, branch=None, organization=None):
    user = get_user_model().objects.create_user(email=f"{role_code}@example.com", password="secure-password")
    role = Role.objects.create(code=role_code, name=Role.RoleCode(role_code).label)
    UserRole.objects.create(user=user, role=role)
    if branch is not None:
        UserBranchAssignment.objects.create(
            user=user,
            organization_id=(organization or branch.organization).id,
            branch_id=branch.id,
        )
    return user


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def draft_payload(organization, branch, academic_year, student, fee_due):
    return {
        "organization": str(organization.id),
        "branch": str(branch.id),
        "academic_year": str(academic_year.id),
        "student": str(student.id),
        "payment_date_ad": "2024-07-20",
        "payment_method": StudentPayment.PaymentMethod.CASH,
        "amount": "1000.00",
        "allocations": [{"fee_due": str(fee_due.id), "amount_allocated": "1000.00"}],
    }


def create_draft_payment(organization, branch, academic_year, student, fee_due, created_by):
    return StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        created_by=created_by,
        allocations=[PaymentAllocationInput(fee_due_id=str(fee_due.id), amount_allocated=Decimal("1000.00"))],
    )


@pytest.mark.django_db
def test_receptionist_can_create_draft_payment(organization, branch, academic_year, student, fee_due):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch)
    response = client_for(receptionist).post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_receptionist_cannot_approve_payment(organization, branch, academic_year, student, fee_due, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch)
    payment = create_draft_payment(organization, branch, academic_year, student, fee_due, created_by=receptionist)

    response = client_for(receptionist).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_accountant_can_approve_receptionist_payment(organization, branch, academic_year, student, fee_due, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch)
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)
    payment = create_draft_payment(organization, branch, academic_year, student, fee_due, created_by=receptionist)

    response = client_for(accountant).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == StudentPayment.Status.POSTED


@pytest.mark.django_db
def test_accountant_cannot_approve_own_payment(organization, branch, academic_year, student, fee_due, accounts):
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch)
    payment = create_draft_payment(organization, branch, academic_year, student, fee_due, created_by=accountant)

    response = client_for(accountant).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code == 400
    assert "Maker-checker" in str(response.json()["errors"])


@pytest.mark.django_db
def test_super_admin_can_approve_payment(organization, branch, academic_year, student, fee_due, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch)
    super_admin = get_user_model().objects.create_superuser(email="super-admin@example.com", password="secure-password")
    payment = create_draft_payment(organization, branch, academic_year, student, fee_due, created_by=receptionist)

    response = client_for(super_admin).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code == 200


@pytest.mark.django_db
def test_institute_owner_can_approve_payment(organization, branch, academic_year, student, fee_due, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch)
    owner = user_with_role(Role.RoleCode.INSTITUTE_OWNER)
    payment = create_draft_payment(organization, branch, academic_year, student, fee_due, created_by=receptionist)

    response = client_for(owner).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code == 200


@pytest.mark.django_db
def test_teacher_cannot_create_or_approve_payment(organization, branch, academic_year, student, fee_due, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch)
    teacher = user_with_role(Role.RoleCode.TEACHER, branch=branch)
    teacher_client = client_for(teacher)
    payment = create_draft_payment(organization, branch, academic_year, student, fee_due, created_by=receptionist)

    create_response = teacher_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )
    approve_response = teacher_client.post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert create_response.status_code == 403
    assert approve_response.status_code == 403


@pytest.mark.django_db
def test_auditor_can_read_but_cannot_mutate_payments(organization, branch, academic_year, student, fee_due):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch)
    auditor = user_with_role(Role.RoleCode.AUDITOR)
    UserBranchAssignment.objects.create(user=auditor, organization_id=organization.id, branch_id=branch.id)
    payment = create_draft_payment(organization, branch, academic_year, student, fee_due, created_by=receptionist)
    auditor_client = client_for(auditor)

    list_response = auditor_client.get("/api/v1/student-payments/")
    retrieve_response = auditor_client.get(f"/api/v1/student-payments/{payment.id}/")
    create_response = auditor_client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )

    assert list_response.status_code == 200
    assert retrieve_response.status_code == 200
    assert create_response.status_code == 403


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_or_approve_payment(organization, branch, academic_year, student, fee_due):
    payment = create_draft_payment(organization, branch, academic_year, student, fee_due, created_by=None)
    client = APIClient()

    create_response = client.post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(organization, branch, academic_year, student, fee_due),
        format="json",
    )
    approve_response = client.post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert create_response.status_code in {401, 403}
    assert approve_response.status_code in {401, 403}
