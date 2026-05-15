from rest_framework.routers import DefaultRouter

from .views import (
    BillingDiscountViewSet,
    BillingFineViewSet,
    BillingWaiverViewSet,
    FeePlanItemViewSet,
    FeePlanViewSet,
    StudentAdvanceBalanceViewSet,
    StudentFeeDueViewSet,
    StudentInvoiceItemViewSet,
    StudentInvoiceViewSet,
    StudentPaymentAllocationViewSet,
    StudentPaymentViewSet,
    StudentRefundViewSet,
)

router = DefaultRouter()
router.register("fee-plans", FeePlanViewSet, basename="fee-plan")
router.register("fee-plan-items", FeePlanItemViewSet, basename="fee-plan-item")
router.register("student-fee-dues", StudentFeeDueViewSet, basename="student-fee-due")
router.register("student-invoices", StudentInvoiceViewSet, basename="student-invoice")
router.register("student-invoice-items", StudentInvoiceItemViewSet, basename="student-invoice-item")
router.register("student-payments", StudentPaymentViewSet, basename="student-payment")
router.register("student-payment-allocations", StudentPaymentAllocationViewSet, basename="student-payment-allocation")
router.register("student-advance-balances", StudentAdvanceBalanceViewSet, basename="student-advance-balance")
router.register("billing-discounts", BillingDiscountViewSet, basename="billing-discount")
router.register("billing-waivers", BillingWaiverViewSet, basename="billing-waiver")
router.register("billing-fines", BillingFineViewSet, basename="billing-fine")
router.register("student-refunds", StudentRefundViewSet, basename="student-refund")

urlpatterns = router.urls
