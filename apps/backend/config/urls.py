from django.contrib import admin
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    return JsonResponse({"success": True, "data": {"status": "ok"}, "message": "TCMS ERP backend is running", "errors": None, "meta": {}})


def deep_health_check(_request):
    checks = {"database": _database_is_available()}
    redis_checked = False

    if settings.DEEP_HEALTH_CHECK_REDIS:
        redis_checked = True
        checks["redis"] = _redis_is_available()

    is_healthy = all(checks.values())
    status = "ok" if is_healthy else "degraded"
    return JsonResponse(
        {
            "success": is_healthy,
            "data": {"status": status, "checks": checks},
            "message": "TCMS ERP backend dependency health",
            "errors": None if is_healthy else {"health": ["One or more dependencies are unavailable."]},
            "meta": {"redis_checked": redis_checked},
        },
        status=200 if is_healthy else 503,
    )


def _database_is_available() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return False
    return True


def _redis_is_available() -> bool:
    try:
        from redis import Redis

        client = Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1, socket_timeout=1)
        return bool(client.ping())
    except Exception:
        return False


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/health/deep/", deep_health_check, name="deep-health-check"),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/", include("common.urls")),
    path("api/v1/", include("organizations.urls")),
    path("api/v1/", include("academic.urls")),
    path("api/v1/", include("students.urls")),
    path("api/v1/", include("guardians.urls")),
    path("api/v1/", include("teachers.urls")),
    path("api/v1/", include("classes.urls")),
    path("api/v1/", include("billing.urls")),
    path("api/v1/", include("payroll.urls")),
    path("api/v1/", include("accounting.urls")),
]
