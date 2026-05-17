from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounting.models import Account, JournalEntry, JournalEntryLine
from accounting.reports import FinancialReportFilters, TrialBalanceReportService
from accounting.services import AccountingPostingService
from common.audit import AuditAction, AuditLogService, AuditModule
from common.money import ZERO_MONEY, quantize_money

from .models import AcademicPeriod, AcademicYear, AcademicYearRollover


@dataclass
class NewAcademicYearInput:
    name: str
    bs_start_year: int
    bs_end_year: int
    bs_start_date: str
    bs_end_date: str
    ad_start_date: object
    ad_end_date: object
    notes: str = ""


class AcademicYearRolloverService:
    INCOME_SUMMARY_CODE = "3300"
    RETAINED_EARNINGS_CODE = "3200"
    PROFIT_LOSS_TYPES = {
        Account.AccountType.REVENUE,
        Account.AccountType.CONTRA_REVENUE,
        Account.AccountType.EXPENSE,
        Account.AccountType.OTHER_INCOME,
        Account.AccountType.OTHER_EXPENSE,
    }
    BALANCE_SHEET_TYPES = {
        Account.AccountType.ASSET,
        Account.AccountType.CONTRA_ASSET,
        Account.AccountType.LIABILITY,
        Account.AccountType.EQUITY,
    }

    @classmethod
    @transaction.atomic
    def prepare_rollover(cls, *, organization, from_academic_year, prepared_by=None, notes: str = "") -> AcademicYearRollover:
        cls._validate_from_year(organization=organization, from_academic_year=from_academic_year)
        existing = AcademicYearRollover.objects.select_for_update().filter(
            organization=organization,
            from_academic_year=from_academic_year,
            status__in=[
                AcademicYearRollover.Status.DRAFT,
                AcademicYearRollover.Status.VALIDATING,
                AcademicYearRollover.Status.READY,
            ],
        )
        if existing.exists():
            raise ValidationError("A rollover is already pending for this academic year.")
        rollover = AcademicYearRollover.objects.create(
            organization=organization,
            from_academic_year=from_academic_year,
            notes=notes,
        )
        AuditLogService.record(
            action=AuditAction.CREATE,
            module=AuditModule.ACADEMIC,
            obj=rollover,
            user=prepared_by,
            metadata={"event": "academic_year_rollover_prepared"},
        )
        return rollover

    @classmethod
    @transaction.atomic
    def validate_rollover(cls, *, rollover_id, validated_by=None) -> AcademicYearRollover:
        rollover = AcademicYearRollover.objects.select_for_update().select_related("organization", "from_academic_year").get(id=rollover_id)
        rollover.status = AcademicYearRollover.Status.VALIDATING
        rollover._allow_immutable_update = True
        rollover.save(update_fields=["status", "updated_at"])
        try:
            cls._validate_from_year(organization=rollover.organization, from_academic_year=rollover.from_academic_year)
            cls._validate_required_accounts(organization=rollover.organization)
            trial_balance = TrialBalanceReportService.get_trial_balance(
                filters=FinancialReportFilters(
                    organization=rollover.organization,
                    academic_year=rollover.from_academic_year,
                )
            )
            if not trial_balance.is_balanced:
                raise ValidationError("Cannot rollover because outgoing year trial balance is not balanced.")
            rollover.trial_balance_validated = True
            rollover.status = AcademicYearRollover.Status.READY
            rollover._allow_immutable_update = True
            rollover.save(update_fields=["trial_balance_validated", "status", "updated_at"])
            AuditLogService.record(
                action=AuditAction.SYSTEM,
                module=AuditModule.ACADEMIC,
                obj=rollover,
                user=validated_by,
                metadata={"event": "academic_year_rollover_validated"},
            )
        except Exception as exc:
            rollover.status = AcademicYearRollover.Status.FAILED
            rollover.notes = f"{rollover.notes}\nValidation failed: {exc}".strip()
            rollover._allow_immutable_update = True
            rollover.save(update_fields=["status", "notes", "updated_at"])
            AuditLogService.record(
                action=AuditAction.SYSTEM,
                module=AuditModule.ACADEMIC,
                obj=rollover,
                user=validated_by,
                metadata={"event": "academic_year_rollover_validation_failed", "error": str(exc)},
            )
            raise
        return rollover

    @classmethod
    @transaction.atomic
    def execute_rollover(
        cls,
        *,
        rollover_id,
        executed_by=None,
        new_year_data: NewAcademicYearInput | dict | None = None,
        hard_close: bool = True,
    ) -> AcademicYearRollover:
        rollover = (
            AcademicYearRollover.objects.select_for_update()
            .select_related("organization", "from_academic_year", "to_academic_year")
            .get(id=rollover_id)
        )
        if rollover.status == AcademicYearRollover.Status.EXECUTED:
            return rollover
        if not rollover.trial_balance_validated or rollover.status != AcademicYearRollover.Status.READY:
            rollover = cls.validate_rollover(rollover_id=rollover.id, validated_by=executed_by)
        if rollover.to_academic_year_id is None:
            if new_year_data is None:
                raise ValidationError("New academic year data is required when rollover target year does not exist.")
            target_year = cls.create_new_academic_year(
                organization=rollover.organization,
                from_academic_year=rollover.from_academic_year,
                data=new_year_data,
            )
            rollover.to_academic_year = target_year
            rollover._allow_immutable_update = True
            rollover.save(update_fields=["to_academic_year", "updated_at"])
        else:
            target_year = rollover.to_academic_year
            cls._validate_target_year(organization=rollover.organization, target_year=target_year)

        if cls._opening_entries_exist(organization=rollover.organization, to_academic_year=target_year, rollover=rollover):
            raise ValidationError("Opening entries already exist for this rollover target year.")

        cls.post_closing_entries(rollover=rollover, posted_by=executed_by)
        cls.soft_close_outgoing_year(rollover=rollover, closed_by=executed_by)
        cls.post_opening_entries(rollover=rollover, posted_by=executed_by)
        cls.activate_new_year(rollover=rollover, activated_by=executed_by)
        if hard_close:
            cls.hard_close_outgoing_year(rollover=rollover, closed_by=executed_by)

        rollover.status = AcademicYearRollover.Status.EXECUTED
        rollover.executed_by = executed_by
        rollover.executed_at = timezone.now()
        rollover._allow_immutable_update = True
        rollover.save(update_fields=["status", "executed_by", "executed_at", "updated_at"])
        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACADEMIC,
            obj=rollover,
            user=executed_by,
            metadata={"event": "academic_year_rollover_executed"},
        )
        return rollover

    @classmethod
    def create_new_academic_year(cls, *, organization, from_academic_year, data: NewAcademicYearInput | dict) -> AcademicYear:
        if isinstance(data, dict):
            data = NewAcademicYearInput(**data)
        if AcademicYear.objects.filter(organization=organization, name=data.name).exists():
            raise ValidationError("New academic year name already exists for this organization.")
        return AcademicYear.objects.create(
            organization=organization,
            name=data.name,
            bs_start_year=data.bs_start_year,
            bs_end_year=data.bs_end_year,
            bs_start_date=data.bs_start_date,
            bs_end_date=data.bs_end_date,
            ad_start_date=data.ad_start_date,
            ad_end_date=data.ad_end_date,
            status=AcademicYear.Status.DRAFT,
            is_active=False,
            notes=data.notes or f"Created from rollover of {from_academic_year.name}",
        )

    @staticmethod
    def create_new_academic_periods_placeholder(*, to_academic_year) -> list[AcademicPeriod]:
        return []

    @classmethod
    def post_closing_entries(cls, *, rollover: AcademicYearRollover, posted_by=None) -> list[JournalEntry]:
        if rollover.revenue_expense_closing_completed:
            return list(
                JournalEntry.objects.filter(
                    organization=rollover.organization,
                    academic_year=rollover.from_academic_year,
                    source_app="academic",
                    source_model="AcademicYearRollover",
                    source_object_id=rollover.id,
                    source_number__startswith="closing",
                )
            )
        income_summary = cls._get_account(organization=rollover.organization, code=cls.INCOME_SUMMARY_CODE)
        retained_earnings = cls._get_account(organization=rollover.organization, code=cls.RETAINED_EARNINGS_CODE)
        entries = []
        income_summary_credit = ZERO_MONEY
        income_summary_debit = ZERO_MONEY

        for account in Account.objects.filter(organization=rollover.organization, account_type__in=cls.PROFIT_LOSS_TYPES).order_by("code"):
            if account.code in {cls.INCOME_SUMMARY_CODE, cls.RETAINED_EARNINGS_CODE}:
                continue
            debit, credit = cls._account_totals(account=account, academic_year=rollover.from_academic_year)
            raw = quantize_money(debit - credit)
            if raw == ZERO_MONEY:
                continue
            entry = cls._new_system_entry(
                rollover=rollover,
                academic_year=rollover.from_academic_year,
                description=f"Close {account.code} {account.name}",
                source_number=f"closing-{account.code}",
                posted_by=posted_by,
            )
            if raw < ZERO_MONEY:
                amount = quantize_money(-raw)
                cls._add_line(entry=entry, account=account, credit=ZERO_MONEY, debit=amount)
                cls._add_line(entry=entry, account=income_summary, credit=amount, debit=ZERO_MONEY)
                income_summary_credit = quantize_money(income_summary_credit + amount)
            else:
                amount = raw
                cls._add_line(entry=entry, account=income_summary, credit=ZERO_MONEY, debit=amount)
                cls._add_line(entry=entry, account=account, credit=amount, debit=ZERO_MONEY)
                income_summary_debit = quantize_money(income_summary_debit + amount)
            entries.append(AccountingPostingService.post_journal_entry(entry, posted_by=posted_by))

        net_income = quantize_money(income_summary_credit - income_summary_debit)
        if net_income != ZERO_MONEY:
            transfer = cls._new_system_entry(
                rollover=rollover,
                academic_year=rollover.from_academic_year,
                description="Transfer income summary to retained earnings",
                source_number="closing-retained-earnings",
                posted_by=posted_by,
            )
            if net_income > ZERO_MONEY:
                cls._add_line(entry=transfer, account=income_summary, debit=net_income, credit=ZERO_MONEY)
                cls._add_line(entry=transfer, account=retained_earnings, debit=ZERO_MONEY, credit=net_income)
            else:
                loss = quantize_money(-net_income)
                cls._add_line(entry=transfer, account=retained_earnings, debit=loss, credit=ZERO_MONEY)
                cls._add_line(entry=transfer, account=income_summary, debit=ZERO_MONEY, credit=loss)
            entries.append(AccountingPostingService.post_journal_entry(transfer, posted_by=posted_by))

        rollover.revenue_expense_closing_completed = True
        rollover._allow_immutable_update = True
        rollover.save(update_fields=["revenue_expense_closing_completed", "updated_at"])
        AuditLogService.record(
            action=AuditAction.POST,
            module=AuditModule.ACADEMIC,
            obj=rollover,
            user=posted_by,
            metadata={"event": "academic_year_closing_entries_posted", "entry_count": len(entries)},
        )
        return entries

    @classmethod
    def post_opening_entries(cls, *, rollover: AcademicYearRollover, posted_by=None) -> JournalEntry | None:
        if rollover.opening_balances_posted:
            return JournalEntry.objects.filter(
                organization=rollover.organization,
                academic_year=rollover.to_academic_year,
                source_app="academic",
                source_model="AcademicYearRollover",
                source_object_id=rollover.id,
                source_number="opening-balances",
            ).first()
        entry = cls._new_system_entry(
            rollover=rollover,
            academic_year=rollover.to_academic_year,
            academic_period=rollover.to_academic_year.periods.order_by("period_order").first(),
            description=f"Opening balances from {rollover.from_academic_year.name}",
            source_number="opening-balances",
            posted_by=posted_by,
        )
        line_count = 0
        for account in Account.objects.filter(organization=rollover.organization, account_type__in=cls.BALANCE_SHEET_TYPES).order_by("code"):
            debit, credit = cls._account_totals(account=account, academic_year=rollover.from_academic_year)
            raw = quantize_money(debit - credit)
            if raw == ZERO_MONEY:
                continue
            if raw > ZERO_MONEY:
                cls._add_line(entry=entry, account=account, debit=raw, credit=ZERO_MONEY)
            else:
                cls._add_line(entry=entry, account=account, debit=ZERO_MONEY, credit=quantize_money(-raw))
            line_count += 1
        if line_count < 2:
            entry.delete()
            posted = None
        else:
            posted = AccountingPostingService.post_journal_entry(entry, posted_by=posted_by)
        rollover.opening_balances_posted = True
        rollover._allow_immutable_update = True
        rollover.save(update_fields=["opening_balances_posted", "updated_at"])
        AuditLogService.record(
            action=AuditAction.POST,
            module=AuditModule.ACADEMIC,
            obj=rollover,
            user=posted_by,
            metadata={"event": "academic_year_opening_entries_posted", "line_count": line_count},
        )
        return posted

    @staticmethod
    def soft_close_outgoing_year(*, rollover: AcademicYearRollover, closed_by=None) -> AcademicYear:
        year = rollover.from_academic_year
        year.status = AcademicYear.Status.SOFT_CLOSED
        year.is_active = False
        year._allow_hard_closed_update = True
        year.save(update_fields=["status", "is_active", "updated_at"])
        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACADEMIC,
            obj=year,
            user=closed_by,
            metadata={"event": "academic_year_soft_closed", "rollover_id": str(rollover.id)},
        )
        return year

    @staticmethod
    def hard_close_outgoing_year(*, rollover: AcademicYearRollover, closed_by=None) -> AcademicYear:
        year = rollover.from_academic_year
        year.status = AcademicYear.Status.HARD_CLOSED
        year.is_active = False
        year._allow_hard_closed_update = True
        year.save(update_fields=["status", "is_active", "updated_at"])
        for period in year.periods.exclude(status=AcademicPeriod.Status.HARD_CLOSED):
            period.status = AcademicPeriod.Status.HARD_CLOSED
            period.is_active = False
            period._allow_hard_closed_update = True
            period.save(update_fields=["status", "is_active", "updated_at"])
        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACADEMIC,
            obj=year,
            user=closed_by,
            metadata={"event": "academic_year_hard_closed", "rollover_id": str(rollover.id)},
        )
        return year

    @staticmethod
    @transaction.atomic
    def soft_close_academic_year(*, academic_year_id, closed_by=None, reason: str = "") -> AcademicYear:
        year = AcademicYear.objects.select_for_update().get(id=academic_year_id)
        if year.status == AcademicYear.Status.HARD_CLOSED:
            raise ValidationError("Hard-closed academic years cannot be soft closed.")
        year.status = AcademicYear.Status.SOFT_CLOSED
        year.is_active = False
        year._allow_hard_closed_update = True
        year.save(update_fields=["status", "is_active", "updated_at"])
        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACADEMIC,
            obj=year,
            user=closed_by,
            metadata={"event": "academic_year_soft_closed", "reason": reason, "source": "api"},
        )
        return year

    @staticmethod
    @transaction.atomic
    def hard_close_academic_year(*, academic_year_id, closed_by=None, reason: str = "") -> AcademicYear:
        year = AcademicYear.objects.select_for_update().get(id=academic_year_id)
        if year.status == AcademicYear.Status.HARD_CLOSED:
            return year
        year.status = AcademicYear.Status.HARD_CLOSED
        year.is_active = False
        year._allow_hard_closed_update = True
        year.save(update_fields=["status", "is_active", "updated_at"])
        for period in year.periods.exclude(status=AcademicPeriod.Status.HARD_CLOSED):
            period.status = AcademicPeriod.Status.HARD_CLOSED
            period.is_active = False
            period._allow_hard_closed_update = True
            period.save(update_fields=["status", "is_active", "updated_at"])
        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACADEMIC,
            obj=year,
            user=closed_by,
            metadata={"event": "academic_year_hard_closed", "reason": reason, "source": "api"},
        )
        return year

    @staticmethod
    def activate_new_year(*, rollover: AcademicYearRollover, activated_by=None) -> AcademicYear:
        AcademicYear.objects.filter(organization=rollover.organization).exclude(id=rollover.to_academic_year_id).update(is_active=False)
        year = rollover.to_academic_year
        year.status = AcademicYear.Status.ACTIVE
        year.is_active = True
        year.save(update_fields=["status", "is_active", "updated_at"])
        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACADEMIC,
            obj=year,
            user=activated_by,
            metadata={"event": "academic_year_activated", "rollover_id": str(rollover.id)},
        )
        return year

    @classmethod
    def cancel_rollover(cls, *, rollover_id, cancelled_by=None, reason: str = "") -> AcademicYearRollover:
        rollover = AcademicYearRollover.objects.get(id=rollover_id)
        if rollover.status == AcademicYearRollover.Status.EXECUTED:
            raise ValidationError("Executed rollovers cannot be cancelled.")
        rollover.status = AcademicYearRollover.Status.CANCELLED
        if reason:
            rollover.notes = f"{rollover.notes}\nCancelled: {reason}".strip()
        rollover.save(update_fields=["status", "notes", "updated_at"])
        AuditLogService.record(
            action=AuditAction.SYSTEM,
            module=AuditModule.ACADEMIC,
            obj=rollover,
            user=cancelled_by,
            metadata={"event": "academic_year_rollover_cancelled", "reason": reason},
        )
        return rollover

    @staticmethod
    def get_rollover_summary(*, rollover: AcademicYearRollover) -> dict:
        return {
            "id": str(rollover.id),
            "organization": str(rollover.organization),
            "from_academic_year": rollover.from_academic_year.name,
            "to_academic_year": rollover.to_academic_year.name if rollover.to_academic_year_id else None,
            "status": rollover.status,
            "trial_balance_validated": rollover.trial_balance_validated,
            "revenue_expense_closing_completed": rollover.revenue_expense_closing_completed,
            "opening_balances_posted": rollover.opening_balances_posted,
            "executed_at": rollover.executed_at.isoformat() if rollover.executed_at else None,
        }

    @staticmethod
    def _validate_from_year(*, organization, from_academic_year):
        if from_academic_year.organization_id != organization.id:
            raise ValidationError("Source academic year must belong to the organization.")
        if from_academic_year.status == AcademicYear.Status.HARD_CLOSED:
            raise ValidationError("Cannot rollover a hard-closed academic year.")
        if from_academic_year.status not in {AcademicYear.Status.ACTIVE, AcademicYear.Status.SOFT_CLOSED}:
            raise ValidationError("Source academic year must be active or soft closed.")

    @staticmethod
    def _validate_target_year(*, organization, target_year):
        if target_year.organization_id != organization.id:
            raise ValidationError("Target academic year must belong to the organization.")
        if target_year.status == AcademicYear.Status.HARD_CLOSED:
            raise ValidationError("Target academic year cannot be hard closed.")

    @classmethod
    def _validate_required_accounts(cls, *, organization):
        cls._get_account(organization=organization, code=cls.INCOME_SUMMARY_CODE)
        cls._get_account(organization=organization, code=cls.RETAINED_EARNINGS_CODE)

    @staticmethod
    def _get_account(*, organization, code: str) -> Account:
        try:
            return Account.objects.get(organization=organization, code=code, is_active=True)
        except Account.DoesNotExist as exc:
            raise ValidationError(f"Required rollover account {code} is missing or inactive.") from exc

    @staticmethod
    def _opening_entries_exist(*, organization, to_academic_year, rollover) -> bool:
        return JournalEntry.objects.filter(
            organization=organization,
            academic_year=to_academic_year,
            source_app="academic",
            source_model="AcademicYearRollover",
            source_object_id=rollover.id,
            source_number="opening-balances",
            status=JournalEntry.Status.POSTED,
        ).exists()

    @staticmethod
    def _account_totals(*, account: Account, academic_year: AcademicYear) -> tuple[Decimal, Decimal]:
        totals = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__academic_year=academic_year,
            journal_entry__status=JournalEntry.Status.POSTED,
        ).aggregate(debit=decimal_sum("debit_amount"), credit=decimal_sum("credit_amount"))
        return quantize_money(totals["debit"]), quantize_money(totals["credit"])

    @staticmethod
    def _new_system_entry(
        *,
        rollover: AcademicYearRollover,
        academic_year: AcademicYear,
        description: str,
        source_number: str,
        posted_by=None,
        academic_period: AcademicPeriod | None = None,
    ) -> JournalEntry:
        return JournalEntry.objects.create(
            organization=rollover.organization,
            academic_year=academic_year,
            academic_period=academic_period,
            entry_number=AcademicYearRolloverService._generate_journal_entry_number(organization=rollover.organization),
            entry_date_ad=academic_year.ad_end_date if academic_year == rollover.from_academic_year else academic_year.ad_start_date,
            entry_date_bs=academic_year.bs_end_date if academic_year == rollover.from_academic_year else academic_year.bs_start_date,
            description=description,
            source_type=JournalEntry.SourceType.SYSTEM,
            source_app="academic",
            source_model="AcademicYearRollover",
            source_object_id=rollover.id,
            source_number=source_number,
            status=JournalEntry.Status.APPROVED,
            is_system_generated=True,
            created_by=posted_by,
            approved_by=posted_by,
        )

    @staticmethod
    def _add_line(*, entry: JournalEntry, account: Account, debit: Decimal, credit: Decimal) -> JournalEntryLine:
        return JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=entry.organization,
            branch=entry.branch,
            account=account,
            debit_amount=quantize_money(debit),
            credit_amount=quantize_money(credit),
        )

    @staticmethod
    def _generate_journal_entry_number(*, organization) -> str:
        count = JournalEntry.objects.select_for_update().filter(organization=organization).count() + 1
        return f"JV-{count:06d}"


def decimal_sum(field_name: str):
    from django.db.models import Sum

    return Sum(field_name, default=Decimal("0.00"))
