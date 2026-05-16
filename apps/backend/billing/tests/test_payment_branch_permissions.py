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
def branches(organization):
    branch_a = Branch.objects.create(organization=organization, code="A", name="Branch A", is_main_branch=True)
    branch_b = Branch.objects.create(organization=organization, code="B", name="Branch B")
    return branch_a, branch_b


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
def accounts(organization):
    for code, name, account_type, normal_balance in [
        ("1110", "Cash in Hand", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1120", "Bank Account", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1130", "Online Wallet", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("1210", "Student Receivable", Account.AccountType.ASSET, Account.NormalBalance.DEBIT),
        ("2210", "Student Advance Revenue", Account.AccountType.LIABILITY, Account.NormalBalance.CREDIT),
    ]:
        Account.objects.create(
            organization=organization,
            code=code,
            name=name,
            account_type=account_type,
            normal_balance=normal_balance,
        )


def user_with_role(role_code, *, branch=None, organization=None, email_prefix=None):
    user = get_user_model().objects.create_user(
        email=f"{email_prefix or role_code}@example.com",
        password="secure-password",
    )
    role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role.RoleCode(role_code).label})
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


def branch_records(organization, branch, academic_year, academic_period, suffix):
    student = Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number=f"ADM-{suffix}",
        full_name=f"Student {suffix}",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )
    class_room = ClassRoom.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        class_name=f"Grade {suffix}",
        status=ClassRoom.Status.ACTIVE,
    )
    enrollment = ClassEnrollment.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        class_room=class_room,
        joined_date_ad=date(2024, 5, 1),
        status=ClassEnrollment.Status.ACTIVE,
    )
    fee_plan = FeePlan.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        class_room=class_room,
        name=f"Monthly Plan {suffix}",
    )
    due = StudentFeeDue.objects.create(
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
        net_amount=Decimal("2500.00"),
        balance_amount=Decimal("2500.00"),
        status=BillStatus.UNPAID,
    )
    return student, due


def draft_payload(organization, branch, academic_year, student, due, amount="1000.00"):
    return {
        "organization": str(organization.id),
        "branch": str(branch.id),
        "academic_year": str(academic_year.id),
        "student": str(student.id),
        "payment_date_ad": "2024-07-20",
        "payment_method": StudentPayment.PaymentMethod.CASH,
        "amount": amount,
        "allocations": [{"fee_due": str(due.id), "amount_allocated": amount}],
    }


def create_draft(organization, branch, academic_year, student, due, created_by):
    return StudentPaymentService.create_draft_payment(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("1000.00"),
        created_by=created_by,
        allocations=[PaymentAllocationInput(fee_due_id=str(due.id), amount_allocated=Decimal("1000.00"))],
    )


@pytest.fixture
def branch_context(organization, branches, academic_year, academic_period):
    branch_a, branch_b = branches
    student_a, due_a = branch_records(organization, branch_a, academic_year, academic_period, "A")
    student_b, due_b = branch_records(organization, branch_b, academic_year, academic_period, "B")
    return {
        "branch_a": branch_a,
        "branch_b": branch_b,
        "student_a": student_a,
        "student_b": student_b,
        "due_a": due_a,
        "due_b": due_b,
    }


@pytest.mark.django_db
def test_branch_a_receptionist_can_create_branch_a_payment(organization, academic_year, branch_context):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_a"])

    response = client_for(receptionist).post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(
            organization,
            branch_context["branch_a"],
            academic_year,
            branch_context["student_a"],
            branch_context["due_a"],
        ),
        format="json",
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_branch_a_receptionist_cannot_create_branch_b_payment(organization, academic_year, branch_context):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_a"])

    response = client_for(receptionist).post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(
            organization,
            branch_context["branch_b"],
            academic_year,
            branch_context["student_b"],
            branch_context["due_b"],
        ),
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_branch_a_accountant_can_approve_branch_a_payment(organization, academic_year, branch_context, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_a"], email_prefix="maker-a")
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch_context["branch_a"], email_prefix="accountant-a")
    payment = create_draft(
        organization,
        branch_context["branch_a"],
        academic_year,
        branch_context["student_a"],
        branch_context["due_a"],
        receptionist,
    )

    response = client_for(accountant).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == StudentPayment.Status.POSTED


@pytest.mark.django_db
def test_branch_a_accountant_cannot_approve_branch_b_payment(organization, academic_year, branch_context, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_b"], email_prefix="maker-b")
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, branch=branch_context["branch_a"], email_prefix="accountant-a")
    payment = create_draft(
        organization,
        branch_context["branch_b"],
        academic_year,
        branch_context["student_b"],
        branch_context["due_b"],
        receptionist,
    )

    response = client_for(accountant).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code in {403, 404}


