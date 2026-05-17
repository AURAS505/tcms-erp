from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from accounts.models import Role
from common.permissions import BranchScopedPermission, IsFinancialApprover, user_has_any_role, user_has_global_branch_access
from common.responses import api_success, validation_error_response
from common.viewsets import BaseModelViewSet, BaseReadOnlyModelViewSet

from .models import AcademicPeriod, AcademicYear, AcademicYearRollover, NepaliCalendarDay
from .serializers import (
    AcademicYearCloseSerializer,
    AcademicPeriodSerializer,
    AcademicYearRolloverCancelSerializer,
    AcademicYearRolloverExecuteSerializer,
    AcademicYearRolloverPrepareSerializer,
    AcademicYearRolloverSerializer,
    AcademicYearRolloverValidateSerializer,
    AcademicYearSerializer,
    NepaliCalendarDaySerializer,
)
from .services import AcademicYearRolloverService


def _validation_errors(exc: DjangoValidationError):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"non_field_errors": exc.messages}
    return {"non_field_errors": [str(exc)]}


def _has_active_branch_scope(user) -> bool:
    return user.branch_assignments.filter(is_active=True).exists()


def _ensure_org_rollover_operator(user):
    if user_has_global_branch_access(user):
        return
    if user_has_any_role(user, [Role.RoleCode.ACCOUNTANT]) and not _has_active_branch_scope(user):
        return
    raise PermissionDenied("Organization-wide rollover actions require organization-wide financial access.")


def _ensure_hard_close_operator(user):
    if user_has_any_role(user, [Role.RoleCode.SUPER_ADMIN, Role.RoleCode.INSTITUTE_OWNER]):
        return
    raise PermissionDenied("Hard close requires Super Admin or Institute Owner access.")


class AcademicYearViewSet(BaseModelViewSet):
    queryset = AcademicYear.objects.select_related("organization").all()
    serializer_class = AcademicYearSerializer
    search_fields = ("name", "bs_start_date", "bs_end_date")
    ordering_fields = ("name", "ad_start_date", "ad_end_date", "created_at")

    def get_permissions(self):
        if self.action in {"soft_close", "hard_close"}:
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"], url_path="soft-close")
    def soft_close(self, request, pk=None):
        serializer = AcademicYearCloseSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        _ensure_org_rollover_operator(request.user)
        academic_year = self.get_object()
        try:
            academic_year = AcademicYearRolloverService.soft_close_academic_year(
                academic_year_id=academic_year.id,
                closed_by=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(AcademicYearSerializer(academic_year, context={"request": request}).data, message="Academic year soft closed.")

    @action(detail=True, methods=["post"], url_path="hard-close")
    def hard_close(self, request, pk=None):
        serializer = AcademicYearCloseSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        _ensure_hard_close_operator(request.user)
        academic_year = self.get_object()
        try:
            academic_year = AcademicYearRolloverService.hard_close_academic_year(
                academic_year_id=academic_year.id,
                closed_by=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(AcademicYearSerializer(academic_year, context={"request": request}).data, message="Academic year hard closed.")


class AcademicPeriodViewSet(BaseModelViewSet):
    queryset = AcademicPeriod.objects.select_related("organization", "academic_year").all()
    serializer_class = AcademicPeriodSerializer
    search_fields = ("name", "bs_month_name", "bs_start_date", "bs_end_date")
    ordering_fields = ("period_order", "ad_start_date", "ad_end_date", "created_at")


class NepaliCalendarDayViewSet(BaseReadOnlyModelViewSet):
    queryset = NepaliCalendarDay.objects.all()
    serializer_class = NepaliCalendarDaySerializer
    search_fields = ("bs_date", "bs_month_name")
    ordering_fields = ("ad_date", "bs_year", "bs_month", "bs_day")


class AcademicYearRolloverViewSet(BaseReadOnlyModelViewSet):
    queryset = AcademicYearRollover.objects.select_related("organization", "from_academic_year", "to_academic_year").all()
    serializer_class = AcademicYearRolloverSerializer
    search_fields = ("from_academic_year__name", "to_academic_year__name", "notes")
    ordering_fields = ("created_at", "executed_at", "status")

    def get_permissions(self):
        if self.action in {"prepare", "validate_rollover", "execute", "cancel"}:
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["post"], url_path="prepare")
    def prepare(self, request):
        serializer = AcademicYearRolloverPrepareSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        _ensure_org_rollover_operator(request.user)
        data = serializer.validated_data
        try:
            rollover = AcademicYearRolloverService.prepare_rollover(
                organization=data["organization"],
                from_academic_year=data["from_academic_year"],
                prepared_by=request.user,
                notes=data.get("notes", ""),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            AcademicYearRolloverSerializer(rollover, context={"request": request}).data,
            message="Academic year rollover prepared.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="validate")
    def validate_rollover(self, request, pk=None):
        serializer = AcademicYearRolloverValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        _ensure_org_rollover_operator(request.user)
        rollover = self.get_object()
        try:
            rollover = AcademicYearRolloverService.validate_rollover(rollover_id=rollover.id, validated_by=request.user)
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            AcademicYearRolloverSerializer(rollover, context={"request": request}).data,
            message="Academic year rollover validated.",
        )

    @action(detail=True, methods=["post"], url_path="execute")
    def execute(self, request, pk=None):
        serializer = AcademicYearRolloverExecuteSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        _ensure_org_rollover_operator(request.user)
        rollover = self.get_object()
        try:
            rollover = AcademicYearRolloverService.execute_rollover(
                rollover_id=rollover.id,
                executed_by=request.user,
                new_year_data=serializer.validated_data.get("new_year_data"),
                hard_close=serializer.validated_data.get("hard_close", True),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            AcademicYearRolloverSerializer(rollover, context={"request": request}).data,
            message="Academic year rollover executed.",
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        serializer = AcademicYearRolloverCancelSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        _ensure_org_rollover_operator(request.user)
        rollover = self.get_object()
        try:
            rollover = AcademicYearRolloverService.cancel_rollover(
                rollover_id=rollover.id,
                cancelled_by=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            AcademicYearRolloverSerializer(rollover, context={"request": request}).data,
            message="Academic year rollover cancelled.",
        )

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        rollover = self.get_object()
        return api_success(AcademicYearRolloverService.get_rollover_summary(rollover=rollover))
