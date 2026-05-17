from django.urls import path

from .views import (
    CurrentUserAPIView,
    CsrfTokenAPIView,
    ForcePasswordChangeAPIView,
    LoginAPIView,
    LogoutAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    SessionStatusAPIView,
)


urlpatterns = [
    path("csrf/", CsrfTokenAPIView.as_view(), name="auth-csrf"),
    path("login/", LoginAPIView.as_view(), name="auth-login"),
    path("logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("me/", CurrentUserAPIView.as_view(), name="auth-me"),
    path("session/", SessionStatusAPIView.as_view(), name="auth-session"),
    path("password-reset/request/", PasswordResetRequestAPIView.as_view(), name="auth-password-reset-request"),
    path("password-reset/confirm/", PasswordResetConfirmAPIView.as_view(), name="auth-password-reset-confirm"),
    path("force-password-change/", ForcePasswordChangeAPIView.as_view(), name="auth-force-password-change"),
]
