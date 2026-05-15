from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "module", "action", "object_type", "object_repr", "user", "organization", "branch"]
    list_filter = ["module", "action", "organization", "branch", "created_at"]
    search_fields = ["object_type", "object_id", "object_repr", "reason", "request_id", "user__email"]
    readonly_fields = [
        "id",
        "organization",
        "branch",
        "user",
        "action",
        "module",
        "object_type",
        "object_id",
        "object_repr",
        "before_data",
        "after_data",
        "metadata",
        "reason",
        "ip_address",
        "user_agent",
        "request_id",
        "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
