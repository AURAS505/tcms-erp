from rest_framework.routers import DefaultRouter

from .views import (
    StudentAcademicRecordViewSet,
    StudentDocumentViewSet,
    StudentInquiryViewSet,
    StudentNoteViewSet,
    StudentSchoolHistoryViewSet,
    StudentStatusHistoryViewSet,
    StudentViewSet,
)

router = DefaultRouter()
router.register("student-inquiries", StudentInquiryViewSet, basename="student-inquiry")
router.register("students", StudentViewSet, basename="student")
router.register("student-documents", StudentDocumentViewSet, basename="student-document")
router.register("student-academic-records", StudentAcademicRecordViewSet, basename="student-academic-record")
router.register("student-school-history", StudentSchoolHistoryViewSet, basename="student-school-history")
router.register("student-status-history", StudentStatusHistoryViewSet, basename="student-status-history")
router.register("student-notes", StudentNoteViewSet, basename="student-note")

urlpatterns = router.urls
