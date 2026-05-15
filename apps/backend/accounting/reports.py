from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

from django.db.models import Q, Sum

from billing.models import StudentFeeDue, StudentInvoice
from common.money import ZERO_MONEY, quantize_money
from payroll.models import TeacherEarning

from .models import Account, JournalEntry, JournalEntryLine


@dataclass
class FinancialReportFilters:
    organization: Any
    branch: Any | None = None
    academic_year: Any | None = None
    academic_period: Any | None = None
    date_from: date | None = None
    date_to: date | None = None
    include_zero_balances: bool = False
    account: Account | None = None


@dataclass
class LedgerTransaction:
    entry_date: date
    entry_number: str
    description: str
    narration: str
    debit: Decimal
    credit: Decimal
    running_balance: Decimal
    source_app: str
    source_model: str
    source_object_id: str
    source_number: str


@dataclass
class AccountLedger:
    account_code: str
    account_name: str
    opening_balance: Decimal
    transactions: list[LedgerTransaction]
    total_debit: Decimal
    total_credit: Decimal
    closing_balance: Decimal


@dataclass
class AccountBalance:
    account_code: str
    account_name: str
    account_type: str
    normal_balance: str
    debit: Decimal
    credit: Decimal
    balance: Decimal
    is_abnormal: bool = False


@dataclass
class TrialBalanceResult:
    lines: list[AccountBalance]
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool
    difference: Decimal


@dataclass
class ProfitLossResult:
    revenue: list[AccountBalance]
    contra_revenue: list[AccountBalance]
    expenses: list[AccountBalance]
    other_income: list[AccountBalance]
    other_expenses: list[AccountBalance]
    total_revenue: Decimal
    total_contra_revenue: Decimal
    total_expenses: Decimal
    total_other_income: Decimal
    total_other_expenses: Decimal
    net_profit_loss: Decimal


@dataclass
class BalanceSheetResult:
    assets: list[AccountBalance]
    contra_assets: list[AccountBalance]
    liabilities: list[AccountBalance]
    equity: list[AccountBalance]
    current_year_profit_loss: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    total_liabilities_and_equity: Decimal
    is_balanced: bool
    difference: Decimal


@dataclass
class CashFlowResult:
    cash_accounts: list[AccountBalance]
    opening_balance: Decimal
    inflows: Decimal
    outflows: Decimal
    closing_balance: Decimal


@dataclass
class ReconciliationResult:
    name: str
    operational_balance: Decimal | None
    ledger_balance: Decimal | None
    difference: Decimal | None
    is_reconciled: bool
    limitations: list[str] = field(default_factory=list)


class BaseFinancialReportService:
    @staticmethod
    def _posted_lines(filters: FinancialReportFilters, *, include_date_range: bool = True):
        qs = JournalEntryLine.objects.select_related("account", "journal_entry").filter(
            organization=filters.organization,
            journal_entry__status=JournalEntry.Status.POSTED,
        )
        if filters.branch:
            qs = qs.filter(branch=filters.branch)
        if filters.academic_year:
            qs = qs.filter(journal_entry__academic_year=filters.academic_year)
        if filters.academic_period:
            qs = qs.filter(journal_entry__academic_period=filters.academic_period)
        if filters.account:
            qs = qs.filter(account=filters.account)
        if include_date_range:
            if filters.date_from:
                qs = qs.filter(journal_entry__entry_date_ad__gte=filters.date_from)
            if filters.date_to:
                qs = qs.filter(journal_entry__entry_date_ad__lte=filters.date_to)
        return qs

    @staticmethod
    def _sum_lines(qs) -> tuple[Decimal, Decimal]:
        totals = qs.aggregate(
            debit=Sum("debit_amount", default=Decimal("0.00")),
            credit=Sum("credit_amount", default=Decimal("0.00")),
        )
        return quantize_money(totals["debit"]), quantize_money(totals["credit"])

    @staticmethod
    def _raw_balance(debit: Decimal, credit: Decimal) -> Decimal:
        return quantize_money(debit - credit)

    @staticmethod
    def _normal_balance_amount(account: Account, debit: Decimal, credit: Decimal) -> Decimal:
        raw = debit - credit
        if account.normal_balance == Account.NormalBalance.CREDIT:
            raw = -raw
        return quantize_money(raw)

    @classmethod
    def _account_balance(cls, account: Account, debit: Decimal, credit: Decimal) -> AccountBalance:
        raw = cls._raw_balance(debit, credit)
        if account.normal_balance == Account.NormalBalance.DEBIT:
            debit_balance = raw if raw >= ZERO_MONEY else ZERO_MONEY
            credit_balance = -raw if raw < ZERO_MONEY else ZERO_MONEY
            normal_amount = raw
        else:
            debit_balance = raw if raw > ZERO_MONEY else ZERO_MONEY
            credit_balance = -raw if raw <= ZERO_MONEY else ZERO_MONEY
            normal_amount = -raw
        return AccountBalance(
            account_code=account.code,
            account_name=account.name,
            account_type=account.account_type,
            normal_balance=account.normal_balance,
            debit=quantize_money(debit_balance),
            credit=quantize_money(credit_balance),
            balance=quantize_money(normal_amount),
            is_abnormal=normal_amount < ZERO_MONEY,
        )

    @staticmethod
    def _accounts(filters: FinancialReportFilters):
        qs = Account.objects.filter(organization=filters.organization).order_by("code")
        if filters.account:
            qs = qs.filter(id=filters.account.id)
        return qs


