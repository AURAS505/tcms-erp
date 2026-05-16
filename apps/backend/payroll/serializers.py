from rest_framework import serializers

from academic.models import AcademicPeriod, AcademicYear
from common.money import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS
from organizations.models import Branch, Organization
from teachers.models import Teacher

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


class TeacherEarningCreateSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    earning_date_ad = serializers.DateField()
    gross_amount = serializers.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES)
    deduction_amount = serializers.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        required=False,
        default="0.00",
    )
    net_amount = serializers.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        required=False,
        allow_null=True,
    )
    academic_period = serializers.PrimaryKeyRelatedField(queryset=AcademicPeriod.objects.all(), required=False, allow_null=True)
    earning_date_bs = serializers.CharField(required=False, allow_blank=True, default="")
    period_label = serializers.CharField(required=False, allow_blank=True, default="")
    earning_source = serializers.ChoiceField(
        choices=TeacherEarning.EarningSource.choices,
        required=False,
        default=TeacherEarning.EarningSource.MANUAL_ADJUSTMENT,
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class EmptyPayrollActionSerializer(serializers.Serializer):
    pass


class TeacherPaymentAllocationInputSerializer(serializers.Serializer):
    teacher_earning = serializers.PrimaryKeyRelatedField(queryset=TeacherEarning.objects.all())
    amount_allocated = serializers.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class TeacherPaymentDraftCreateSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    payment_date_ad = serializers.DateField()
    payment_method = serializers.ChoiceField(choices=TeacherPayment.PaymentMethod.choices)
    amount = serializers.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES)
    deduction_amount = serializers.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        required=False,
        default="0.00",
    )
    net_paid_amount = serializers.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        required=False,
        allow_null=True,
    )
    academic_period = serializers.PrimaryKeyRelatedField(queryset=AcademicPeriod.objects.all(), required=False, allow_null=True)
    payment_batch = serializers.PrimaryKeyRelatedField(queryset=TeacherPaymentBatch.objects.all(), required=False, allow_null=True)
    payment_date_bs = serializers.CharField(required=False, allow_blank=True, default="")
    reference_number = serializers.CharField(required=False, allow_blank=True, default="")
    acknowledgement_file_path = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    allocations = TeacherPaymentAllocationInputSerializer(many=True, required=False, default=list)


class TeacherPaymentVoidPlaceholderSerializer(serializers.Serializer):
    reason = serializers.CharField()


class TeacherDeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherDeduction
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
