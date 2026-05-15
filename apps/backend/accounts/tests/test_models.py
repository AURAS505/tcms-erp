import uuid

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import PasswordResetToken, Permission, Role, RolePermission, UserRole


@pytest.mark.django_db
def test_user_creation_normalizes_email_and_username():
    user = get_user_model().objects.create_user(
        email="Admin@Example.COM",
        username="AdminUser",
        password="secure-password",
    )

    assert user.email == "Admin@example.com"
    assert user.username == "adminuser"
    assert user.check_password("secure-password")
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_superuser_creation_sets_required_flags():
    user = get_user_model().objects.create_superuser(email="owner@example.com", password="secure-password")

    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.status == get_user_model().UserStatus.ACTIVE


@pytest.mark.django_db
def test_role_creation():
    role = Role.objects.create(code=Role.RoleCode.AUDITOR, name="Auditor", is_read_only=True)

    assert str(role) == "Auditor"
    assert role.is_read_only is True


@pytest.mark.django_db
def test_permission_creation():
    permission = Permission.objects.create(
        code="students.view",
        name="View students",
        module="students",
        is_read_only=True,
    )

    assert str(permission) == "students.view"
    assert permission.module == "students"


@pytest.mark.django_db
def test_assigning_role_to_user():
    user = get_user_model().objects.create_user(email="branch@example.com", password="secure-password")
    role = Role.objects.create(code=Role.RoleCode.BRANCH_ADMIN, name="Branch Admin")

    assignment = UserRole.objects.create(user=user, role=role)

    assert str(assignment) == "branch@example.com -> Branch Admin"
    assert assignment.is_active is True


@pytest.mark.django_db
def test_assigning_permission_to_role():
    role = Role.objects.create(code=Role.RoleCode.RECEPTIONIST, name="Receptionist")
    permission = Permission.objects.create(code="inquiry.create", name="Create inquiry", module="students")

    assignment = RolePermission.objects.create(role=role, permission=permission)

    assert str(assignment) == "Receptionist -> inquiry.create"
    assert assignment.is_active is True


@pytest.mark.django_db
def test_password_reset_token_hashing_behavior():
    user = get_user_model().objects.create_user(email="reset@example.com", password="secure-password")
    raw_token, token = PasswordResetToken.create_for_user(
        user,
        expires_at=timezone.now() + timezone.timedelta(hours=1),
    )

    assert token.token_hash != raw_token
    assert len(token.token_hash) == 64
    assert token.matches(raw_token) is True
    assert token.matches("wrong-token") is False


@pytest.mark.django_db
def test_user_string_representation():
    user = get_user_model().objects.create_user(email="person@example.com", password="secure-password")

    assert str(user) == "person@example.com"


@pytest.mark.django_db
def test_force_password_change_field_behavior():
    user = get_user_model().objects.create_user(
        email="force@example.com",
        password="secure-password",
        force_password_change=True,
    )

    assert user.force_password_change is True


@pytest.mark.django_db
def test_branch_assignment_placeholder_uses_uuid_values():
    user = get_user_model().objects.create_user(email="scoped@example.com", password="secure-password")
    assignment = user.branch_assignments.create(branch_id=uuid.uuid4())

    assert isinstance(assignment.organization_id, uuid.UUID)
    assert isinstance(assignment.branch_id, uuid.UUID)
