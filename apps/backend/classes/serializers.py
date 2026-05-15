from rest_framework import serializers

from .models import (
    ClassEnrollment,
    ClassEnrollmentBreak,
    ClassEnrollmentDiscount,
    ClassRoom,
    ClassSchedule,
    ClassTeacherTransfer,
    StudentWithdrawal,
    Subject,
)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClassEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassEnrollment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClassEnrollmentBreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassEnrollmentBreak
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClassEnrollmentDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassEnrollmentDiscount
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentWithdrawal
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClassTeacherTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTeacherTransfer
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
