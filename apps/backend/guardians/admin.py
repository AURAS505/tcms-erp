from django.contrib import admin

from .models import Family, Guardian, StudentGuardian


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ["family_code", "primary_contact_name", "primary_contact_number", "branch", "is_active"]
    list_filter = ["organization", "branch", "is_active"]
    search_fields = ["family_code", "primary_contact_name", "primary_contact_number"]


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ["full_name", "relationship_type", "phone", "branch", "family", "is_primary_contact", "is_active"]
    list_filter = ["organization", "branch", "relationship_type", "is_primary_contact", "is_active"]
    search_fields = ["full_name", "phone", "alternate_phone", "email"]


@admin.register(StudentGuardian)
class StudentGuardianAdmin(admin.ModelAdmin):
    list_display = ["student", "guardian", "relationship_type", "is_primary", "can_make_payments", "can_request_refunds"]
    list_filter = ["relationship_type", "is_primary", "can_receive_notifications", "can_make_payments", "can_request_refunds"]
    search_fields = ["student__admission_number", "student__full_name", "guardian__full_name", "guardian__phone"]
