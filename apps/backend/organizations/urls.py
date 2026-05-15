from rest_framework.routers import DefaultRouter

from .views import ApprovalRuleViewSet, BranchViewSet, OrganizationSettingViewSet, OrganizationViewSet, TaxRateViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("branches", BranchViewSet, basename="branch")
router.register("organization-settings", OrganizationSettingViewSet, basename="organization-setting")
router.register("tax-rates", TaxRateViewSet, basename="tax-rate")
router.register("approval-rules", ApprovalRuleViewSet, basename="approval-rule")

urlpatterns = router.urls
