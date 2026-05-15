from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    return JsonResponse({"success": True, "data": {"status": "ok"}, "message": "TCMS ERP backend is running", "errors": None, "meta": {}})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
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