class GeneralLedgerReportService(BaseFinancialReportService):
    @classmethod
    def get_account_ledger(cls, *, filters: FinancialReportFilters, account: Account | None = None) -> AccountLedger:
        account = account or filters.account
        if account is None:
            raise ValueError("Account is required for account ledger report.")

        opening_qs = cls._posted_lines(FinancialReportFilters(**{**filters.__dict__, "account": account}), include_date_range=False)
        if filters.date_from:
            opening_qs = opening_qs.filter(journal_entry__entry_date_ad__lt=filters.date_from)
        else:
            opening_qs = opening_qs.none()
        opening_debit, opening_credit = cls._sum_lines(opening_qs)
        opening_balance = cls._normal_balance_amount(account, opening_debit, opening_credit)

        period_filters = FinancialReportFilters(**{**filters.__dict__, "account": account})
        lines = cls._posted_lines(period_filters).order_by("journal_entry__entry_date_ad", "journal_entry__entry_number", "created_at")
        total_debit = ZERO_MONEY
        total_credit = ZERO_MONEY
        running_balance = opening_balance
        transactions: list[LedgerTransaction] = []
        for line in lines:
            debit = quantize_money(line.debit_amount)
            credit = quantize_money(line.credit_amount)
            total_debit = quantize_money(total_debit + debit)
            total_credit = quantize_money(total_credit + credit)
            movement = debit - credit
            if account.normal_balance == Account.NormalBalance.CREDIT:
                movement = -movement
            running_balance = quantize_money(running_balance + movement)
            entry = line.journal_entry
            transactions.append(
                LedgerTransaction(
                    entry_date=entry.entry_date_ad,
                    entry_number=entry.entry_number,
                    description=entry.description,
                    narration=entry.narration,
                    debit=debit,
                    credit=credit,
                    running_balance=running_balance,
                    source_app=entry.source_app,
                    source_model=entry.source_model,
                    source_object_id=str(entry.source_object_id or ""),
                    source_number=entry.source_number,
                )
            )

        return AccountLedger(
            account_code=account.code,
            account_name=account.name,
            opening_balance=opening_balance,
            transactions=transactions,
            total_debit=total_debit,
            total_credit=total_credit,
            closing_balance=running_balance,
        )

    @classmethod
    def get_general_ledger(cls, *, filters: FinancialReportFilters) -> list[AccountLedger]:
        ledgers = []
        for account in cls._accounts(filters):
            ledger = cls.get_account_ledger(filters=filters, account=account)
            if filters.include_zero_balances or ledger.opening_balance or ledger.total_debit or ledger.total_credit or ledger.closing_balance:
                ledgers.append(ledger)
        return ledgers


class TrialBalanceReportService(BaseFinancialReportService):
    @classmethod
    def get_trial_balance(cls, *, filters: FinancialReportFilters) -> TrialBalanceResult:
        lines = []
        total_debit = ZERO_MONEY
        total_credit = ZERO_MONEY
        for account in cls._accounts(filters):
            qs = cls._posted_lines(FinancialReportFilters(**{**filters.__dict__, "account": account}))
            debit, credit = cls._sum_lines(qs)
            balance = cls._account_balance(account, debit, credit)
            if filters.include_zero_balances or balance.debit or balance.credit:
                lines.append(balance)
                total_debit = quantize_money(total_debit + balance.debit)
                total_credit = quantize_money(total_credit + balance.credit)
        difference = quantize_money(total_debit - total_credit)
        return TrialBalanceResult(
            lines=lines,
            total_debit=total_debit,
            total_credit=total_credit,
            is_balanced=difference == ZERO_MONEY,
            difference=difference,
        )


