from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from common.permissions import BranchScopedPermission, IsFinancialApprover, IsPaymentDraftCreator, user_can_access_branch
from common.responses import api_success, validation_error_response
from common.viewsets import BaseModelViewSet, BaseReadOnlyModelViewSet

from .models import (
    BillingDiscount,
    BillingFine,
    BillingWaiver,
    BillStatus,
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
from .serializers import (
    AdvanceApplicationToDueSerializer,
    AdvanceApplicationToInvoiceSerializer,
    BillingDiscountSerializer,
    BillingFineSerializer,
    BillingWaiverSerializer,
    EmptyActionSerializer,
    FeePlanItemSerializer,
    FeePlanSerializer,
    StudentAdvanceBalanceSerializer,
    StudentFeeDueSerializer,
    StudentInvoiceItemSerializer,
    StudentInvoiceSerializer,
    StudentPaymentApproveSerializer,
    StudentPaymentAllocationSerializer,
    StudentPaymentDraftCreateSerializer,
    StudentPaymentSerializer,
    StudentPaymentVoidPlaceholderSerializer,
    StudentRefundSerializer,
)
from .services import AdvanceApplicationService, BillingAdjustmentService, StudentPaymentService, StudentRefundService

OPEN_OBLIGATION_STATUSES = (BillStatus.APPROVED, BillStatus.UNPAID, BillStatus.PARTIAL)


def _validation_errors(exc: DjangoValidationError):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"non_field_errors": exc.messages}
    return {"non_field_errors": [str(exc)]}


