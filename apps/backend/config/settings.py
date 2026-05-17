import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "y", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def env_int(name: str, default: int = 0) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} must be an integer.") from exc


def validate_security_configuration(
    *,
    environment: str,
    debug: bool,
    secret_key: str,
    allowed_hosts: list[str],
    cors_allowed_origins: list[str],
    cors_allow_credentials: bool,
    cors_allow_all_origins: bool,
    csrf_trusted_origins: list[str],
    session_cookie_secure: bool,
    csrf_cookie_secure: bool,
) -> None:
    if cors_allow_credentials and ("*" in cors_allowed_origins or cors_allow_all_origins):
        raise ImproperlyConfigured("CORS credentials require explicit DJANGO_CORS_ALLOWED_ORIGINS; wildcard origins are unsafe.")

    if environment == "production":
        if debug:
            raise ImproperlyConfigured("DJANGO_DEBUG must be false in production.")
        if secret_key in {"", "unsafe-local-development-key", "change-me-for-local-development"}:
            raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set to a strong secret in production.")
        if not allowed_hosts:
            raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be explicit in production.")
        if not cors_allowed_origins:
            raise ImproperlyConfigured("DJANGO_CORS_ALLOWED_ORIGINS must be explicit in production.")
        if not csrf_trusted_origins:
            raise ImproperlyConfigured("DJANGO_CSRF_TRUSTED_ORIGINS must be explicit in production.")
        if not session_cookie_secure or not csrf_cookie_secure:
            raise ImproperlyConfigured("Secure session and CSRF cookies must be enabled in production.")


ENVIRONMENT = os.getenv("DJANGO_ENV", "development").strip().lower()
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-local-development-key")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "common",
    "accounts",
    "organizations",
    "academic",
    "people",
    "students",
    "guardians",
    "teachers",
    "classes",
    "billing",
    "payroll",
    "accounting",
    "reports",
    "notifications",
    "files",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardResultsSetPagination",
    "DEFAULT_THROTTLE_RATES": {
        "auth_login": os.getenv("DJANGO_THROTTLE_AUTH_LOGIN", "20/min"),
        "password_reset_request": os.getenv("DJANGO_THROTTLE_PASSWORD_RESET_REQUEST", "5/min"),
        "password_reset_confirm": os.getenv("DJANGO_THROTTLE_PASSWORD_RESET_CONFIRM", "10/min"),
        "force_password_change": os.getenv("DJANGO_THROTTLE_FORCE_PASSWORD_CHANGE", "10/min"),
        "csrf_token": os.getenv("DJANGO_THROTTLE_CSRF_TOKEN", "60/min"),
    },
    "PAGE_SIZE": 25,
}

CORS_ALLOWED_ORIGINS = env_list("DJANGO_CORS_ALLOWED_ORIGINS", "http://localhost:3000")
CORS_ALLOW_CREDENTIALS = env_bool("DJANGO_CORS_ALLOW_CREDENTIALS", True)
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "http://localhost:3000")

SESSION_COOKIE_HTTPONLY = env_bool("DJANGO_SESSION_COOKIE_HTTPONLY", True)
CSRF_COOKIE_HTTPONLY = env_bool("DJANGO_CSRF_COOKIE_HTTPONLY", False)
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", False)
SESSION_COOKIE_SAMESITE = os.getenv("DJANGO_SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = env_int("DJANGO_SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if env_bool("DJANGO_SECURE_PROXY_SSL_HEADER", False) else None

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = os.getenv("DJANGO_X_FRAME_OPTIONS", "DENY")
REFERRER_POLICY = os.getenv("DJANGO_REFERRER_POLICY", "same-origin")

validate_security_configuration(
    environment=ENVIRONMENT,
    debug=DEBUG,
    secret_key=SECRET_KEY,
    allowed_hosts=ALLOWED_HOSTS,
    cors_allowed_origins=CORS_ALLOWED_ORIGINS,
    cors_allow_credentials=CORS_ALLOW_CREDENTIALS,
    cors_allow_all_origins=env_bool("DJANGO_CORS_ALLOW_ALL_ORIGINS", False),
    csrf_trusted_origins=CSRF_TRUSTED_ORIGINS,
    session_cookie_secure=SESSION_COOKIE_SECURE,
    csrf_cookie_secure=CSRF_COOKIE_SECURE,
)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/1"))