@pytest.mark.django_db
def test_branch_scoped_user_without_assignment_cannot_create_payment(organization, academic_year, branch_context):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, email_prefix="unassigned-receptionist")

    response = client_for(receptionist).post(
        "/api/v1/student-payments/create-draft/",
        draft_payload(
            organization,
            branch_context["branch_a"],
            academic_year,
            branch_context["student_a"],
            branch_context["due_a"],
        ),
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_branch_scoped_user_without_assignment_cannot_approve_payment(organization, academic_year, branch_context, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_a"], email_prefix="maker-a")
    accountant = user_with_role(Role.RoleCode.ACCOUNTANT, email_prefix="unassigned-accountant")
    payment = create_draft(
        organization,
        branch_context["branch_a"],
        academic_year,
        branch_context["student_a"],
        branch_context["due_a"],
        receptionist,
    )

    response = client_for(accountant).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code in {403, 404}


@pytest.mark.django_db
def test_super_admin_can_approve_any_branch_payment(organization, academic_year, branch_context, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_b"], email_prefix="maker-b")
    super_admin = get_user_model().objects.create_superuser(email="super-admin@example.com", password="secure-password")
    payment = create_draft(
        organization,
        branch_context["branch_b"],
        academic_year,
        branch_context["student_b"],
        branch_context["due_b"],
        receptionist,
    )

    response = client_for(super_admin).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code == 200


@pytest.mark.django_db
def test_institute_owner_can_approve_any_branch_payment(organization, academic_year, branch_context, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_b"], email_prefix="maker-b")
    owner = user_with_role(Role.RoleCode.INSTITUTE_OWNER, email_prefix="owner")
    payment = create_draft(
        organization,
        branch_context["branch_b"],
        academic_year,
        branch_context["student_b"],
        branch_context["due_b"],
        receptionist,
    )

    response = client_for(owner).post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

    assert response.status_code == 200


@pytest.mark.django_db
def test_teacher_and_auditor_cannot_mutate_regardless_of_branch(organization, academic_year, branch_context, accounts):
    receptionist = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_a"], email_prefix="maker-a")
    teacher = user_with_role(Role.RoleCode.TEACHER, branch=branch_context["branch_a"], email_prefix="teacher-a")
    auditor = user_with_role(Role.RoleCode.AUDITOR, branch=branch_context["branch_a"], email_prefix="auditor-a")
    payment = create_draft(
        organization,
        branch_context["branch_a"],
        academic_year,
        branch_context["student_a"],
        branch_context["due_a"],
        receptionist,
    )

    for user in [teacher, auditor]:
        api = client_for(user)
        create_response = api.post(
            "/api/v1/student-payments/create-draft/",
            draft_payload(
                organization,
                branch_context["branch_a"],
                academic_year,
                branch_context["student_a"],
                branch_context["due_a"],
            ),
            format="json",
        )
        approve_response = api.post(f"/api/v1/student-payments/{payment.id}/approve/", {}, format="json")

        assert create_response.status_code == 403
        assert approve_response.status_code == 403


@pytest.mark.django_db
def test_branch_scoped_list_and_retrieve_only_expose_assigned_branch(organization, academic_year, branch_context):
    receptionist_a = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_a"], email_prefix="maker-a")
    receptionist_b = user_with_role(Role.RoleCode.RECEPTIONIST, branch=branch_context["branch_b"], email_prefix="maker-b")
    payment_a = create_draft(
        organization,
        branch_context["branch_a"],
        academic_year,
        branch_context["student_a"],
        branch_context["due_a"],
        receptionist_a,
    )
    payment_b = create_draft(
        organization,
        branch_context["branch_b"],
        academic_year,
        branch_context["student_b"],
        branch_context["due_b"],
        receptionist_b,
    )
    api = client_for(receptionist_a)

    list_response = api.get("/api/v1/student-payments/")
    retrieve_a_response = api.get(f"/api/v1/student-payments/{payment_a.id}/")
    retrieve_b_response = api.get(f"/api/v1/student-payments/{payment_b.id}/")

    returned_ids = {item["id"] for item in list_response.json()["data"]}
    assert list_response.status_code == 200
    assert str(payment_a.id) in returned_ids
    assert str(payment_b.id) not in returned_ids
    assert retrieve_a_response.status_code == 200
    assert retrieve_b_response.status_code in {403, 404}
