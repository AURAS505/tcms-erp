from datetime import timedelta
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.test import APIClient

from accounts.models import LoginSession, PasswordResetToken, Permission, Role, RolePermission, UserBranchAssignment, UserRole


User = get_user_model()

TEST_THROTTLE_SETTINGS = {
    "auth_login": "1/min",
    "password_reset_request": "1/min",
    "password_reset_confirm": "1/min",
    "force_password_change": "1/min",
    "csrf_token": "1/min",
}


@pytest.fixture
def low_auth_throttle_rates(monkeypatch):
    cache.clear()
    monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", TEST_THROTTLE_SETTINGS)


@pytest.fixture
def user():
    return User.objects.create_user(
        email="auth@example.com",
        username="authuser",
        password="StrongPass123!",
        first_name="Auth",
        last_name="User",
    )


@pytest.mark.django_db
def test_csrf_endpoint_issues_cookie_and_token():
    client = APIClient()

    response = client.get("/api/v1/auth/csrf/")

    assert response.status_code == 200
    assert response.json()["data"]["csrf_token"]
    assert "csrftoken" in response.cookies


@pytest.mark.django_db
def test_csrf_endpoint_throttles_after_configured_limit(low_auth_throttle_rates):
    client = APIClient()

    allowed = client.get("/api/v1/auth/csrf/")
    throttled = client.get("/api/v1/auth/csrf/")

    assert allowed.status_code == 200
    assert throttled.status_code == 429


@pytest.mark.django_db
def test_login_succeeds_with_valid_username(user):
    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"username_or_email": "authuser", "password": "StrongPass123!"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["email"] == user.email
    assert LoginSession.objects.filter(user=user, revoked_at__isnull=True).exists()


@pytest.mark.django_db
def test_login_succeeds_with_valid_email(user):
    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"username_or_email": "AUTH@example.com", "password": "StrongPass123!"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["data"]["username"] == "authuser"


@pytest.mark.django_db
def test_login_fails_with_wrong_password(user):
    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"username_or_email": user.email, "password": "wrong-password"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.django_db
def test_login_fails_for_inactive_user(user):
    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])

    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"username_or_email": user.email, "password": "StrongPass123!"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_endpoint_throttles_after_configured_limit(user, low_auth_throttle_rates):
    client = APIClient()

    allowed = client.post(
        "/api/v1/auth/login/",
        {"username_or_email": "authuser", "password": "wrong-password"},
        format="json",
    )
    throttled = client.post(
        "/api/v1/auth/login/",
        {"username_or_email": "authuser", "password": "wrong-password"},
        format="json",
    )

    assert allowed.status_code == 400
    assert throttled.status_code == 429


@pytest.mark.django_db
def test_logout_works_for_authenticated_user(user):
    client = APIClient()
    login_response = client.post(
        "/api/v1/auth/login/",
        {"username_or_email": user.email, "password": "StrongPass123!"},
        format="json",
    )
    assert login_response.status_code == 200

    logout_response = client.post("/api/v1/auth/logout/")

    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logout successful"
    assert LoginSession.objects.filter(user=user, revoked_at__isnull=False).exists()


@pytest.mark.django_db
def test_current_user_requires_authentication():
    response = APIClient().get("/api/v1/auth/me/")
    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_current_user_returns_roles_permissions_and_branches(user):
    role = Role.objects.create(code=Role.RoleCode.BRANCH_ADMIN, name="Branch Admin")
    permission = Permission.objects.create(code="students.view", name="View Students", module="students")
    UserRole.objects.create(user=user, role=role)
    RolePermission.objects.create(role=role, permission=permission)
    organization_id = uuid4()
    branch_id = uuid4()
    UserBranchAssignment.objects.create(user=user, organization_id=organization_id, branch_id=branch_id, is_primary=True)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/auth/me/")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["roles"][0]["code"] == Role.RoleCode.BRANCH_ADMIN
    assert data["permissions"][0]["code"] == "students.view"
    assert data["branch_assignments"][0]["organization_id"] == str(organization_id)
    assert data["force_password_change"] is False


@pytest.mark.django_db
def test_password_reset_request_always_returns_generic_success(user):
    client = APIClient()
    existing_response = client.post("/api/v1/auth/password-reset/request/", {"email": user.email}, format="json")
    missing_response = client.post("/api/v1/auth/password-reset/request/", {"email": "missing@example.com"}, format="json")

    assert existing_response.status_code == 202
    assert missing_response.status_code == 202
    assert existing_response.json()["message"] == missing_response.json()["message"]


