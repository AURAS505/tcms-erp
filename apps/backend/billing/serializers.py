from rest_framework import serializers

from .models import (
    BillingDiscount,
    BillingFine,
    BillingWaiver,
    FeePlan,
    FeePlanItem,
    StudentAdvanceBalance,
    StudentFeeDue,
    StudentInvoice,
    StudentInvoiceItem,
    StudentPayment,
    StudentPaymentAllocation,
    StudentRefund,
)


class FeePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePlan
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FeePlanItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePlanItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentFeeDueSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeDue
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInvoice
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInvoiceItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPayment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentPaymentAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPaymentAllocation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentAdvanceBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAdvanceBalance
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BillingDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingDiscount
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BillingWaiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingWaiver
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BillingFineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingFine
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRefund
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
