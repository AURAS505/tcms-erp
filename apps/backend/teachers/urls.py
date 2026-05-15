from rest_framework.routers import DefaultRouter

from .views import TeacherActivityViewSet, TeacherContractViewSet, TeacherStatusHistoryViewSet, TeacherViewSet

router = DefaultRouter()
router.register("teachers", TeacherViewSet, basename="teacher")
router.register("teacher-contracts", TeacherContractViewSet, basename="teacher-contract")
router.register("teacher-activities", TeacherActivityViewSet, basename="teacher-activity")
router.register("teacher-status-history", TeacherStatusHistoryViewSet, basename="teacher-status-history")

urlpatterns = router.urls