@pytest.mark.django_db
def test_password_reset_request_throttles_and_keeps_generic_response(user, low_auth_throttle_rates):
    client = APIClient()

    allowed = client.post("/api/v1/auth/password-reset/request/", {"email": "missing@example.com"}, format="json")
    throttled = client.post("/api/v1/auth/password-reset/request/", {"email": user.email}, format="json")

    assert allowed.status_code == 202
    assert allowed.json()["message"] == "If the email exists, password reset instructions will be sent."
    assert throttled.status_code == 429


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_password_reset_token_is_stored_hashed_not_raw(user):
    client = APIClient()
    response = client.post("/api/v1/auth/password-reset/request/", {"email": user.email}, format="json")

    raw_token = response.json()["meta"]["dev_reset_token"]
    reset_token = PasswordResetToken.objects.get(user=user)

    assert reset_token.token_hash != raw_token
    assert reset_token.token_hash == PasswordResetToken.hash_token(raw_token)


@pytest.mark.django_db
def test_password_reset_confirm_updates_password(user):
    raw_token, _reset_token = PasswordResetToken.create_for_user(user, expires_at=timezone.now() + timedelta(hours=1))

    client = APIClient()
    response = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"token": raw_token, "new_password": "NewStrongPass123!"},
        format="json",
    )

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.check_password("NewStrongPass123!")
    assert user.force_password_change is False
    assert user.password_reset_tokens.get().is_used


@pytest.mark.django_db
def test_password_reset_confirm_rejects_invalid_used_and_expired_tokens(user):
    client = APIClient()
    invalid_response = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"token": "invalid-token", "new_password": "NewStrongPass123!"},
        format="json",
    )

    used_raw_token, used_token = PasswordResetToken.create_for_user(user, expires_at=timezone.now() + timedelta(hours=1))
    used_token.used_at = timezone.now()
    used_token.save(update_fields=["used_at", "updated_at"])
    used_response = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"token": used_raw_token, "new_password": "NewStrongPass123!"},
        format="json",
    )

    expired_raw_token, _expired_token = PasswordResetToken.create_for_user(user, expires_at=timezone.now() - timedelta(minutes=1))
    expired_response = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"token": expired_raw_token, "new_password": "NewStrongPass123!"},
        format="json",
    )

    assert invalid_response.status_code == 400
    assert used_response.status_code == 400
    assert expired_response.status_code == 400


@pytest.mark.django_db
def test_password_reset_confirm_throttles_after_configured_limit(low_auth_throttle_rates):
    client = APIClient()

    allowed = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"token": "invalid-token", "new_password": "NewStrongPass123!"},
        format="json",
    )
    throttled = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"token": "invalid-token", "new_password": "NewStrongPass123!"},
        format="json",
    )

    assert allowed.status_code == 400
    assert throttled.status_code == 429


@pytest.mark.django_db
def test_force_password_change_requires_authentication():
    response = APIClient().post(
        "/api/v1/auth/force-password-change/",
        {"current_password": "StrongPass123!", "new_password": "NewStrongPass123!"},
        format="json",
    )
    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_force_password_change_rejects_wrong_current_password(user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/v1/auth/force-password-change/",
        {"current_password": "wrong-password", "new_password": "NewStrongPass123!"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_force_password_change_throttles_after_configured_limit(user, low_auth_throttle_rates):
    client = APIClient()
    client.force_authenticate(user=user)

    allowed = client.post(
        "/api/v1/auth/force-password-change/",
        {"current_password": "wrong-password", "new_password": "NewStrongPass123!"},
        format="json",
    )
    throttled = client.post(
        "/api/v1/auth/force-password-change/",
        {"current_password": "wrong-password", "new_password": "NewStrongPass123!"},
        format="json",
    )

    assert allowed.status_code == 400
    assert throttled.status_code == 429


@pytest.mark.django_db
def test_force_password_change_updates_password_and_clears_flag(user):
    user.force_password_change = True
    user.save(update_fields=["force_password_change", "updated_at"])

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/v1/auth/force-password-change/",
        {"current_password": "StrongPass123!", "new_password": "NewStrongPass123!"},
        format="json",
    )

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.check_password("NewStrongPass123!")
    assert user.force_password_change is False
