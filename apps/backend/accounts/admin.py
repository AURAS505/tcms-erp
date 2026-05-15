from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import LoginSession, PasswordResetToken, Permission, Role, RolePermission, User, UserBranchAssignment, UserRole


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["email"]
    list_display = ["email", "username", "first_name", "last_name", "status", "is_staff", "force_password_change"]
    list_filter = ["status", "is_active", "is_staff", "is_superuser", "force_password_change"]
    search_fields = ["email", "username", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Status", {"fields": ("status", "is_active", "force_password_change")}),
        ("Admin access", {"fields": ("is_staff", "is_superuser")}),
        ("Login metadata", {"fields": ("last_login", "last_login_ip")}),
        ("Important dates", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
    readonly_fields = ["created_at", "updated_at", "last_login"]
    filter_horizontal = ()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_system", "is_read_only", "is_active"]
    list_filter = ["is_system", "is_read_only", "is_active"]
    search_fields = ["code", "name"]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "module", "is_read_only", "is_active"]
    list_filter = ["module", "is_read_only", "is_active"]
    search_fields = ["code", "name", "module"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "is_active", "assigned_at"]
    list_filter = ["role", "is_active"]
    search_fields = ["user__email", "role__name", "role__code"]


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ["role", "permission", "is_active", "assigned_at"]
    list_filter = ["role", "permission__module", "is_active"]
    search_fields = ["role__name", "permission__code", "permission__name"]


@admin.register(UserBranchAssignment)
class UserBranchAssignmentAdmin(admin.ModelAdmin):
    list_display = ["user", "organization_id", "branch_id", "is_primary", "is_active", "assigned_at"]
    list_filter = ["is_primary", "is_active"]
    search_fields = ["user__email", "organization_id", "branch_id"]


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "expires_at", "used_at", "created_at"]
    search_fields = ["user__email", "token_hash"]
    readonly_fields = ["token_hash", "created_at", "updated_at"]


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "created_from", "ip_address", "expires_at", "revoked_at", "last_seen_at"]
    search_fields = ["user__email", "session_key_hash", "ip_address"]
    readonly_fields = ["session_key_hash", "created_at", "updated_at"]
