from django.contrib import admin

from .models import ApprovalRule, Branch, Organization, OrganizationSetting, TaxRate


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["display_name", "legal_name", "default_currency", "email", "is_active"]
    list_filter = ["is_active", "default_currency"]
    search_fields = ["display_name", "legal_name", "registration_number", "vat_pan_number", "email"]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "organization", "is_main_branch", "is_active"]
    list_filter = ["organization", "is_main_branch", "is_active"]
    search_fields = ["name", "code", "organization__display_name", "email", "phone"]


@admin.register(OrganizationSetting)
class OrganizationSettingAdmin(admin.ModelAdmin):
    list_display = ["organization", "key", "is_system_setting"]
    list_filter = ["organization", "is_system_setting"]
    search_fields = ["organization__display_name", "key", "description"]


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "tax_type", "rate_percentage", "is_active", "effective_from", "effective_to"]
    list_filter = ["organization", "tax_type", "is_active"]
    search_fields = ["name", "organization__display_name", "notes"]


@admin.register(ApprovalRule)
class ApprovalRuleAdmin(admin.ModelAdmin):
    list_display = ["organization", "branch", "module_name", "action_name", "required_role", "escalation_role", "is_active"]
    list_filter = ["organization", "branch", "module_name", "is_active"]
    search_fields = ["organization__display_name", "branch__name", "module_name", "action_name"]
