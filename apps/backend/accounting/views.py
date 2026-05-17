from dataclasses import asdict, is_dataclass

from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from common.permissions import BranchScopedPermission, IsFinancialApprover, user_can_access_branch
from common.responses import api_success, validation_error_response
from common.viewsets import BaseReadOnlyModelViewSet
from organizations.models import Organization

from .models import Account, AccountingDocument, JournalEntry, JournalEntryLine
from .reports import (
    BalanceSheetReportService,
    FinancialReportFilters,
    GeneralLedgerReportService,
    ProfitLossReportService,
    TrialBalanceReportService,
)
from .serializers import (
    AccountSerializer,
    AccountingDocumentCreateSerializer,
    AccountingDocumentSerializer,
    EmptyAccountingActionSerializer,
    JournalEntryLineSerializer,
    JournalEntrySerializer,
    JournalReverseSerializer,
    ManualJournalCreateSerializer,
)
from .services import AccountingMutationService


def _validation_errors(exc: DjangoValidationError):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"non_field_errors": exc.messages}
    return {"non_field_errors": [str(exc)]}


class AccountViewSet(BaseReadOnlyModelViewSet):
    queryset = Account.objects.select_related("organization", "parent").all()
    serializer_class = AccountSerializer
    search_fields = ("code", "name", "description")
    ordering_fields = ("code", "name", "account_type", "created_at")


