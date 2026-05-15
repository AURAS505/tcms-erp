from rest_framework.routers import DefaultRouter

from .views import FamilyViewSet, GuardianViewSet, StudentGuardianViewSet

router = DefaultRouter()
router.register("families", FamilyViewSet, basename="family")
router.register("guardians", GuardianViewSet, basename="guardian")
router.register("student-guardians", StudentGuardianViewSet, basename="student-guardian")

urlpatterns = router.urls
