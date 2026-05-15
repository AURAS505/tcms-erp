import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from common.audit import AuditAction, AuditContext, AuditLogService, AuditModule, reset_audit_context, set_audit_context
from common.models import AuditLog
from organizations.models import Branch, Organization


@pytest.fixture
def organization():
    return Organization.objects.create(legal_name="Auras Education Pvt. Ltd.", display_name="Auras Education")


@pytest.fixture
def branch(organization):
    return Branch.objects.create(organization=organization, code="MAIN", name="Main Branch", is_main_branch=True)


@pytest.fixture
def user():
    return get_user_model().objects.create_user(email="audit@example.com", password="secure-password")


@pytest.mark.django_db
def test_create_audit_log_through_service(organization, branch, user):
    audit_log = AuditLogService.record(
        action=AuditAction.CREATE,
        module=AuditModule.ORGANIZATIONS,
        organization=organization,
        branch=branch,
        user=user,
        object_type="organizations.Organization",
        object_id=str(organization.id),
        object_repr=str(organization),
        metadata={"source": "test"},
        reason="Created for audit test.",
    )

    assert audit_log.organization == organization
    assert audit_log.branch == branch
    assert audit_log.user == user
    assert audit_log.action == AuditAction.CREATE
    assert audit_log.module == AuditModule.ORGANIZATIONS
    assert audit_log.object_repr == "Auras Education"
    assert audit_log.metadata == {"source": "test"}


@pytest.mark.django_db
def test_audit_log_accepts_before_after_json(organization):
    audit_log = AuditLogService.record(
        action=AuditAction.UPDATE,
        module=AuditModule.ORGANIZATIONS,
        obj=organization,
        before_data={"display_name": "Old"},
        after_data={"display_name": "Auras Education"},
    )

    assert audit_log.before_data == {"display_name": "Old"}
    assert audit_log.after_data == {"display_name": "Auras Education"}


@pytest.mark.django_db
def test_audit_log_uses_request_context(organization, user):
    token = set_audit_context(
        AuditContext(
            user_id=str(user.id),
            ip_address="127.0.0.1",
            user_agent="pytest",
            request_id="req-1",
        )
    )
    try:
        audit_log = AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.SYSTEM,
            obj=organization,
        )
    finally:
        reset_audit_context(token)

    assert audit_log.user == user
    assert audit_log.ip_address == "127.0.0.1"
    assert audit_log.user_agent == "pytest"
    assert audit_log.request_id == "req-1"


@pytest.mark.django_db
def test_audit_logs_are_append_only_on_save(organization):
    audit_log = AuditLogService.record(
        action=AuditAction.CREATE,
        module=AuditModule.ORGANIZATIONS,
        obj=organization,
    )

    audit_log.reason = "Changed reason"
    with pytest.raises(ValidationError):
        audit_log.save()


@pytest.mark.django_db
def test_audit_logs_cannot_be_deleted_by_model_delete(organization):
    audit_log = AuditLogService.record(
        action=AuditAction.CREATE,
        module=AuditModule.ORGANIZATIONS,
        obj=organization,
    )

    with pytest.raises(ValidationError):
        audit_log.delete()

    assert AuditLog.objects.filter(id=audit_log.id).exists()
