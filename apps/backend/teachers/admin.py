from django.contrib import admin

from .models import Teacher, TeacherActivity, TeacherContract, TeacherStatusHistory


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("employee_number", "full_name", "organization", "branch", "status", "phone")
    list_filter = ("organization", "branch", "status", "gender")
    search_fields = ("employee_number", "full_name", "phone", "email")


@admin.register(TeacherContract)
class TeacherContractAdmin(admin.ModelAdmin):
    list_display = ("teacher", "contract_type", "academic_year", "is_active", "effective_from_ad", "effective_to_ad")
    list_filter = ("contract_type", "is_active", "organization", "branch", "academic_year")
    search_fields = ("teacher__employee_number", "teacher__full_name")


@admin.register(TeacherActivity)
class TeacherActivityAdmin(admin.ModelAdmin):
    list_display = ("teacher", "activity_type", "title", "status", "activity_date_ad", "created_by")
    list_filter = ("activity_type", "status", "organization", "branch", "academic_year")
    search_fields = ("teacher__employee_number", "teacher__full_name", "title")


@admin.register(TeacherStatusHistory)
class TeacherStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("teacher", "from_status", "to_status", "changed_by", "changed_at")
    list_filter = ("to_status", "changed_at")
    search_fields = ("teacher__employee_number", "teacher__full_name", "reason")
