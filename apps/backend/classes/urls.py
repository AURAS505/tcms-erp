from rest_framework.routers import DefaultRouter

from .views import (
    ClassEnrollmentBreakViewSet,
    ClassEnrollmentDiscountViewSet,
    ClassEnrollmentViewSet,
    ClassRoomViewSet,
    ClassScheduleViewSet,
    ClassTeacherTransferViewSet,
    StudentWithdrawalViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register("subjects", SubjectViewSet, basename="subject")
router.register("classes", ClassRoomViewSet, basename="class-room")
router.register("class-schedules", ClassScheduleViewSet, basename="class-schedule")
router.register("class-enrollments", ClassEnrollmentViewSet, basename="class-enrollment")
router.register("class-enrollment-breaks", ClassEnrollmentBreakViewSet, basename="class-enrollment-break")
router.register("class-enrollment-discounts", ClassEnrollmentDiscountViewSet, basename="class-enrollment-discount")
router.register("student-withdrawals", StudentWithdrawalViewSet, basename="student-withdrawal")
router.register("class-teacher-transfers", ClassTeacherTransferViewSet, basename="class-teacher-transfer")

urlpatterns = router.urls
