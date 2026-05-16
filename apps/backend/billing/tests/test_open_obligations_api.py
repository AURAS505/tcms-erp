from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicPeriod, AcademicYear
from accounts.models import Role, UserBranchAssignment, UserRole
from billing.models import BillStatus, StudentFeeDue, StudentInvoice
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


def user_with_role(role_code, *, branch=None, email_prefix=None):
    user = get_user_model().objects.create_user(
        email=f"{email_prefix or role_code}@example.com",
        password="secure-password",
    )
    role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role.RoleCode(role_code).label})
    UserRole.objects.create(user=user, role=role)
    if branch is not None:
        UserBranchAssignment.objects.create(user=user, organization_id=branch.organization_id, branch_id=branch.id)
    return user


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def create_student(organization, branch, academic_year, suffix):
    return Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number=f"ADM-{suffix}",
        full_name=f"Student {suffix}",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )


def create_due(organization, branch, academic_year, academic_period, student, suffix, status, balance="1000.00"):
    return StudentFeeDue.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        student=student,
        period_label=f"Period {suffix}",
        due_date_ad=date(2024, 7, 20),
        original_amount=Decimal("1000.00"),
        net_amount=Decimal("1000.00"),
        paid_amount=Decimal("0.00") if Decimal(balance) else Decimal("1000.00"),
        balance_amount=Decimal(balance),
        status=status,
    )


def create_invoice(organization, branch, academic_year, academic_period, student, suffix, status, balance="1000.00"):
    return StudentInvoice.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        academic_period=academic_period,
        student=student,
        invoice_number=f"INV-{suffix}",
        invoice_date_ad=date(2024, 7, 20),
        due_date_ad=date(2024, 7, 30),
        subtotal=Decimal("1000.00"),
        total_amount=Decimal("1000.00"),
        paid_amount=Decimal("0.00") if Decimal(balance) else Decimal("1000.00"),
        balance_amount=Decimal(balance),
        status=status,
    )


@pytest.fixture
def obligation_context(organization, branches, academic_year, academic_period):
    branch_a, branch_b = branches
    student_a = create_student(organization, branch_a, academic_year, "A")
    student_a_other = create_student(organization, branch_a, academic_year, "A2")
    student_b = create_student(organization, branch_b, academic_year, "B")

    due_open = create_due(organization, branch_a, academic_year, academic_period, student_a, "OPEN", BillStatus.UNPAID)
    due_partial = create_due(organization, branch_a, academic_year, academic_period, student_a, "PARTIAL", BillStatus.PARTIAL)
    due_approved = create_due(organization, branch_a, academic_year, academic_period, student_a, "APPROVED", BillStatus.APPROVED)
    create_due(organization, branch_a, academic_year, academic_period, student_a, "PAID", BillStatus.PAID, "0.00")
    create_due(organization, branch_a, academic_year, academic_period, student_a, "CANCELLED", BillStatus.CANCELLED)
    create_due(organization, branch_a, academic_year, academic_period, student_a, "WRITEOFF", BillStatus.WRITTEN_OFF)
    create_due(organization, branch_a, academic_year, academic_period, student_a_other, "OTHER", BillStatus.UNPAID)
    due_branch_b = create_due(organization, branch_b, academic_year, academic_period, student_b, "BRANCHB", BillStatus.UNPAID)

    invoice_open = create_invoice(organization, branch_a, academic_year, academic_period, student_a, "OPEN", BillStatus.UNPAID)
    invoice_partial = create_invoice(organization, branch_a, academic_year, academic_period, student_a, "PARTIAL", BillStatus.PARTIAL)
    invoice_approved = create_invoice(organization, branch_a, academic_year, academic_period, student_a, "APPROVED", BillStatus.APPROVED)
    create_invoice(organization, branch_a, academic_year, academic_period, student_a, "PAID", BillStatus.PAID, "0.00")
    create_invoice(organization, branch_a, academic_year, academic_period, student_a_other, "OTHER", BillStatus.UNPAID)
    invoice_branch_b = create_invoice(organization, branch_b, academic_year, academic_period, student_b, "BRANCHB", BillStatus.UNPAID)

    return {
        "branch_a": branch_a,
        "branch_b": branch_b,
        "student_a": student_a,
        "student_b": student_b,
        "due_open_ids": {str(due_open.id), str(due_partial.id), str(due_approved.id)},
        "due_branch_b": due_branch_b,
        "invoice_open_ids": {str(invoice_open.id), str(invoice_partial.id), str(invoice_approved.id)},
        "invoice_branch_b": invoice_branch_b,
    }


