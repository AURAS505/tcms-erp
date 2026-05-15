from common.viewsets import BaseModelViewSet

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
from .serializers import (
    ClassEnrollmentBreakSerializer,
    ClassEnrollmentDiscountSerializer,
    ClassEnrollmentSerializer,
    ClassRoomSerializer,
    ClassScheduleSerializer,
    ClassTeacherTransferSerializer,
    StudentWithdrawalSerializer,
    SubjectSerializer,
)


class SubjectViewSet(BaseModelViewSet):
    queryset = Subject.objects.select_related("organization", "branch", "academic_year").all()
    serializer_class = SubjectSerializer
    search_fields = ("subject_code", "subject_name", "description")
    ordering_fields = ("subject_code", "subject_name", "created_at")


class ClassRoomViewSet(BaseModelViewSet):
    queryset = ClassRoom.objects.select_related("organization", "branch", "academic_year", "primary_teacher").prefetch_related("subjects").all()
    serializer_class = ClassRoomSerializer
    search_fields = ("class_name", "batch_name", "section_name", "primary_teacher__full_name")
    ordering_fields = ("class_name", "batch_name", "created_at", "start_date_ad")


class ClassScheduleViewSet(BaseModelViewSet):
    queryset = ClassSchedule.objects.select_related("class_room").all()
    serializer_class = ClassScheduleSerializer
    search_fields = ("class_room__class_name", "day_of_week", "room_name")
    ordering_fields = ("day_of_week", "start_time", "created_at")


class ClassEnrollmentViewSet(BaseModelViewSet):
    queryset = ClassEnrollment.objects.select_related("organization", "branch", "academic_year", "student", "class_room").all()
    serializer_class = ClassEnrollmentSerializer
    search_fields = ("student__admission_number", "student__full_name", "class_room__class_name")
    ordering_fields = ("joined_date_ad", "created_at", "status")


class ClassEnrollmentBreakViewSet(BaseModelViewSet):
    queryset = ClassEnrollmentBreak.objects.select_related("enrollment", "approved_by").all()
    serializer_class = ClassEnrollmentBreakSerializer
    search_fields = ("enrollment__student__admission_number", "reason", "status")
    ordering_fields = ("break_start_date_ad", "created_at", "status")


class ClassEnrollmentDiscountViewSet(BaseModelViewSet):
    queryset = ClassEnrollmentDiscount.objects.select_related("enrollment", "approved_by").all()
    serializer_class = ClassEnrollmentDiscountSerializer
    search_fields = ("enrollment__student__admission_number", "discount_type", "reason", "status")
    ordering_fields = ("effective_from_ad", "created_at", "status")


class StudentWithdrawalViewSet(BaseModelViewSet):
    queryset = StudentWithdrawal.objects.select_related("enrollment", "student", "organization", "branch", "academic_year").all()
    serializer_class = StudentWithdrawalSerializer
    search_fields = ("student__admission_number", "student__full_name", "reason", "status")
    ordering_fields = ("last_attendance_date_ad", "created_at", "status")


class ClassTeacherTransferViewSet(BaseModelViewSet):
    queryset = ClassTeacherTransfer.objects.select_related("class_room", "from_teacher", "to_teacher", "approved_by").all()
    serializer_class = ClassTeacherTransferSerializer
    search_fields = ("class_room__class_name", "from_teacher__full_name", "to_teacher__full_name", "reason", "status")
    ordering_fields = ("effective_date_ad", "created_at", "status")
