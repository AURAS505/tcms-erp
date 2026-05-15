from dataclasses import asdict, is_dataclass

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from common.permissions import BranchScopedPermission
from common.responses import api_success
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
from .serializers import AccountSerializer, AccountingDocumentSerializer, JournalEntryLineSerializer, JournalEntrySerializer


class AccountViewSet(BaseReadOnlyModelViewSet):
    queryset = Account.objects.select_related("organization", "parent").all()
    serializer_class = AccountSerializer
    search_fields = ("code", "name", "description")
    ordering_fields = ("code", "name", "account_type", "created_at")


class JournalEntryViewSet(BaseReadOnlyModelViewSet):
    queryset = JournalEntry.objects.select_related("organization", "branch", "academic_year", "academic_period").all()
    serializer_class = JournalEntrySerializer
    search_fields = ("entry_number", "description", "narration", "source_app", "source_model", "source_number")
    ordering_fields = ("entry_date_ad", "posting_date_ad", "created_at", "status")


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
