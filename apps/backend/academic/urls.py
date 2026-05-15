from rest_framework.routers import DefaultRouter

from .views import AcademicPeriodViewSet, AcademicYearRolloverViewSet, AcademicYearViewSet, NepaliCalendarDayViewSet

router = DefaultRouter()
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("academic-periods", AcademicPeriodViewSet, basename="academic-period")
router.register("nepali-calendar-days", NepaliCalendarDayViewSet, basename="nepali-calendar-day")
router.register("academic-year-rollovers", AcademicYearRolloverViewSet, basename="academic-year-rollover")

urlpatterns = router.urls