def response_ids(response):
    return {item["id"] for item in response.json()["data"]}


@pytest.mark.django_db
def test_student_filtered_open_dues_return_only_selected_student_open_records(obligation_context):
    user = user_with_role(Role.RoleCode.RECEPTIONIST, branch=obligation_context["branch_a"])

    response = client_for(user).get(
        "/api/v1/student-fee-dues/",
        {"student": str(obligation_context["student_a"].id), "open_only": "true"},
    )

    assert response.status_code == 200
    assert response_ids(response) == obligation_context["due_open_ids"]


@pytest.mark.django_db
def test_student_filtered_open_invoices_return_only_selected_student_open_records(obligation_context):
    user = user_with_role(Role.RoleCode.RECEPTIONIST, branch=obligation_context["branch_a"])

    response = client_for(user).get(
        "/api/v1/student-invoices/",
        {"student": str(obligation_context["student_a"].id), "open_only": "true"},
    )

    assert response.status_code == 200
    assert response_ids(response) == obligation_context["invoice_open_ids"]


@pytest.mark.django_db
def test_paid_cancelled_and_written_off_dues_are_excluded_from_open_results(obligation_context):
    user = user_with_role(Role.RoleCode.RECEPTIONIST, branch=obligation_context["branch_a"])

    response = client_for(user).get(
        "/api/v1/student-fee-dues/",
        {"student": str(obligation_context["student_a"].id), "open_only": "true"},
    )

    statuses = {item["status"] for item in response.json()["data"]}
    assert statuses == {BillStatus.APPROVED, BillStatus.UNPAID, BillStatus.PARTIAL}


@pytest.mark.django_db
def test_paid_invoices_are_excluded_from_open_results(obligation_context):
    user = user_with_role(Role.RoleCode.RECEPTIONIST, branch=obligation_context["branch_a"])

    response = client_for(user).get(
        "/api/v1/student-invoices/",
        {"student": str(obligation_context["student_a"].id), "open_only": "true"},
    )

    statuses = {item["status"] for item in response.json()["data"]}
    assert statuses == {BillStatus.APPROVED, BillStatus.UNPAID, BillStatus.PARTIAL}


@pytest.mark.django_db
def test_branch_a_user_cannot_see_branch_b_open_dues(obligation_context):
    user = user_with_role(Role.RoleCode.RECEPTIONIST, branch=obligation_context["branch_a"])

    response = client_for(user).get(
        "/api/v1/student-fee-dues/",
        {"student": str(obligation_context["student_b"].id), "open_only": "true"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.django_db
def test_branch_scoped_user_without_assignment_sees_no_open_obligations(obligation_context):
    user = user_with_role(Role.RoleCode.RECEPTIONIST, email_prefix="unassigned")
    api = client_for(user)

    dues_response = api.get(
        "/api/v1/student-fee-dues/",
        {"student": str(obligation_context["student_a"].id), "open_only": "true"},
    )
    invoices_response = api.get(
        "/api/v1/student-invoices/",
        {"student": str(obligation_context["student_a"].id), "open_only": "true"},
    )

    assert dues_response.status_code == 200
    assert invoices_response.status_code == 200
    assert dues_response.json()["data"] == []
    assert invoices_response.json()["data"] == []


@pytest.mark.django_db
def test_super_admin_can_see_open_obligations_across_branches(obligation_context):
    user = get_user_model().objects.create_superuser(email="super-admin@example.com", password="secure-password")
    api = client_for(user)

    dues_response = api.get(
        "/api/v1/student-fee-dues/",
        {"student": str(obligation_context["student_b"].id), "open_only": "true"},
    )
    invoices_response = api.get(
        "/api/v1/student-invoices/",
        {"student": str(obligation_context["student_b"].id), "open_only": "true"},
    )

    assert response_ids(dues_response) == {str(obligation_context["due_branch_b"].id)}
    assert response_ids(invoices_response) == {str(obligation_context["invoice_branch_b"].id)}
