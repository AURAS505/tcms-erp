from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from common.audit import AuditAction, AuditLogService, AuditModule
from common.responses import api_success, validation_error_response

from .models import LoginSession, PasswordResetToken
from .serializers import (
    CurrentUserSerializer,
    ForcePasswordChangeSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)


User = get_user_model()


def _client_ip(request) -> str | None:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _user_agent(request) -> str:
    return request.META.get("HTTP_USER_AGENT", "")


def _record_login_session(request, user) -> None:
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    if not session_key:
        return

    try:
        expires_at = request.session.get_expiry_date()
    except Exception:
        expires_at = None

    LoginSession.objects.update_or_create(
        session_key_hash=LoginSession.hash_session_key(session_key),
        defaults={
            "user": user,
            "ip_address": _client_ip(request),
            "user_agent": _user_agent(request),
            "created_from": "api_login",
            "expires_at": expires_at,
            "revoked_at": None,
            "last_seen_at": timezone.now(),
        },
    )


def _revoke_current_login_session(request) -> None:
    session_key = request.session.session_key
    if not session_key:
        return
    LoginSession.objects.filter(session_key_hash=LoginSession.hash_session_key(session_key), revoked_at__isnull=True).update(
        revoked_at=timezone.now()
    )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        user = serializer.validated_data["user"]
        login(request, user)
        user.last_login_ip = _client_ip(request)
        user.save(update_fields=["last_login_ip", "last_login", "updated_at"])
        _record_login_session(request, user)

        AuditLogService.record(
            action=AuditAction.LOGIN,
            module=AuditModule.ACCOUNTS,
            obj=user,
            user=user,
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )

        return api_success(CurrentUserSerializer(user).data, message="Login successful")


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "csrf_token"

    def get(self, request):
        return api_success({"csrf_token": get_token(request)}, message="CSRF token issued.")


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        _revoke_current_login_session(request)
        AuditLogService.record(
            action=AuditAction.LOGOUT,
            module=AuditModule.ACCOUNTS,
            obj=user,
            user=user,
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )
        logout(request)
        return api_success(message="Logout successful")


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_key = request.session.session_key
        if session_key:
            LoginSession.objects.filter(session_key_hash=LoginSession.hash_session_key(session_key), revoked_at__isnull=True).update(
                last_seen_at=timezone.now()
            )
        return api_success(CurrentUserSerializer(request.user).data)


class SessionStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_success({"authenticated": True, "user": CurrentUserSerializer(request.user).data})


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset_request"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email, is_active=True, status=User.UserStatus.ACTIVE).first()
        meta = {}

        if user is not None:
            raw_token, reset_token = PasswordResetToken.create_for_user(
                user,
                expires_at=timezone.now() + timedelta(hours=1),
                requested_ip=_client_ip(request),
                requested_user_agent=_user_agent(request),
            )
            AuditLogService.record(
                action=AuditAction.SYSTEM,
                module=AuditModule.ACCOUNTS,
                obj=user,
                user=user,
                metadata={"event": "password_reset_requested"},
                ip_address=_client_ip(request),
                user_agent=_user_agent(request),
            )
            if settings.DEBUG:
                meta["dev_reset_token"] = raw_token
                meta["dev_reset_url"] = f"/api/v1/auth/password-reset/confirm/?token={raw_token}"
                meta["dev_reset_token_expires_at"] = reset_token.expires_at.isoformat()

        return api_success(
            message="If the email exists, password reset instructions will be sent.",
            meta=meta,
            status_code=status.HTTP_202_ACCEPTED,
        )


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset_confirm"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        reset_token = serializer.validated_data["reset_token"]
        user = reset_token.user

        with transaction.atomic():
            user.set_password(serializer.validated_data["new_password"])
            user.force_password_change = False
            user.save(update_fields=["password", "force_password_change", "updated_at"])
            reset_token.used_at = timezone.now()
            reset_token.save(update_fields=["used_at", "updated_at"])
            LoginSession.objects.filter(user=user, revoked_at__isnull=True).update(revoked_at=timezone.now())

        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACCOUNTS,
            obj=user,
            user=user,
            metadata={"event": "password_reset_confirmed"},
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )

        return api_success(message="Password has been reset.")


class ForcePasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "force_password_change"

    def post(self, request):
        serializer = ForcePasswordChangeSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.force_password_change = False
        user.save(update_fields=["password", "force_password_change", "updated_at"])
        update_session_auth_hash(request, user)

        session_key = request.session.session_key
        active_sessions = LoginSession.objects.filter(user=user, revoked_at__isnull=True)
        if session_key:
            active_sessions.exclude(session_key_hash=LoginSession.hash_session_key(session_key)).update(revoked_at=timezone.now())

        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACCOUNTS,
            obj=user,
            user=user,
            metadata={"event": "forced_password_changed"},
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )

        return api_success(CurrentUserSerializer(user).data, message="Password changed successfully.")
