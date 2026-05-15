from common.viewsets import BaseModelViewSet

from .models import ApprovalRule, Branch, Organization, OrganizationSetting, TaxRate
from .serializers import (
    ApprovalRuleSerializer,
    BranchSerializer,
    OrganizationSerializer,
    OrganizationSettingSerializer,
    TaxRateSerializer,
)


class OrganizationViewSet(BaseModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    search_fields = ("legal_name", "display_name", "registration_number", "vat_pan_number")
    ordering_fields = ("display_name", "created_at")


class BranchViewSet(BaseModelViewSet):
    queryset = Branch.objects.select_related("organization").all()
    serializer_class = BranchSerializer
    search_fields = ("code", "name", "email", "phone")
    ordering_fields = ("code", "name", "created_at")


class OrganizationSettingViewSet(BaseModelViewSet):
    queryset = OrganizationSetting.objects.select_related("organization").all()
    serializer_class = OrganizationSettingSerializer
    search_fields = ("key", "description")
    ordering_fields = ("key", "created_at")


class TaxRateViewSet(BaseModelViewSet):
    queryset = TaxRate.objects.select_related("organization").all()
    serializer_class = TaxRateSerializer
    search_fields = ("name", "tax_type")
    ordering_fields = ("name", "rate", "effective_from", "created_at")


class ApprovalRuleViewSet(BaseModelViewSet):
    queryset = ApprovalRule.objects.select_related("organization", "branch").all()
    serializer_class = ApprovalRuleSerializer
    search_fields = ("module_name", "action_name", "required_role", "escalation_role")
    ordering_fields = ("module_name", "action_name", "created_at")
