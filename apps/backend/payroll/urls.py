from rest_framework.routers import DefaultRouter

from .views import (
    TeacherDeductionViewSet,
    TeacherEarningViewSet,
    TeacherPaymentAllocationViewSet,
    TeacherPaymentBatchViewSet,
    TeacherPaymentViewSet,
)

router = DefaultRouter()
router.register("teacher-earnings", TeacherEarningViewSet, basename="teacher-earning")
router.register("teacher-payment-batches", TeacherPaymentBatchViewSet, basename="teacher-payment-batch")
router.register("teacher-payments", TeacherPaymentViewSet, basename="teacher-payment")
router.register("teacher-payment-allocations", TeacherPaymentAllocationViewSet, basename="teacher-payment-allocation")
router.register("teacher-deductions", TeacherDeductionViewSet, basename="teacher-deduction")

urlpatterns = router.urls
