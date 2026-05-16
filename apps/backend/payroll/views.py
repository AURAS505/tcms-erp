from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from common.permissions import BranchScopedPermission, IsFinancialApprover, user_can_access_branch
from common.responses import api_success, validation_error_response
from common.viewsets import BaseReadOnlyModelViewSet

from .models import TeacherDeduction, TeacherEarning, TeacherPayment, TeacherPaymentAllocation, TeacherPaymentBatch
from .serializers import (
    EmptyPayrollActionSerializer,
    TeacherDeductionSerializer,
    TeacherEarningCreateSerializer,
    TeacherEarningSerializer,
    TeacherPaymentAllocationSerializer,
    TeacherPaymentBatchSerializer,
    TeacherPaymentDraftCreateSerializer,
    TeacherPaymentSerializer,
    TeacherPaymentVoidPlaceholderSerializer,
)
from .services import TeacherEarningService, TeacherPaymentService


def _validation_errors(exc: DjangoValidationError):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"non_field_errors": exc.messages}
    return {"non_field_errors": [str(exc)]}


def _query_param_is_true(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


class TeacherEarningViewSet(BaseReadOnlyModelViewSet):
    queryset = TeacherEarning.objects.select_related("organization", "branch", "academic_year", "academic_period", "teacher").all()
    serializer_class = TeacherEarningSerializer
    search_fields = ("teacher__employee_number", "teacher__full_name", "earning_source", "period_label")
    ordering_fields = ("earning_date_ad", "net_amount", "balance_amount", "created_at", "status")

    def get_queryset(self):
        queryset = super().get_queryset()
        teacher_id = self.request.query_params.get("teacher")
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if _query_param_is_true(self.request.query_params.get("open_only")):
            queryset = queryset.filter(
                status__in=[TeacherEarning.Status.POSTED, TeacherEarning.Status.PARTIAL],
                balance_amount__gt=0,
            )
        return queryset

    def get_permissions(self):
        if self.action in {"create_manual", "approve", "post"}:
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["post"], url_path="create-manual")
    def create_manual(self, request):
        serializer = TeacherEarningCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        data = serializer.validated_data
        if not user_can_access_branch(request.user, data["branch"].id, data["organization"].id):
            raise PermissionDenied("You do not have access to create earnings for this branch.")

        try:
            earning = TeacherEarningService.create_manual_earning(
                organization=data["organization"],
                branch=data["branch"],
                academic_year=data["academic_year"],
                teacher=data["teacher"],
                earning_date_ad=data["earning_date_ad"],
                gross_amount=data["gross_amount"],
                deduction_amount=data.get("deduction_amount", 0),
                net_amount=data.get("net_amount"),
                academic_period=data.get("academic_period"),
                earning_date_bs=data.get("earning_date_bs", ""),
                period_label=data.get("period_label", ""),
                earning_source=data.get("earning_source", TeacherEarning.EarningSource.MANUAL_ADJUSTMENT),
                created_by=request.user,
                notes=data.get("notes", ""),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            TeacherEarningSerializer(earning, context={"request": request}).data,
            message="Teacher earning created.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = EmptyPayrollActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        earning = self.get_object()
        try:
            earning = TeacherEarningService.approve_earning(earning_id=earning.id, approved_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(TeacherEarningSerializer(earning, context={"request": request}).data, message="Teacher earning approved.")

    @action(detail=True, methods=["post"], url_path="post")
    def post(self, request, pk=None):
        serializer = EmptyPayrollActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        earning = self.get_object()
        try:
            earning = TeacherEarningService.post_earning(earning_id=earning.id, posted_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(TeacherEarningSerializer(earning, context={"request": request}).data, message="Teacher earning posted.")


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

    def get_permissions(self):
        if self.action in {"create_draft", "approve", "post", "void_placeholder"}:
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @staticmethod
    def _allocation_payload(allocations):
        return [
            {
                "teacher_earning_id": str(allocation["teacher_earning"].id),
                "amount_allocated": allocation["amount_allocated"],
                "notes": allocation.get("notes", ""),
            }
            for allocation in allocations
        ]

    @action(detail=False, methods=["post"], url_path="create-draft")
    def create_draft(self, request):
        serializer = TeacherPaymentDraftCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        data = serializer.validated_data
        if not user_can_access_branch(request.user, data["branch"].id, data["organization"].id):
            raise PermissionDenied("You do not have access to create teacher payments for this branch.")

        try:
            payment = TeacherPaymentService.create_draft_payment(
                organization=data["organization"],
                branch=data["branch"],
                academic_year=data["academic_year"],
                teacher=data["teacher"],
                payment_date_ad=data["payment_date_ad"],
                payment_method=data["payment_method"],
                amount=data["amount"],
                created_by=request.user,
                academic_period=data.get("academic_period"),
                payment_batch=data.get("payment_batch"),
                payment_date_bs=data.get("payment_date_bs", ""),
                deduction_amount=data.get("deduction_amount", 0),
                net_paid_amount=data.get("net_paid_amount"),
                reference_number=data.get("reference_number", ""),
                acknowledgement_file_path=data.get("acknowledgement_file_path", ""),
                notes=data.get("notes", ""),
                allocations=self._allocation_payload(data.get("allocations", [])),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            TeacherPaymentSerializer(payment, context={"request": request}).data,
            message="Draft teacher payment created.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = EmptyPayrollActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        payment = self.get_object()
        try:
            payment = TeacherPaymentService.approve_payment(payment_id=payment.id, approved_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            TeacherPaymentSerializer(payment, context={"request": request}).data,
            message="Teacher payment approved and posted.",
        )

    @action(detail=True, methods=["post"], url_path="post")
    def post(self, request, pk=None):
        serializer = EmptyPayrollActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        payment = self.get_object()
        try:
            payment = TeacherPaymentService.post_payment(payment_id=payment.id, approved_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(TeacherPaymentSerializer(payment, context={"request": request}).data, message="Teacher payment posted.")

    @action(detail=True, methods=["post"], url_path="void-placeholder")
    def void_placeholder(self, request, pk=None):
        serializer = TeacherPaymentVoidPlaceholderSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        payment = self.get_object()
        try:
            payment = TeacherPaymentService.void_payment_placeholder(
                payment_id=payment.id,
                reason=serializer.validated_data["reason"],
                voided_by=request.user,
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            TeacherPaymentSerializer(payment, context={"request": request}).data,
            message="Teacher payment void placeholder recorded.",
        )


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
