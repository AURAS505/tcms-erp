from common.viewsets import BaseReadOnlyModelViewSet

from .models import TeacherDeduction, TeacherEarning, TeacherPayment, TeacherPaymentAllocation, TeacherPaymentBatch
from .serializers import (
    TeacherDeductionSerializer,
    TeacherEarningSerializer,
    TeacherPaymentAllocationSerializer,
    TeacherPaymentBatchSerializer,
    TeacherPaymentSerializer,
)


class TeacherEarningViewSet(BaseReadOnlyModelViewSet):
    queryset = TeacherEarning.objects.select_related("organization", "branch", "academic_year", "academic_period", "teacher").all()
    serializer_class = TeacherEarningSerializer
    search_fields = ("teacher__employee_number", "teacher__full_name", "earning_source", "period_label")
    ordering_fields = ("earning_date_ad", "net_amount", "balance_amount", "created_at", "status")


class TeacherPaymentBatchViewSet(BaseReadOnlyModelViewSet):
    queryset = TeacherPaymentBatch.objects.select_related("organization", "branch", "academic_year", "academic_period").all()
    serializer_class = TeacherPaymentBatchSerializer
    search_fields = ("batch_number", "description")
    ordering_fields = ("batch_date_ad", "total_amount", "created_at", "status")


class TeacherPaymentViewSet(BaseReadOnlyModelViewSet):
    queryset = TeacherPayment.objects.select_related("organization", "branch", "academic_year", "academic_period", "teacher").all()
    serializer_class = TeacherPaymentSerializer
    search_fields = ("voucher_number", "draft_voucher_number", "teacher__employee_number", "teacher__full_name")
    ordering_fields = ("payment_date_ad", "amount", "created_at", "status")


class TeacherPaymentAllocationViewSet(BaseReadOnlyModelViewSet):
    queryset = TeacherPaymentAllocation.objects.select_related("teacher_payment", "teacher_earning").all()
    serializer_class = TeacherPaymentAllocationSerializer
    search_fields = ("teacher_payment__voucher_number", "teacher_earning__teacher__employee_number")
    ordering_fields = ("amount_allocated", "created_at")


class TeacherDeductionViewSet(BaseReadOnlyModelViewSet):
    queryset = TeacherDeduction.objects.select_related("organization", "branch", "academic_year", "teacher").all()
    serializer_class = TeacherDeductionSerializer
    search_fields = ("teacher__employee_number", "teacher__full_name", "deduction_type", "reason")
    ordering_fields = ("amount", "created_at", "status")
