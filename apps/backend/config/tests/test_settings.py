import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings import env_bool, env_int, env_list, validate_security_configuration


def test_env_list_parses_comma_separated_values(monkeypatch):
    monkeypatch.setenv("TCMS_TEST_LIST", "https://app.example.com, https://admin.example.com,")

    assert env_list("TCMS_TEST_LIST") == ["https://app.example.com", "https://admin.example.com"]


def test_env_bool_accepts_common_true_values(monkeypatch):
    monkeypatch.setenv("TCMS_TEST_BOOL", "yes")

    assert env_bool("TCMS_TEST_BOOL") is True


def test_env_int_rejects_non_integer_values(monkeypatch):
    monkeypatch.setenv("TCMS_TEST_INT", "not-an-int")

    with pytest.raises(ImproperlyConfigured, match="TCMS_TEST_INT"):
        env_int("TCMS_TEST_INT")


def test_security_validation_rejects_wildcard_cors_with_credentials():
    with pytest.raises(ImproperlyConfigured, match="wildcard origins"):
        validate_security_configuration(
            environment="development",
            debug=True,
            secret_key="local",
            allowed_hosts=["localhost"],
            cors_allowed_origins=["*"],
            cors_allow_credentials=True,
            cors_allow_all_origins=False,
            csrf_trusted_origins=["http://localhost:3000"],
            session_cookie_secure=False,
            csrf_cookie_secure=False,
        )


def test_security_validation_rejects_unsafe_production_defaults():
    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        validate_security_configuration(
            environment="production",
            debug=False,
            secret_key="unsafe-local-development-key",
            allowed_hosts=["api.example.com"],
            cors_allowed_origins=["https://app.example.com"],
            cors_allow_credentials=True,
            cors_allow_all_origins=False,
            csrf_trusted_origins=["https://app.example.com"],
            session_cookie_secure=True,
            csrf_cookie_secure=True,
        )


def test_logging_config_uses_console_handler(settings):
    assert settings.LOGGING["handlers"]["console"]["class"] == "logging.StreamHandler"
    assert settings.LOGGING["root"]["handlers"] == ["console"]
