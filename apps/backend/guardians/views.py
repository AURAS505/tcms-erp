from common.viewsets import BaseModelViewSet

from .models import Family, Guardian, StudentGuardian
from .serializers import FamilySerializer, GuardianSerializer, StudentGuardianSerializer


class FamilyViewSet(BaseModelViewSet):
    queryset = Family.objects.select_related("organization", "branch").all()
    serializer_class = FamilySerializer
    search_fields = ("family_code", "primary_contact_name", "primary_contact_number")
    ordering_fields = ("family_code", "primary_contact_name", "created_at")


class GuardianViewSet(BaseModelViewSet):
    queryset = Guardian.objects.select_related("organization", "branch", "family").all()
    serializer_class = GuardianSerializer
    search_fields = ("full_name", "phone", "alternate_phone", "email", "occupation")
    ordering_fields = ("full_name", "created_at")


class StudentGuardianViewSet(BaseModelViewSet):
    queryset = StudentGuardian.objects.select_related("student", "guardian").all()
    serializer_class = StudentGuardianSerializer
    search_fields = ("student__admission_number", "student__full_name", "guardian__full_name", "relationship_type")
    ordering_fields = ("created_at",)
