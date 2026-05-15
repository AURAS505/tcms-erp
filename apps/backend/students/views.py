from common.viewsets import BaseModelViewSet, BaseReadOnlyModelViewSet

from .models import (
    Student,
    StudentAcademicRecord,
    StudentDocument,
    StudentInquiry,
    StudentNote,
    StudentSchoolHistory,
    StudentStatusHistory,
)
from .serializers import (
    StudentAcademicRecordSerializer,
    StudentDocumentSerializer,
    StudentInquirySerializer,
    StudentNoteSerializer,
    StudentSchoolHistorySerializer,
    StudentSerializer,
    StudentStatusHistorySerializer,
)


class StudentInquiryViewSet(BaseModelViewSet):
    queryset = StudentInquiry.objects.select_related("organization", "branch", "academic_year", "created_by").all()
    serializer_class = StudentInquirySerializer
    search_fields = ("student_full_name", "guardian_name", "contact_number", "email", "interested_class_subject")
    ordering_fields = ("student_full_name", "created_at", "inquiry_status")


class StudentViewSet(BaseModelViewSet):
    queryset = Student.objects.select_related("organization", "branch", "academic_year", "approved_by").all()
    serializer_class = StudentSerializer
    search_fields = ("admission_number", "full_name", "preferred_name", "phone", "email")
    ordering_fields = ("admission_number", "full_name", "created_at", "admission_date_ad")


class StudentDocumentViewSet(BaseModelViewSet):
    queryset = StudentDocument.objects.select_related("organization", "branch", "academic_year", "student", "uploaded_by").all()
    serializer_class = StudentDocumentSerializer
    search_fields = ("document_type", "file_name", "student__admission_number", "student__full_name")
    ordering_fields = ("document_type", "created_at")


class StudentAcademicRecordViewSet(BaseModelViewSet):
    queryset = StudentAcademicRecord.objects.select_related("student").all()
    serializer_class = StudentAcademicRecordSerializer
    search_fields = ("student__admission_number", "institution_name", "board_university", "level_grade")
    ordering_fields = ("passed_year_ad", "created_at")


class StudentSchoolHistoryViewSet(BaseModelViewSet):
    queryset = StudentSchoolHistory.objects.select_related("student").all()
    serializer_class = StudentSchoolHistorySerializer
    search_fields = ("student__admission_number", "school_college_name", "level_class_attended")
    ordering_fields = ("start_date_ad", "end_date_ad", "created_at")


class StudentStatusHistoryViewSet(BaseReadOnlyModelViewSet):
    queryset = StudentStatusHistory.objects.select_related("student", "changed_by").all()
    serializer_class = StudentStatusHistorySerializer
    search_fields = ("student__admission_number", "to_status", "reason")
    ordering_fields = ("changed_at", "created_at")


class StudentNoteViewSet(BaseModelViewSet):
    queryset = StudentNote.objects.select_related("student", "created_by").all()
    serializer_class = StudentNoteSerializer
    search_fields = ("student__admission_number", "category", "title", "note")
    ordering_fields = ("category", "created_at")
