from django.contrib import admin

from .models import (
    ClassEnrollment,
    ClassEnrollmentBreak,
    ClassEnrollmentDiscount,
    ClassRoom,
    ClassSchedule,
    ClassTeacherTransfer,
    StudentWithdrawal,
    Subject,
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_code", "subject_name", "organization", "branch", "academic_year", "is_active")
    list_filter = ("organization", "branch", "academic_year", "is_active")
    search_fields = ("subject_code", "subject_name")


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("class_name", "batch_name", "section_name", "branch", "academic_year", "primary_teacher", "status")
    list_filter = ("organization", "branch", "academic_year", "status", "teacher_payment_type", "payment_due_rule")
    search_fields = ("class_name", "batch_name", "section_name", "primary_teacher__full_name")
    filter_horizontal = ("subjects",)


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ("class_room", "day_of_week", "start_time", "end_time", "room_name", "is_active")
    list_filter = ("day_of_week", "is_active")
    search_fields = ("class_room__class_name", "class_room__batch_name", "room_name")


@admin.register(ClassEnrollment)
class ClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "class_room", "academic_year", "status", "joined_date_ad")
    list_filter = ("organization", "branch", "academic_year", "status")
    search_fields = ("student__admission_number", "student__full_name", "class_room__class_name")


@admin.register(ClassEnrollmentBreak)
class ClassEnrollmentBreakAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "break_start_date_ad", "expected_return_date_ad", "status", "approved_by")
    list_filter = ("status", "break_start_date_ad")
    search_fields = ("enrollment__student__admission_number", "reason")


@admin.register(ClassEnrollmentDiscount)
class ClassEnrollmentDiscountAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "discount_type", "status", "discount_percentage", "discount_amount", "approved_by")
    list_filter = ("discount_type", "status")
    search_fields = ("enrollment__student__admission_number", "reason")


@admin.register(StudentWithdrawal)
class StudentWithdrawalAdmin(admin.ModelAdmin):
    list_display = ("student", "enrollment", "last_attendance_date_ad", "status", "approved_by")
    list_filter = ("organization", "branch", "academic_year", "status")
    search_fields = ("student__admission_number", "student__full_name", "reason")


@admin.register(ClassTeacherTransfer)
class ClassTeacherTransferAdmin(admin.ModelAdmin):
    list_display = ("class_room", "from_teacher", "to_teacher", "effective_date_ad", "status", "approved_by")
    list_filter = ("status", "effective_date_ad")
    search_fields = ("class_room__class_name", "from_teacher__full_name", "to_teacher__full_name", "reason")
