from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academic.models import AcademicYear
from accounting.models import Account
from billing.models import StudentPayment
from classes.models import ClassRoom
from common.audit import AuditAction, AuditLogService, AuditModule
from organizations.models import Branch, Organization
from students.models import Student
from teachers.models import Teacher


@pytest.fixture
def user():
    return get_user_model().objects.create_superuser(email="api@example.com", password="secure-password")


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
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


@pytest.mark.django_db
def test_health_endpoint_still_works(client):
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
def test_deep_health_endpoint_checks_database(client):
    response = client.get("/api/health/deep/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["checks"]["database"] is True
    assert payload["meta"]["redis_checked"] is False


@pytest.mark.django_db
def test_api_requires_authentication(client):
    response = client.get("/api/v1/organizations/")
    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_organization_list_create_endpoint(api_client):
    response = api_client.post(
        "/api/v1/organizations/",
        {"legal_name": "Auras Education Pvt. Ltd.", "display_name": "Auras Education"},
        format="json",
    )
    assert response.status_code == 201

    list_response = api_client.get("/api/v1/organizations/?search=Auras")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["pagination"]["count"] == 1


@pytest.mark.django_db
def test_branch_list_create_endpoint(api_client, organization):
    response = api_client.post(
        "/api/v1/branches/",
        {
            "organization": str(organization.id),
            "code": "MAIN",
            "name": "Main Branch",
            "is_main_branch": True,
        },
        format="json",
    )
    assert response.status_code == 201

    list_response = api_client.get(f"/api/v1/branches/?organization={organization.id}&search=MAIN")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["pagination"]["count"] == 1


@pytest.mark.django_db
def test_student_list_create_endpoint(api_client, organization, branch, academic_year):
    response = api_client.post(
        "/api/v1/students/",
        {
            "organization": str(organization.id),
            "branch": str(branch.id),
            "academic_year": str(academic_year.id),
            "admission_number": "ADM-001",
            "full_name": "Sita Sharma",
            "permanent_address": "Kathmandu",
            "status": Student.Status.ACTIVE,
        },
        format="json",
    )
    assert response.status_code == 201

    list_response = api_client.get("/api/v1/students/?search=Sita")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["pagination"]["count"] == 1


@pytest.mark.django_db
def test_teacher_list_create_endpoint(api_client, organization, branch):
    response = api_client.post(
        "/api/v1/teachers/",
        {
            "organization": str(organization.id),
            "branch": str(branch.id),
            "employee_number": "T-001",
            "full_name": "Ram Sir",
            "phone": "9800000000",
            "status": Teacher.Status.ACTIVE,
        },
        format="json",
    )
    assert response.status_code == 201

    list_response = api_client.get("/api/v1/teachers/?search=Ram")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["pagination"]["count"] == 1


@pytest.mark.django_db
def test_class_list_create_endpoint(api_client, organization, branch, academic_year):
    response = api_client.post(
        "/api/v1/classes/",
        {
            "organization": str(organization.id),
            "branch": str(branch.id),
            "academic_year": str(academic_year.id),
            "class_name": "Grade 10",
            "batch_name": "Morning",
            "status": ClassRoom.Status.ACTIVE,
        },
        format="json",
    )
    assert response.status_code == 201

    list_response = api_client.get("/api/v1/classes/?search=Grade")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["pagination"]["count"] == 1


@pytest.mark.django_db
def test_billing_read_list_endpoint(api_client, organization, branch, academic_year):
    student = Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number="ADM-001",
        full_name="Sita Sharma",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )
    StudentPayment.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        draft_receipt_number="DR-000001",
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("100.00"),
        net_received_amount=Decimal("100.00"),
    )

    response = api_client.get("/api/v1/student-payments/")
    assert response.status_code == 200
    assert response.json()["meta"]["pagination"]["count"] == 1


@pytest.mark.django_db
def test_accounting_read_list_endpoint(api_client, organization):
    Account.objects.create(
        organization=organization,
        code="1110",
        name="Cash in Hand",
        account_type=Account.AccountType.ASSET,
        normal_balance=Account.NormalBalance.DEBIT,
    )

    response = api_client.get("/api/v1/accounts/?search=Cash")
    assert response.status_code == 200
    assert response.json()["meta"]["pagination"]["count"] == 1


@pytest.mark.django_db
def test_audit_logs_are_read_only(api_client, organization):
    AuditLogService.record(action=AuditAction.CREATE, module=AuditModule.ORGANIZATIONS, obj=organization)

    list_response = api_client.get("/api/v1/audit-logs/")
    create_response = api_client.post("/api/v1/audit-logs/", {"action": "create"}, format="json")

    assert list_response.status_code == 200
    assert create_response.status_code == 405


@pytest.mark.django_db
def test_financial_records_are_read_only_through_api(api_client, organization, branch, academic_year):
    student = Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number="ADM-001",
        full_name="Sita Sharma",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )
    payment = StudentPayment.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        receipt_number="RC-000001",
        payment_date_ad=date(2024, 7, 20),
        payment_method=StudentPayment.PaymentMethod.CASH,
        amount=Decimal("100.00"),
        net_received_amount=Decimal("100.00"),
        status=StudentPayment.Status.POSTED,
    )

    response = api_client.patch(f"/api/v1/student-payments/{payment.id}/", {"notes": "changed"}, format="json")
    assert response.status_code == 405


@pytest.mark.django_db
def test_report_endpoint_works(api_client, organization):
    response = api_client.get(f"/api/v1/reports/trial-balance/?organization={organization.id}")
    assert response.status_code == 200
    assert "is_balanced" in response.json()["data"]
