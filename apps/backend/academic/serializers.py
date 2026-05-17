from rest_framework import serializers

from organizations.models import Organization

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


class RolloverNewAcademicYearSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    bs_start_year = serializers.IntegerField(min_value=1)
    bs_end_year = serializers.IntegerField(min_value=1)
    bs_start_date = serializers.CharField(max_length=10)
    bs_end_date = serializers.CharField(max_length=10)
    ad_start_date = serializers.DateField()
    ad_end_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True)


class AcademicYearRolloverPrepareSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    from_academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    notes = serializers.CharField(required=False, allow_blank=True)


class AcademicYearRolloverValidateSerializer(serializers.Serializer):
    pass


class AcademicYearRolloverExecuteSerializer(serializers.Serializer):
    new_year_data = RolloverNewAcademicYearSerializer(required=False)
    hard_close = serializers.BooleanField(required=False, default=True)


class AcademicYearRolloverCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class AcademicYearCloseSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
