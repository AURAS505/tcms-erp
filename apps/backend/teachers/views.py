from common.viewsets import BaseModelViewSet, BaseReadOnlyModelViewSet

from .models import Teacher, TeacherActivity, TeacherContract, TeacherStatusHistory
from .serializers import TeacherActivitySerializer, TeacherContractSerializer, TeacherSerializer, TeacherStatusHistorySerializer


class TeacherViewSet(BaseModelViewSet):
    queryset = Teacher.objects.select_related("organization", "branch", "user").all()
    serializer_class = TeacherSerializer
    search_fields = ("employee_number", "full_name", "phone", "email", "specialization")
    ordering_fields = ("employee_number", "full_name", "created_at", "joining_date_ad")


class TeacherContractViewSet(BaseModelViewSet):
    queryset = TeacherContract.objects.select_related("teacher", "organization", "branch", "academic_year").all()
    serializer_class = TeacherContractSerializer
    search_fields = ("teacher__employee_number", "teacher__full_name", "contract_type")
    ordering_fields = ("effective_from_ad", "effective_to_ad", "created_at")


class TeacherActivityViewSet(BaseModelViewSet):
    queryset = TeacherActivity.objects.select_related("teacher", "organization", "branch", "academic_year", "created_by").all()
    serializer_class = TeacherActivitySerializer
    search_fields = ("teacher__employee_number", "teacher__full_name", "activity_type", "title", "description")
    ordering_fields = ("activity_date_ad", "created_at", "status")


class TeacherStatusHistoryViewSet(BaseReadOnlyModelViewSet):
    queryset = TeacherStatusHistory.objects.select_related("teacher", "changed_by").all()
    serializer_class = TeacherStatusHistorySerializer
    search_fields = ("teacher__employee_number", "teacher__full_name", "to_status", "reason")
    ordering_fields = ("changed_at", "created_at")