class ProfitLossReportService(BaseFinancialReportService):
    @classmethod
    def get_profit_and_loss(cls, *, filters: FinancialReportFilters) -> ProfitLossResult:
        sections = {
            "revenue": [],
            "contra_revenue": [],
            "expenses": [],
            "other_income": [],
            "other_expenses": [],
        }
        totals = {key: ZERO_MONEY for key in sections}
        type_map = {
            Account.AccountType.REVENUE: "revenue",
            Account.AccountType.CONTRA_REVENUE: "contra_revenue",
            Account.AccountType.EXPENSE: "expenses",
            Account.AccountType.OTHER_INCOME: "other_income",
            Account.AccountType.OTHER_EXPENSE: "other_expenses",
        }
        for account in cls._accounts(filters).filter(account_type__in=type_map):
            debit, credit = cls._sum_lines(cls._posted_lines(FinancialReportFilters(**{**filters.__dict__, "account": account})))
            line = cls._account_balance(account, debit, credit)
            if filters.include_zero_balances or line.balance:
                section = type_map[account.account_type]
                sections[section].append(line)
                totals[section] = quantize_money(totals[section] + line.balance)

        net = quantize_money(
            totals["revenue"]
            + totals["other_income"]
            - totals["expenses"]
            - totals["other_expenses"]
            - totals["contra_revenue"]
        )
        return ProfitLossResult(
            revenue=sections["revenue"],
            contra_revenue=sections["contra_revenue"],
            expenses=sections["expenses"],
            other_income=sections["other_income"],
            other_expenses=sections["other_expenses"],
            total_revenue=totals["revenue"],
            total_contra_revenue=totals["contra_revenue"],
            total_expenses=totals["expenses"],
            total_other_income=totals["other_income"],
            total_other_expenses=totals["other_expenses"],
            net_profit_loss=net,
        )


class BalanceSheetReportService(BaseFinancialReportService):
    @classmethod
    def get_balance_sheet(cls, *, filters: FinancialReportFilters, include_current_year_profit: bool = True) -> BalanceSheetResult:
        sections = {"assets": [], "contra_assets": [], "liabilities": [], "equity": []}
        totals = {key: ZERO_MONEY for key in sections}
        type_map = {
            Account.AccountType.ASSET: "assets",
            Account.AccountType.CONTRA_ASSET: "contra_assets",
            Account.AccountType.LIABILITY: "liabilities",
            Account.AccountType.EQUITY: "equity",
        }
        for account in cls._accounts(filters).filter(account_type__in=type_map):
            debit, credit = cls._sum_lines(cls._posted_lines(FinancialReportFilters(**{**filters.__dict__, "account": account})))
            line = cls._account_balance(account, debit, credit)
            if filters.include_zero_balances or line.balance:
                section = type_map[account.account_type]
                sections[section].append(line)
                totals[section] = quantize_money(totals[section] + line.balance)

        current_profit = (
            ProfitLossReportService.get_profit_and_loss(filters=filters).net_profit_loss if include_current_year_profit else ZERO_MONEY
        )
        total_assets = quantize_money(totals["assets"] - totals["contra_assets"])
        total_equity = quantize_money(totals["equity"] + current_profit)
        total_liabilities_equity = quantize_money(totals["liabilities"] + total_equity)
        difference = quantize_money(total_assets - total_liabilities_equity)
        return BalanceSheetResult(
            assets=sections["assets"],
            contra_assets=sections["contra_assets"],
            liabilities=sections["liabilities"],
            equity=sections["equity"],
            current_year_profit_loss=current_profit,
            total_assets=total_assets,
            total_liabilities=totals["liabilities"],
            total_equity=total_equity,
            total_liabilities_and_equity=total_liabilities_equity,
            is_balanced=difference == ZERO_MONEY,
            difference=difference,
        )