class JournalEntryViewSet(BaseReadOnlyModelViewSet):
    queryset = JournalEntry.objects.select_related("organization", "branch", "academic_year", "academic_period").prefetch_related("lines").all()
    serializer_class = JournalEntrySerializer
    search_fields = ("entry_number", "description", "narration", "source_app", "source_model", "source_number")
    ordering_fields = ("entry_date_ad", "posting_date_ad", "created_at", "status")

    def get_queryset(self):
        queryset = super().get_queryset()
        source_filters = {
            "source_app": self.request.query_params.get("source_app"),
            "source_model": self.request.query_params.get("source_model"),
            "source_object_id": self.request.query_params.get("source_object_id"),
            "source_type": self.request.query_params.get("source_type"),
        }
        return queryset.filter(**{key: value for key, value in source_filters.items() if value})

    def get_permissions(self):
        if self.action in {"create_manual", "approve", "post", "reverse", "documents"}:
            permission_classes = [BranchScopedPermission, IsFinancialApprover]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["post"], url_path="create-manual")
    def create_manual(self, request):
        serializer = ManualJournalCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        data = serializer.validated_data
        if not user_can_access_branch(request.user, data["branch"].id, data["organization"].id):
            raise PermissionDenied("You do not have access to create journal entries for this branch.")
        try:
            journal_entry = AccountingMutationService.create_manual_journal_entry(
                organization=data["organization"],
                branch=data["branch"],
                academic_year=data["academic_year"],
                academic_period=data.get("academic_period"),
                entry_date_ad=data["entry_date_ad"],
                entry_date_bs=data.get("entry_date_bs", ""),
                description=data["description"],
                narration=data.get("narration", ""),
                lines=data["lines"],
                created_by=request.user,
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            JournalEntrySerializer(journal_entry, context={"request": request}).data,
            message="Manual journal entry created.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = EmptyAccountingActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        journal_entry = self.get_object()
        try:
            journal_entry = AccountingMutationService.approve_journal_entry(
                journal_entry_id=journal_entry.id,
                approved_by=request.user,
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            JournalEntrySerializer(journal_entry, context={"request": request}).data,
            message="Journal entry approved.",
        )

    @action(detail=True, methods=["post"], url_path="post")
    def post(self, request, pk=None):
        serializer = EmptyAccountingActionSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        journal_entry = self.get_object()
        try:
            journal_entry = AccountingMutationService.post_manual_journal_entry(
                journal_entry_id=journal_entry.id,
                posted_by=request.user,
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            JournalEntrySerializer(journal_entry, context={"request": request}).data,
            message="Journal entry posted.",
        )

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request, pk=None):
        serializer = JournalReverseSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        journal_entry = self.get_object()
        try:
            reversal = AccountingMutationService.reverse_journal_entry(
                journal_entry_id=journal_entry.id,
                reversed_by=request.user,
                reversal_date_ad=serializer.validated_data.get("reversal_date_ad"),
                narration=serializer.validated_data.get("narration", ""),
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            JournalEntrySerializer(reversal, context={"request": request}).data,
            message="Journal entry reversed.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="documents")
    def documents(self, request, pk=None):
        serializer = AccountingDocumentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        journal_entry = self.get_object()
        try:
            document = AccountingMutationService.attach_accounting_document(
                journal_entry_id=journal_entry.id,
                uploaded_by=request.user,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            return validation_error_response(_validation_errors(exc))
        return api_success(
            AccountingDocumentSerializer(document, context={"request": request}).data,
            message="Accounting document attached.",
            status_code=status.HTTP_201_CREATED,
        )


class JournalEntryLineViewSet(BaseReadOnlyModelViewSet):
    queryset = JournalEntryLine.objects.select_related("organization", "branch", "journal_entry", "account").all()
    serializer_class = JournalEntryLineSerializer
    search_fields = ("journal_entry__entry_number", "account__code", "account__name", "description")
    ordering_fields = ("created_at", "debit_amount", "credit_amount")


class AccountingDocumentViewSet(BaseReadOnlyModelViewSet):
    queryset = AccountingDocument.objects.select_related("organization", "journal_entry", "uploaded_by").all()
    serializer_class = AccountingDocumentSerializer
    search_fields = ("reference_number", "document_type", "description")
    ordering_fields = ("created_at", "document_type")


def _serialize_report(value):
    if is_dataclass(value):
        return {key: _serialize_report(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_serialize_report(item) for item in value]
    return value


class ReportAPIView(APIView):
    permission_classes = [BranchScopedPermission]

    def build_filters(self, request) -> FinancialReportFilters:
        from academic.models import AcademicPeriod, AcademicYear
        from organizations.models import Branch

        organization = get_object_or_404(Organization, id=request.query_params.get("organization"))
        branch = Branch.objects.filter(id=request.query_params.get("branch")).first() if request.query_params.get("branch") else None
        academic_year = (
            AcademicYear.objects.filter(id=request.query_params.get("academic_year")).first()
            if request.query_params.get("academic_year")
            else None
        )
        academic_period = (
            AcademicPeriod.objects.filter(id=request.query_params.get("academic_period")).first()
            if request.query_params.get("academic_period")
            else None
        )
        account = Account.objects.filter(id=request.query_params.get("account")).first() if request.query_params.get("account") else None
        return FinancialReportFilters(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            academic_period=academic_period,
            date_from=request.query_params.get("date_from") or None,
            date_to=request.query_params.get("date_to") or None,
            include_zero_balances=request.query_params.get("include_zero_balances") == "true",
            account=account,
        )


class TrialBalanceAPIView(ReportAPIView):
    def get(self, request):
        return api_success(_serialize_report(TrialBalanceReportService.get_trial_balance(filters=self.build_filters(request))))


class GeneralLedgerAPIView(ReportAPIView):
    def get(self, request):
        filters = self.build_filters(request)
        if filters.account:
            data = GeneralLedgerReportService.get_account_ledger(filters=filters, account=filters.account)
        else:
            data = GeneralLedgerReportService.get_general_ledger(filters=filters)
        return api_success(_serialize_report(data))


class ProfitLossAPIView(ReportAPIView):
    def get(self, request):
        return api_success(_serialize_report(ProfitLossReportService.get_profit_and_loss(filters=self.build_filters(request))))


class BalanceSheetAPIView(ReportAPIView):
    def get(self, request):
        return api_success(_serialize_report(BalanceSheetReportService.get_balance_sheet(filters=self.build_filters(request))))
