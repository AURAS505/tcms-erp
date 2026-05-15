from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AccountViewSet,
    AccountingDocumentViewSet,
    BalanceSheetAPIView,
    GeneralLedgerAPIView,
    JournalEntryLineViewSet,
    JournalEntryViewSet,
    ProfitLossAPIView,
    TrialBalanceAPIView,
)

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename="account")
router.register("journal-entries", JournalEntryViewSet, basename="journal-entry")
router.register("journal-entry-lines", JournalEntryLineViewSet, basename="journal-entry-line")
router.register("accounting-documents", AccountingDocumentViewSet, basename="accounting-document")

urlpatterns = [
    path("reports/trial-balance/", TrialBalanceAPIView.as_view(), name="trial-balance-report"),
    path("reports/general-ledger/", GeneralLedgerAPIView.as_view(), name="general-ledger-report"),
    path("reports/profit-loss/", ProfitLossAPIView.as_view(), name="profit-loss-report"),
    path("reports/balance-sheet/", BalanceSheetAPIView.as_view(), name="balance-sheet-report"),
]
urlpatterns += router.urls
