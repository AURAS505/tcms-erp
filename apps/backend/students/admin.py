from django.contrib import admin

from .models import (
    Student,
    StudentAcademicRecord,
    StudentDocument,
    StudentInquiry,
    StudentNote,
    StudentSchoolHistory,
    StudentStatusHistory,
)


@admin.register(StudentInquiry)
class StudentInquiryAdmin(admin.ModelAdmin):
    list_display = ["student_full_name", "guardian_name", "branch", "status", "contact_number", "created_at"]
    list_filter = ["organization", "branch", "academic_year", "status", "inquiry_source"]
    search_fields = ["student_full_name", "guardian_name", "contact_number", "email"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["admission_number", "full_name", "branch", "academic_year", "status", "phone"]
    list_filter = ["organization", "branch", "academic_year", "status", "gender"]
    search_fields = ["admission_number", "full_name", "preferred_name", "phone", "email"]


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ["student", "document_type", "academic_year", "file_name", "uploaded_by", "created_at"]
    list_filter = ["organization", "branch", "academic_year", "document_type"]
    search_fields = ["student__admission_number", "student__full_name", "file_name", "notes"]


@admin.register(StudentAcademicRecord)
class StudentAcademicRecordAdmin(admin.ModelAdmin):
    list_display = ["student", "institution_name", "level_grade", "result_type", "passed_year_bs", "passed_year_ad"]
    search_fields = ["student__admission_number", "student__full_name", "institution_name", "level_grade"]


@admin.register(StudentSchoolHistory)
class StudentSchoolHistoryAdmin(admin.ModelAdmin):
    list_display = ["student", "school_college_name", "level_class_attended", "start_date_ad", "end_date_ad"]
    search_fields = ["student__admission_number", "student__full_name", "school_college_name"]


@admin.register(StudentStatusHistory)
class StudentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["student", "from_status", "to_status", "changed_by", "changed_at"]
    list_filter = ["to_status", "changed_at"]
    search_fields = ["student__admission_number", "student__full_name", "reason"]


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ["student", "category", "title", "created_by", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["student__admission_number", "student__full_name", "title", "note"]