class CashFlowReportService(BaseFinancialReportService):
    CASH_ACCOUNT_CODES = {"1110", "1120", "1130"}

    @classmethod
    def get_cash_flow_summary(cls, *, filters: FinancialReportFilters) -> CashFlowResult:
        cash_accounts = []
        opening = ZERO_MONEY
        inflows = ZERO_MONEY
        outflows = ZERO_MONEY
        closing = ZERO_MONEY
        for account in cls._accounts(filters).filter(code__in=cls.CASH_ACCOUNT_CODES):
            account_filters = FinancialReportFilters(**{**filters.__dict__, "account": account})
            ledger = GeneralLedgerReportService.get_account_ledger(filters=account_filters, account=account)
            cash_accounts.append(
                AccountBalance(
                    account_code=account.code,
                    account_name=account.name,
                    account_type=account.account_type,
                    normal_balance=account.normal_balance,
                    debit=ledger.total_debit,
                    credit=ledger.total_credit,
                    balance=ledger.closing_balance,
                )
            )
            opening = quantize_money(opening + ledger.opening_balance)
            inflows = quantize_money(inflows + ledger.total_debit)
            outflows = quantize_money(outflows + ledger.total_credit)
            closing = quantize_money(closing + ledger.closing_balance)
        return CashFlowResult(cash_accounts=cash_accounts, opening_balance=opening, inflows=inflows, outflows=outflows, closing_balance=closing)


class ReconciliationReportService(BaseFinancialReportService):
    @classmethod
    def _ledger_balance_for_code(cls, *, filters: FinancialReportFilters, code: str, credit_normal: bool = False) -> Decimal | None:
        try:
            account = Account.objects.get(organization=filters.organization, code=code)
        except Account.DoesNotExist:
            return None
        debit, credit = cls._sum_lines(cls._posted_lines(FinancialReportFilters(**{**filters.__dict__, "account": account})))
        return quantize_money(credit - debit if credit_normal else debit - credit)

    @classmethod
    def compare_billing_receivables_to_ledger(cls, *, filters: FinancialReportFilters) -> ReconciliationResult:
        qs_filter = Q(organization=filters.organization)
        if filters.branch:
            qs_filter &= Q(branch=filters.branch)
        if filters.academic_year:
            qs_filter &= Q(academic_year=filters.academic_year)
        if filters.academic_period:
            qs_filter &= Q(academic_period=filters.academic_period)
        due_total = StudentFeeDue.objects.filter(qs_filter).aggregate(total=Sum("balance_amount", default=Decimal("0.00")))["total"]
        invoice_total = StudentInvoice.objects.filter(qs_filter).aggregate(total=Sum("balance_amount", default=Decimal("0.00")))["total"]
        operational = quantize_money(due_total + invoice_total)
        ledger = cls._ledger_balance_for_code(filters=filters, code="1210")
        difference = None if ledger is None else quantize_money(operational - ledger)
        return ReconciliationResult(
            name="student_receivables",
            operational_balance=operational,
            ledger_balance=ledger,
            difference=difference,
            is_reconciled=difference == ZERO_MONEY,
            limitations=["Due and invoice balances can double count when invoices are generated from dues."],
        )

    @classmethod
    def compare_teacher_payables_to_ledger(cls, *, filters: FinancialReportFilters) -> ReconciliationResult:
        qs = TeacherEarning.objects.filter(organization=filters.organization)
        if filters.branch:
            qs = qs.filter(branch=filters.branch)
        if filters.academic_year:
            qs = qs.filter(academic_year=filters.academic_year)
        if filters.academic_period:
            qs = qs.filter(academic_period=filters.academic_period)
        operational = quantize_money(qs.aggregate(total=Sum("balance_amount", default=Decimal("0.00")))["total"])
        ledger = cls._ledger_balance_for_code(filters=filters, code="2110", credit_normal=True)
        difference = None if ledger is None else quantize_money(operational - ledger)
        return ReconciliationResult(
            name="teacher_payables",
            operational_balance=operational,
            ledger_balance=ledger,
            difference=difference,
            is_reconciled=difference == ZERO_MONEY,
            limitations=[],
        )

    @classmethod
    def compare_cash_accounts_to_ledger(cls, *, filters: FinancialReportFilters) -> ReconciliationResult:
        cash_flow = CashFlowReportService.get_cash_flow_summary(filters=filters)
        ledger = cash_flow.closing_balance
        return ReconciliationResult(
            name="cash_accounts",
            operational_balance=None,
            ledger_balance=ledger,
            difference=None,
            is_reconciled=True,
            limitations=["No external bank statement source exists yet; this is a ledger cash-account summary only."],
        )
