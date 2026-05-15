from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health_check(_request):
    return JsonResponse({"success": True, "data": {"status": "ok"}, "message": "TCMS ERP backend is running", "errors": None, "meta": {}})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
]