def _query_param_is_true(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


class FeePlanViewSet(BaseModelViewSet):
    queryset = FeePlan.objects.select_related("organization", "branch", "academic_year", "class_room").all()
    serializer_class = FeePlanSerializer
    search_fields = ("name", "class_room__class_name")
    ordering_fields = ("name", "created_at")


class FeePlanItemViewSet(BaseModelViewSet):
    queryset = FeePlanItem.objects.select_related("fee_plan").all()
    serializer_class = FeePlanItemSerializer
    search_fields = ("item_name", "fee_type", "fee_plan__name")
    ordering_fields = ("sort_order", "amount", "created_at")


class StudentFeeDueViewSet(BaseReadOnlyModelViewSet):
    queryset = StudentFeeDue.objects.select_related("organization", "branch", "academic_year", "academic_period", "student").all()
    serializer_class = StudentFeeDueSerializer
    search_fields = ("student__admission_number", "student__full_name", "period_label")
    ordering_fields = ("due_date_ad", "balance_amount", "created_at", "status")

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get("student")
        academic_period_id = self.request.query_params.get("academic_period")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(academic_period_id=academic_period_id)
        if _query_param_is_true(self.request.query_params.get("open_only")):
            queryset = queryset.filter(status__in=OPEN_OBLIGATION_STATUSES, balance_amount__gt=0)
        return queryset


class StudentInvoiceViewSet(BaseReadOnlyModelViewSet):
    queryset = StudentInvoice.objects.select_related("organization", "branch", "academic_year", "academic_period", "student").all()
    serializer_class = StudentInvoiceSerializer
    search_fields = ("invoice_number", "student__admission_number", "student__full_name")
    ordering_fields = ("invoice_date_ad", "due_date_ad", "balance_amount", "created_at", "status")

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get("student")
        academic_period_id = self.request.query_params.get("academic_period")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(academic_period_id=academic_period_id)
        if _query_param_is_true(self.request.query_params.get("open_only")):
            queryset = queryset.filter(status__in=OPEN_OBLIGATION_STATUSES, balance_amount__gt=0)
        return queryset


class StudentInvoiceItemViewSet(BaseReadOnlyModelViewSet):
    queryset = StudentInvoiceItem.objects.select_related("invoice", "fee_due").all()
    serializer_class = StudentInvoiceItemSerializer
    search_fields = ("invoice__invoice_number", "description", "fee_type")
    ordering_fields = ("created_at", "line_total")


class StudentPaymentViewSet(BaseReadOnlyModelViewSet):
    queryset = StudentPayment.objects.select_related("organization", "branch", "academic_year", "student").all()
    serializer_class = StudentPaymentSerializer
    search_fields = ("receipt_number", "draft_receipt_number", "student__admission_number", "student__full_name")
    ordering_fields = ("payment_date_ad", "amount", "created_at", "status")

    def get_permissions(self):
        if self.action == "create_draft":
            permission_classes = [BranchScopedPermission, IsPaymentDraftCreator]
        elif self.action in {"approve", "void_placeholder"}:
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return super().get_queryset().prefetch_related("allocations")

    @staticmethod
    def _allocation_payload(allocations):
        payload = []
        for allocation in allocations:
            payload.append(
                {
                    "fee_due_id": str(allocation["fee_due"].id) if allocation.get("fee_due") else None,
                    "invoice_id": str(allocation["invoice"].id) if allocation.get("invoice") else None,
                    "invoice_item_id": str(allocation["invoice_item"].id) if allocation.get("invoice_item") else None,
                    "amount_allocated": allocation["amount_allocated"],
                    "notes": allocation.get("notes", ""),
                }
            )
        return payload

    @action(detail=False, methods=["post"], url_path="create-draft")
    def create_draft(self, request):
        serializer = StudentPaymentDraftCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        data = serializer.validated_data
        if not user_can_access_branch(request.user, data["branch"].id, data["organization"].id):
            raise PermissionDenied("You do not have access to create payments for this branch.")

        try:
            payment = StudentPaymentService.create_draft_payment(
                organization=data["organization"],
                branch=data["branch"],
                academic_year=data["academic_year"],
                student=data["student"],
                payment_date_ad=data["payment_date_ad"],
                payment_method=data["payment_method"],
                amount=data["amount"],
                created_by=request.user,
                payment_date_bs=data.get("payment_date_bs", ""),
                discount_amount=data.get("discount_amount", 0),
                fine_amount=data.get("fine_amount", 0),
                net_received_amount=data.get("net_received_amount"),
                is_advance_payment=data.get("is_advance_payment", False),
                reference_number=data.get("reference_number", ""),
                file_path=data.get("file_path", ""),
                notes=data.get("notes", ""),
                allocations=self._allocation_payload(data.get("allocations", [])),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            StudentPaymentSerializer(payment, context={"request": request}).data,
            message="Draft payment created.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = StudentPaymentApproveSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        payment = self.get_object()
        try:
            payment = StudentPaymentService.approve_payment(payment_id=payment.id, approved_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            StudentPaymentSerializer(payment, context={"request": request}).data,
            message="Payment approved and posted.",
        )

    @action(detail=True, methods=["post"], url_path="void-placeholder")
    def void_placeholder(self, request, pk=None):
        serializer = StudentPaymentVoidPlaceholderSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        payment = self.get_object()
        try:
            payment = StudentPaymentService.void_payment_placeholder(
                payment_id=payment.id,
                reason=serializer.validated_data["reason"],
                voided_by=request.user,
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            StudentPaymentSerializer(payment, context={"request": request}).data,
            message="Payment void placeholder recorded.",
        )


class StudentPaymentAllocationViewSet(BaseReadOnlyModelViewSet):
    queryset = StudentPaymentAllocation.objects.select_related("payment", "fee_due", "invoice", "invoice_item").all()
    serializer_class = StudentPaymentAllocationSerializer
    search_fields = ("payment__receipt_number", "payment__draft_receipt_number", "invoice__invoice_number")
    ordering_fields = ("created_at", "amount_allocated")


class StudentAdvanceBalanceViewSet(BaseReadOnlyModelViewSet):
    queryset = StudentAdvanceBalance.objects.select_related("organization", "branch", "academic_year", "student").all()
    serializer_class = StudentAdvanceBalanceSerializer
    search_fields = ("student__admission_number", "student__full_name")
    ordering_fields = ("balance_amount", "created_at")

    def get_permissions(self):
        if self.action in {"apply_to_due", "apply_to_invoice"}:
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["post"], url_path="apply-to-due")
    def apply_to_due(self, request):
        serializer = AdvanceApplicationToDueSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        due = serializer.validated_data["due"]
        if not user_can_access_branch(request.user, due.branch_id, due.organization_id):
            raise PermissionDenied("You do not have access to apply advances for this branch.")

        try:
            due = AdvanceApplicationService.apply_advance_to_due(
                student=serializer.validated_data["student"],
                due_id=due.id,
                amount=serializer.validated_data["amount"],
                applied_by=request.user,
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            StudentFeeDueSerializer(due, context={"request": request}).data,
            message="Advance applied to due.",
        )

    @action(detail=False, methods=["post"], url_path="apply-to-invoice")
    def apply_to_invoice(self, request):
        serializer = AdvanceApplicationToInvoiceSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        invoice = serializer.validated_data["invoice"]
        if not user_can_access_branch(request.user, invoice.branch_id, invoice.organization_id):
            raise PermissionDenied("You do not have access to apply advances for this branch.")

        try:
            invoice = AdvanceApplicationService.apply_advance_to_invoice(
                student=serializer.validated_data["student"],
                invoice_id=invoice.id,
                amount=serializer.validated_data["amount"],
                applied_by=request.user,
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            StudentInvoiceSerializer(invoice, context={"request": request}).data,
            message="Advance applied to invoice.",
        )


class BillingDiscountViewSet(BaseReadOnlyModelViewSet):
    queryset = BillingDiscount.objects.select_related("organization", "branch", "academic_year", "student").all()
    serializer_class = BillingDiscountSerializer
    search_fields = ("student__admission_number", "student__full_name", "discount_type", "reason")
    ordering_fields = ("created_at", "status")

    def get_permissions(self):
        if self.action == "approve":
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = EmptyActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        discount = self.get_object()
        try:
            discount = BillingAdjustmentService.approve_discount(discount_id=discount.id, approved_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            BillingDiscountSerializer(discount, context={"request": request}).data,
            message="Discount approved.",
        )


class BillingWaiverViewSet(BaseReadOnlyModelViewSet):
    queryset = BillingWaiver.objects.select_related("organization", "branch", "academic_year", "student").all()
    serializer_class = BillingWaiverSerializer
    search_fields = ("student__admission_number", "student__full_name", "reason")
    ordering_fields = ("created_at", "status")

    def get_permissions(self):
        if self.action == "approve":
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = EmptyActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        waiver = self.get_object()
        try:
            waiver = BillingAdjustmentService.approve_waiver(waiver_id=waiver.id, approved_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            BillingWaiverSerializer(waiver, context={"request": request}).data,
            message="Waiver approved.",
        )


class BillingFineViewSet(BaseReadOnlyModelViewSet):
    queryset = BillingFine.objects.select_related("organization", "branch", "academic_year", "student").all()
    serializer_class = BillingFineSerializer
    search_fields = ("student__admission_number", "student__full_name", "fine_type", "reason")
    ordering_fields = ("created_at", "status")

    def get_permissions(self):
        if self.action == "approve":
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = EmptyActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        fine = self.get_object()
        try:
            fine = BillingAdjustmentService.approve_fine(fine_id=fine.id, approved_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            BillingFineSerializer(fine, context={"request": request}).data,
            message="Fine approved.",
        )


class StudentRefundViewSet(BaseReadOnlyModelViewSet):
    queryset = StudentRefund.objects.select_related("organization", "branch", "academic_year", "student").all()
    serializer_class = StudentRefundSerializer
    search_fields = ("refund_voucher_number", "student__admission_number", "student__full_name", "refund_reason")
    ordering_fields = ("refund_date_ad", "refund_amount", "created_at", "status")

    def get_permissions(self):
        if self.action in {"approve", "pay"}:
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = EmptyActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        refund = self.get_object()
        try:
            refund = StudentRefundService.approve_refund(refund_id=refund.id, approved_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            StudentRefundSerializer(refund, context={"request": request}).data,
            message="Refund approved.",
        )

    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        serializer = EmptyActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        refund = self.get_object()
        try:
            refund = StudentRefundService.pay_refund(refund_id=refund.id, paid_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))

        return api_success(
            StudentRefundSerializer(refund, context={"request": request}).data,
            message="Refund paid.",
        )
