from rest_framework import serializers

from .models import TeacherDeduction, TeacherEarning, TeacherPayment, TeacherPaymentAllocation, TeacherPaymentBatch


class TeacherEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherEarning
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TeacherPaymentBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPaymentBatch
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TeacherPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPayment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TeacherPaymentAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPaymentAllocation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TeacherDeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherDeduction
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
