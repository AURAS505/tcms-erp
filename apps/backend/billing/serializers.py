from rest_framework import serializers

from academic.models import AcademicYear
from common.money import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS
from organizations.models import Branch, Organization
from students.models import Student

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


class StudentPaymentAllocationInputSerializer(serializers.Serializer):
    fee_due = serializers.PrimaryKeyRelatedField(queryset=StudentFeeDue.objects.all(), required=False, allow_null=True)
    invoice = serializers.PrimaryKeyRelatedField(queryset=StudentInvoice.objects.all(), required=False, allow_null=True)
    invoice_item = serializers.PrimaryKeyRelatedField(queryset=StudentInvoiceItem.objects.all(), required=False, allow_null=True)
    amount_allocated = serializers.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        target_count = sum(1 for field in ("fee_due", "invoice", "invoice_item") if attrs.get(field))
        if target_count != 1:
            raise serializers.ValidationError("Each allocation must target exactly one due, invoice, or invoice item.")
        return attrs


class StudentPaymentDraftCreateSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    payment_date_ad = serializers.DateField()
    payment_date_bs = serializers.CharField(required=False, allow_blank=True, default="")
    payment_method = serializers.ChoiceField(choices=StudentPayment.PaymentMethod.choices)
    amount = serializers.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES)
    discount_amount = serializers.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        required=False,
        default="0.00",
    )
    fine_amount = serializers.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        required=False,
        default="0.00",
    )
    net_received_amount = serializers.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        required=False,
        allow_null=True,
    )
    is_advance_payment = serializers.BooleanField(required=False, default=False)
    reference_number = serializers.CharField(required=False, allow_blank=True, default="")
    file_path = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    allocations = StudentPaymentAllocationInputSerializer(many=True, required=False, default=list)


class StudentPaymentApproveSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class StudentPaymentVoidPlaceholderSerializer(serializers.Serializer):
    reason = serializers.CharField()


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
