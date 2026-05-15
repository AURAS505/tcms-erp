from common.viewsets import BaseModelViewSet, BaseReadOnlyModelViewSet

from .models import AcademicPeriod, AcademicYear, AcademicYearRollover, NepaliCalendarDay
from .serializers import (
    AcademicPeriodSerializer,
    AcademicYearRolloverSerializer,
    AcademicYearSerializer,
    NepaliCalendarDaySerializer,
)


class AcademicYearViewSet(BaseModelViewSet):
    queryset = AcademicYear.objects.select_related("organization").all()
    serializer_class = AcademicYearSerializer
    search_fields = ("name", "bs_start_date", "bs_end_date")
    ordering_fields = ("name", "ad_start_date", "ad_end_date", "created_at")


class AcademicPeriodViewSet(BaseModelViewSet):
    queryset = AcademicPeriod.objects.select_related("organization", "academic_year").all()
    serializer_class = AcademicPeriodSerializer
    search_fields = ("name", "bs_month_name", "bs_start_date", "bs_end_date")
    ordering_fields = ("period_order", "ad_start_date", "ad_end_date", "created_at")


class NepaliCalendarDayViewSet(BaseReadOnlyModelViewSet):
    queryset = NepaliCalendarDay.objects.all()
    serializer_class = NepaliCalendarDaySerializer
    search_fields = ("bs_date", "bs_month_name")
    ordering_fields = ("ad_date", "bs_year", "bs_month", "bs_day")


class AcademicYearRolloverViewSet(BaseReadOnlyModelViewSet):
    queryset = AcademicYearRollover.objects.select_related("organization", "from_academic_year", "to_academic_year").all()
    serializer_class = AcademicYearRolloverSerializer
    search_fields = ("from_academic_year__name", "to_academic_year__name", "notes")
    ordering_fields = ("created_at", "executed_at", "status")
