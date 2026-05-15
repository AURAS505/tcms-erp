from rest_framework import serializers

from .models import AcademicPeriod, AcademicYear, AcademicYearRollover, NepaliCalendarDay


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AcademicPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPeriod
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class NepaliCalendarDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = NepaliCalendarDay
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AcademicYearRolloverSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYearRollover
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
