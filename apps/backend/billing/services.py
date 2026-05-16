from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounting.models import Account, JournalEntry, JournalEntryLine
from accounting.services import AccountingPostingService
from common.audit import AuditAction, AuditLogService, AuditModule, serialize_model_instance
from common.money import ZERO_MONEY, quantize_money

from .models import (
    BillingDiscount,
    BillingFine,
    BillingWaiver,
    BillStatus,
    StudentAdvanceBalance,
    StudentFeeDue,
    StudentInvoice,
    StudentPayment,
    StudentPaymentAllocation,
    StudentRefund,
)


@dataclass
class PaymentAllocationInput:
    amount_allocated: Decimal
    fee_due_id: str | None = None
    invoice_id: str | None = None
    invoice_item_id: str | None = None
    notes: str = ""


class StudentPaymentService:
    CASH_ACCOUNT_CODE = "1110"
    BANK_ACCOUNT_CODE = "1120"
    WALLET_ACCOUNT_CODE = "1130"
    STUDENT_RECEIVABLE_CODE = "1210"
    STUDENT_ADVANCE_REVENUE_CODE = "2210"
    FINE_INCOME_CODE = "4400"
    DISCOUNT_ALLOWED_CODE = "5700"
    BAD_DEBT_EXPENSE_CODE = "5800"

    @classmethod
    @transaction.atomic
    def create_draft_payment(
        cls,
        *,
        organization,
        branch,
        academic_year,
        student,
        payment_date_ad,
        payment_method: str,
        amount,
        created_by=None,
        payment_date_bs: str = "",
        discount_amount=ZERO_MONEY,
        fine_amount=ZERO_MONEY,
        net_received_amount=None,
        is_advance_payment: bool = False,
        reference_number: str = "",
        file_path: str = "",
        notes: str = "",
        allocations: list[PaymentAllocationInput | dict[str, Any]] | None = None,
    ) -> StudentPayment:
        amount = quantize_money(amount)
        if amount <= ZERO_MONEY:
            raise ValidationError("Payment amount must be greater than zero.")

        discount_amount = quantize_money(discount_amount)
        fine_amount = quantize_money(fine_amount)
        if net_received_amount is None:
            net_received_amount = amount - discount_amount + fine_amount
        net_received_amount = quantize_money(net_received_amount)

        allocations = allocations or []
        if is_advance_payment and allocations:
            raise ValidationError("Advance payment cannot have due/invoice allocations at draft creation.")

        payment = StudentPayment.objects.create(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            student=student,
            draft_receipt_number=cls.generate_draft_receipt_number(organization_id=organization.id),
            payment_date_ad=payment_date_ad,
            payment_date_bs=payment_date_bs,
            payment_method=payment_method,
            amount=amount,
            discount_amount=discount_amount,
            fine_amount=fine_amount,
            net_received_amount=net_received_amount,
            reference_number=reference_number,
            file_path=file_path,
            is_advance_payment=is_advance_payment,
            status=StudentPayment.Status.DRAFT,
            created_by=created_by,
            notes=notes,
        )
        payment.full_clean()
        payment.save()

        if allocations:
            normalized = cls._normalize_allocations(allocations)
            cls.validate_payment_allocations(payment=payment, allocations=normalized)
            for item in normalized:
                StudentPaymentAllocation.objects.create(
                    payment=payment,
                    fee_due_id=item.fee_due_id,
                    invoice_id=item.invoice_id,
                    invoice_item_id=item.invoice_item_id,
                    amount_allocated=item.amount_allocated,
                    notes=item.notes,
                )
        return payment

    @classmethod
    def _normalize_allocations(
        cls, allocations: list[PaymentAllocationInput | dict[str, Any]]
    ) -> list[PaymentAllocationInput]:
        normalized_by_target: dict[tuple[str, str], PaymentAllocationInput] = {}
        for item in allocations:
            if isinstance(item, PaymentAllocationInput):
                allocation = PaymentAllocationInput(
                    amount_allocated=quantize_money(item.amount_allocated),
                    fee_due_id=str(item.fee_due_id) if item.fee_due_id else None,
                    invoice_id=str(item.invoice_id) if item.invoice_id else None,
                    invoice_item_id=str(item.invoice_item_id) if item.invoice_item_id else None,
                    notes=item.notes,
                )
            else:
                allocation = PaymentAllocationInput(
                    amount_allocated=quantize_money(item["amount_allocated"]),
                    fee_due_id=str(item["fee_due_id"]) if item.get("fee_due_id") else None,
                    invoice_id=str(item["invoice_id"]) if item.get("invoice_id") else None,
                    invoice_item_id=str(item["invoice_item_id"]) if item.get("invoice_item_id") else None,
                    notes=item.get("notes", ""),
                )

            targets = [
                ("fee_due", allocation.fee_due_id),
                ("invoice", allocation.invoice_id),
                ("invoice_item", allocation.invoice_item_id),
            ]
            populated_targets = [(target_type, target_id) for target_type, target_id in targets if target_id]
            if len(populated_targets) != 1:
                raise ValidationError("Each allocation must target exactly one due, invoice, or invoice item.")

            target_key = populated_targets[0]
            existing = normalized_by_target.get(target_key)
            if existing is None:
                normalized_by_target[target_key] = allocation
                continue

            existing.amount_allocated = quantize_money(existing.amount_allocated + allocation.amount_allocated)
            if allocation.notes:
                existing.notes = f"{existing.notes}\n{allocation.notes}".strip()

        return list(normalized_by_target.values())

    @classmethod
    def validate_payment_allocations(
        cls,
        *,
        payment: StudentPayment,
        allocations: list[PaymentAllocationInput] | None = None,
    ) -> None:
        if allocations is None:
            allocations = [
                PaymentAllocationInput(
                    amount_allocated=alloc.amount_allocated,
                    fee_due_id=str(alloc.fee_due_id) if alloc.fee_due_id else None,
                    invoice_id=str(alloc.invoice_id) if alloc.invoice_id else None,
                    invoice_item_id=str(alloc.invoice_item_id) if alloc.invoice_item_id else None,
                    notes=alloc.notes,
                )
                for alloc in payment.allocations.all()
            ]

        if payment.is_advance_payment and allocations:
            raise ValidationError("Advance payments cannot include due or invoice allocations.")

        total_allocated = ZERO_MONEY
        due_running: dict[str, Decimal] = {}
        invoice_running: dict[str, Decimal] = {}

        for item in allocations:
            amount = quantize_money(item.amount_allocated)
            if amount <= ZERO_MONEY:
                raise ValidationError("Allocation amount must be greater than zero.")

            target_count = sum(1 for target in (item.fee_due_id, item.invoice_id, item.invoice_item_id) if target)
            if target_count != 1:
                raise ValidationError("Each allocation must target exactly one due, invoice, or invoice item.")

            total_allocated += amount

            if item.fee_due_id:
                due = StudentFeeDue.objects.get(id=item.fee_due_id)
                if due.student_id != payment.student_id or due.organization_id != payment.organization_id:
                    raise ValidationError("Allocation due must belong to the same student and organization.")
                due_running.setdefault(item.fee_due_id, ZERO_MONEY)
                due_running[item.fee_due_id] += amount
                if due_running[item.fee_due_id] > due.balance_amount:
                    raise ValidationError("Allocation cannot exceed due balance.")

            if item.invoice_id:
                invoice = StudentInvoice.objects.get(id=item.invoice_id)
                if invoice.student_id != payment.student_id or invoice.organization_id != payment.organization_id:
                    raise ValidationError("Allocation invoice must belong to the same student and organization.")
                invoice_running.setdefault(item.invoice_id, ZERO_MONEY)
                invoice_running[item.invoice_id] += amount
                if invoice_running[item.invoice_id] > invoice.balance_amount:
                    raise ValidationError("Allocation cannot exceed invoice balance.")

        if total_allocated > payment.amount:
            raise ValidationError("Total allocation cannot exceed payment amount.")

    @classmethod
    @transaction.atomic
    def approve_payment(cls, *, payment_id, approved_by) -> StudentPayment:
        payment = StudentPayment.objects.select_for_update().get(id=payment_id)
        if payment.created_by_id and payment.created_by_id == getattr(approved_by, "id", None):
            raise ValidationError("Maker-checker violation: payment creator cannot approve the same payment.")
        if payment.status not in {StudentPayment.Status.DRAFT, StudentPayment.Status.SUBMITTED}:
            raise ValidationError("Only draft/submitted payments can be approved.")

        payment.approved_by = approved_by
        payment.approved_at = timezone.now()
        payment.status = StudentPayment.Status.APPROVED
        payment._allow_immutable_update = True
        payment.save(update_fields=["approved_by", "approved_at", "status", "updated_at"])
        return cls.post_payment(payment_id=payment.id, approved_by=approved_by)

    @classmethod
    @transaction.atomic
    def post_payment(cls, *, payment_id, approved_by=None) -> StudentPayment:
        payment = (
            StudentPayment.objects.select_for_update()
            .select_related("organization", "branch", "academic_year", "student", "approved_by", "created_by")
            .get(id=payment_id)
        )

        if payment.status == StudentPayment.Status.POSTED:
            return payment

        if payment.created_by_id and approved_by and payment.created_by_id == approved_by.id:
            raise ValidationError("Maker-checker violation: payment creator cannot approve/post the same payment.")

        allocations = list(payment.allocations.select_for_update())
        cls.validate_payment_allocations(payment=payment)

        if not payment.is_advance_payment and not allocations:
            raise ValidationError("Non-advance payment requires at least one allocation.")

        if not payment.receipt_number:
            payment.receipt_number = cls.generate_official_receipt_number(organization_id=payment.organization_id)

        if approved_by and not payment.approved_by_id:
            payment.approved_by = approved_by
            payment.approved_at = timezone.now()

        if payment.is_advance_payment:
            cls.apply_advance_payment(payment=payment)
        else:
            cls.apply_payment_to_dues(payment=payment, allocations=allocations)

        journal_entry = cls._create_payment_journal_entry(payment=payment, posted_by=approved_by or payment.approved_by)

        payment.status = StudentPayment.Status.POSTED
        payment.posted_at = timezone.now()
        payment._allow_immutable_update = True
        payment.save(
            update_fields=[
                "receipt_number",
                "approved_by",
                "approved_at",
                "status",
                "posted_at",
                "updated_at",
            ]
        )

        AuditLogService.record_model_change(
            action=AuditAction.POST,
            module=AuditModule.BILLING,
            instance=payment,
            user=approved_by or payment.approved_by,
            after_data=serialize_model_instance(
                payment,
                fields=["receipt_number", "status", "posted_at", "approved_by", "approved_at"],
            ),
            metadata={"event": "student_payment_posted", "journal_entry_id": str(journal_entry.id)},
        )
        return payment

    @classmethod
    def void_payment_placeholder(cls, *, payment_id, reason: str, voided_by=None) -> StudentPayment:
        payment = StudentPayment.objects.get(id=payment_id)
        if payment.status == StudentPayment.Status.POSTED:
            raise ValidationError("Void workflow with reversal is not implemented yet.")
        payment.void_reason = reason
        payment.voided_by = voided_by
        payment.voided_at = timezone.now()
        payment.status = StudentPayment.Status.VOIDED
        payment._allow_immutable_update = True
        payment.save(update_fields=["void_reason", "voided_by", "voided_at", "status", "updated_at"])
        return payment

    @classmethod
    def apply_payment_to_dues(cls, *, payment: StudentPayment, allocations: list[StudentPaymentAllocation]) -> None:
        for alloc in allocations:
            amount = quantize_money(alloc.amount_allocated)

            if alloc.fee_due_id:
                due = StudentFeeDue.objects.select_for_update().get(id=alloc.fee_due_id)
                due.paid_amount = quantize_money(due.paid_amount + amount)
                if due.paid_amount > due.net_amount:
                    raise ValidationError("Due paid amount cannot exceed due net amount.")
                due.balance_amount = quantize_money(due.net_amount - due.paid_amount)
                if due.balance_amount == ZERO_MONEY:
                    due.status = BillStatus.PAID
                elif due.paid_amount > ZERO_MONEY:
                    due.status = BillStatus.PARTIAL
                elif due.status in {BillStatus.APPROVED, BillStatus.DRAFT, BillStatus.PENDING_APPROVAL}:
                    due.status = BillStatus.UNPAID
                due.save(update_fields=["paid_amount", "balance_amount", "status", "updated_at"])

            if alloc.invoice_id:
                invoice = StudentInvoice.objects.select_for_update().get(id=alloc.invoice_id)
                invoice.paid_amount = quantize_money(invoice.paid_amount + amount)
                if invoice.paid_amount > invoice.total_amount:
                    raise ValidationError("Invoice paid amount cannot exceed invoice total amount.")
                invoice.balance_amount = quantize_money(invoice.total_amount - invoice.paid_amount)
                if invoice.balance_amount == ZERO_MONEY:
                    invoice.status = BillStatus.PAID
                elif invoice.paid_amount > ZERO_MONEY:
                    invoice.status = BillStatus.PARTIAL
                elif invoice.status in {BillStatus.APPROVED, BillStatus.DRAFT, BillStatus.PENDING_APPROVAL}:
                    invoice.status = BillStatus.UNPAID
                invoice.save(update_fields=["paid_amount", "balance_amount", "status", "updated_at"])

    @classmethod
    def apply_advance_payment(cls, *, payment: StudentPayment) -> StudentAdvanceBalance:
        advance_balance, _ = StudentAdvanceBalance.objects.select_for_update().get_or_create(
            organization=payment.organization,
            branch=payment.branch,
            academic_year=payment.academic_year,
            student=payment.student,
            defaults={
                "opening_amount": ZERO_MONEY,
                "received_amount": ZERO_MONEY,
                "applied_amount": ZERO_MONEY,
                "refunded_amount": ZERO_MONEY,
                "balance_amount": ZERO_MONEY,
            },
        )
        advance_balance.received_amount = quantize_money(advance_balance.received_amount + payment.amount)
        advance_balance.balance_amount = quantize_money(
            advance_balance.opening_amount
            + advance_balance.received_amount
            - advance_balance.applied_amount
            - advance_balance.refunded_amount
        )
        advance_balance.save(update_fields=["received_amount", "balance_amount", "updated_at"])
        return advance_balance

    @classmethod
    def generate_draft_receipt_number(cls, *, organization_id) -> str:
        prefix = "DR"
        sequence = cls._next_payment_sequence(organization_id=organization_id)
        return f"{prefix}-{sequence:06d}"

    @classmethod
    def generate_official_receipt_number(cls, *, organization_id) -> str:
        prefix = "RC"
        sequence = cls._next_payment_sequence(organization_id=organization_id)
        return f"{prefix}-{sequence:06d}"

    @classmethod
    def _next_payment_sequence(cls, *, organization_id) -> int:
        last_payment = (
            StudentPayment.objects.select_for_update()
            .filter(organization_id=organization_id)
            .order_by("-created_at", "-id")
            .first()
        )
        if last_payment is None:
            return 1
        return StudentPayment.objects.filter(organization_id=organization_id).count() + 1

    @classmethod
    def _create_payment_journal_entry(cls, *, payment: StudentPayment, posted_by=None) -> JournalEntry:
        debit_account = cls._resolve_debit_account(payment=payment)
        credit_account = cls._resolve_credit_account(payment=payment)
        entry_number = cls._generate_journal_entry_number(organization_id=payment.organization_id)

        journal_entry = JournalEntry.objects.create(
            organization=payment.organization,
            branch=payment.branch,
            academic_year=payment.academic_year,
            entry_number=entry_number,
            entry_date_ad=payment.payment_date_ad,
            entry_date_bs=payment.payment_date_bs or "",
            description=f"Student payment {payment.receipt_number or payment.draft_receipt_number}",
            narration=payment.notes,
            source_type=JournalEntry.SourceType.SYSTEM,
            source_app="billing",
            source_model="StudentPayment",
            source_object_id=payment.id,
            source_number=payment.receipt_number or payment.draft_receipt_number or "",
            status=JournalEntry.Status.APPROVED,
            is_system_generated=True,
            created_by=payment.created_by,
            approved_by=payment.approved_by,
        )

        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            organization=payment.organization,
            branch=payment.branch,
            account=debit_account,
            debit_amount=payment.amount,
            credit_amount=ZERO_MONEY,
            student_id=payment.student_id,
        )
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            organization=payment.organization,
            branch=payment.branch,
            account=credit_account,
            debit_amount=ZERO_MONEY,
            credit_amount=payment.amount,
            student_id=payment.student_id,
        )
        return AccountingPostingService.post_journal_entry(journal_entry, posted_by=posted_by)

    @classmethod
    def _generate_journal_entry_number(cls, *, organization_id) -> str:
        last_entry = (
            JournalEntry.objects.select_for_update()
            .filter(organization_id=organization_id)
            .order_by("-created_at", "-id")
            .first()
        )
        if last_entry is None:
            sequence = 1
        else:
            sequence = JournalEntry.objects.filter(organization_id=organization_id).count() + 1
        return f"JV-{sequence:06d}"

    @classmethod
    def _resolve_debit_account(cls, *, payment: StudentPayment) -> Account:
        if payment.payment_method == StudentPayment.PaymentMethod.CASH:
            return cls._get_account_by_code(organization_id=payment.organization_id, code=cls.CASH_ACCOUNT_CODE)
        if payment.payment_method == StudentPayment.PaymentMethod.WALLET:
            return cls._get_account_by_code(organization_id=payment.organization_id, code=cls.WALLET_ACCOUNT_CODE)
        return cls._get_account_by_code(organization_id=payment.organization_id, code=cls.BANK_ACCOUNT_CODE)

    @classmethod
    def _resolve_credit_account(cls, *, payment: StudentPayment) -> Account:
        if payment.is_advance_payment:
            return cls._get_account_by_code(organization_id=payment.organization_id, code=cls.STUDENT_ADVANCE_REVENUE_CODE)
        return cls._get_account_by_code(organization_id=payment.organization_id, code=cls.STUDENT_RECEIVABLE_CODE)

    @staticmethod
    def _get_account_by_code(*, organization_id, code: str) -> Account:
        try:
            return Account.objects.get(organization_id=organization_id, code=code, is_active=True)
        except Account.DoesNotExist as exc:
            raise ValidationError(f"Missing accounting account configuration for code `{code}`.") from exc


class AdvanceApplicationService(StudentPaymentService):
    @classmethod
    @transaction.atomic
    def apply_advance_to_due(cls, *, student, due_id, amount, applied_by=None) -> StudentFeeDue:
        due = StudentFeeDue.objects.select_for_update().get(id=due_id)
        cls._validate_advance_target_scope(student=student, due=due)
        amount = quantize_money(amount)
        if amount <= ZERO_MONEY:
            raise ValidationError("Advance application amount must be greater than zero.")
        if amount > due.balance_amount:
            raise ValidationError("Advance application cannot exceed due balance.")

        cls.validate_available_advance_balance(
            organization=due.organization,
            branch=due.branch,
            academic_year=due.academic_year,
            student=student,
            amount=amount,
        )

        cls.update_student_advance_balance(
            organization=due.organization,
            branch=due.branch,
            academic_year=due.academic_year,
            student=student,
            applied_amount=amount,
        )
        cls.update_due_or_invoice_balance(target=due, amount=amount)
        journal = cls.post_advance_application_journal(
            organization=due.organization,
            branch=due.branch,
            academic_year=due.academic_year,
            student=student,
            amount=amount,
            entry_date_ad=timezone.now().date(),
            entry_date_bs="",
            posted_by=applied_by,
            source_number=f"ADV-APPLY-DUE-{due.id}",
        )
        AuditLogService.record(
            action=AuditAction.POST,
            module=AuditModule.BILLING,
            obj=due,
            user=applied_by,
            metadata={"event": "advance_applied_to_due", "amount": str(amount), "journal_entry_id": str(journal.id)},
        )
        return due

    @classmethod
    @transaction.atomic
    def apply_advance_to_invoice(cls, *, student, invoice_id, amount, applied_by=None) -> StudentInvoice:
        invoice = StudentInvoice.objects.select_for_update().get(id=invoice_id)
        cls._validate_advance_target_scope(student=student, invoice=invoice)
        amount = quantize_money(amount)
        if amount <= ZERO_MONEY:
            raise ValidationError("Advance application amount must be greater than zero.")
        if amount > invoice.balance_amount:
            raise ValidationError("Advance application cannot exceed invoice balance.")

        cls.validate_available_advance_balance(
            organization=invoice.organization,
            branch=invoice.branch,
            academic_year=invoice.academic_year,
            student=student,
            amount=amount,
        )
        cls.update_student_advance_balance(
            organization=invoice.organization,
            branch=invoice.branch,
            academic_year=invoice.academic_year,
            student=student,
            applied_amount=amount,
        )
        cls.update_due_or_invoice_balance(target=invoice, amount=amount)
        journal = cls.post_advance_application_journal(
            organization=invoice.organization,
            branch=invoice.branch,
            academic_year=invoice.academic_year,
            student=student,
            amount=amount,
            entry_date_ad=timezone.now().date(),
            entry_date_bs="",
            posted_by=applied_by,
            source_number=f"ADV-APPLY-INV-{invoice.id}",
        )
        AuditLogService.record(
            action=AuditAction.POST,
            module=AuditModule.BILLING,
            obj=invoice,
            user=applied_by,
            metadata={"event": "advance_applied_to_invoice", "amount": str(amount), "journal_entry_id": str(journal.id)},
        )
        return invoice

    @classmethod
    def _validate_advance_target_scope(cls, *, student, due=None, invoice=None) -> None:
        target = due or invoice
        if student.id != target.student_id:
            raise ValidationError("Advance application student must match the target due/invoice student.")
        if student.organization_id != target.organization_id or student.branch_id != target.branch_id:
            raise ValidationError("Advance application scope mismatch for organization/branch.")
        if student.academic_year_id != target.academic_year_id:
            raise ValidationError("Advance application academic year mismatch.")

    @classmethod
    def validate_available_advance_balance(cls, *, organization, branch, academic_year, student, amount: Decimal) -> None:
        balance = (
            StudentAdvanceBalance.objects.select_for_update()
            .filter(organization=organization, branch=branch, academic_year=academic_year, student=student)
            .first()
        )
        available = balance.balance_amount if balance else ZERO_MONEY
        if amount > available:
            raise ValidationError("Advance application exceeds available advance balance.")

    @classmethod
    def update_student_advance_balance(
        cls,
        *,
        organization,
        branch,
        academic_year,
        student,
        applied_amount=ZERO_MONEY,
        refunded_amount=ZERO_MONEY,
    ) -> StudentAdvanceBalance:
        advance, _ = StudentAdvanceBalance.objects.select_for_update().get_or_create(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            student=student,
            defaults={
                "opening_amount": ZERO_MONEY,
                "received_amount": ZERO_MONEY,
                "applied_amount": ZERO_MONEY,
                "refunded_amount": ZERO_MONEY,
                "balance_amount": ZERO_MONEY,
            },
        )
        advance.applied_amount = quantize_money(advance.applied_amount + quantize_money(applied_amount))
        advance.refunded_amount = quantize_money(advance.refunded_amount + quantize_money(refunded_amount))
        advance.balance_amount = quantize_money(
            advance.opening_amount + advance.received_amount - advance.applied_amount - advance.refunded_amount
        )
        if advance.balance_amount < ZERO_MONEY:
            raise ValidationError("Advance balance cannot be negative.")
        advance.save(update_fields=["applied_amount", "refunded_amount", "balance_amount", "updated_at"])
        return advance

    @classmethod
    def update_due_or_invoice_balance(cls, *, target, amount: Decimal):
        amount = quantize_money(amount)
        if isinstance(target, StudentFeeDue):
            target.paid_amount = quantize_money(target.paid_amount + amount)
            if target.paid_amount > target.net_amount:
                raise ValidationError("Due paid amount cannot exceed due net amount.")
            target.balance_amount = quantize_money(target.net_amount - target.paid_amount)
            if target.balance_amount == ZERO_MONEY:
                target.status = BillStatus.PAID
            elif target.paid_amount > ZERO_MONEY:
                target.status = BillStatus.PARTIAL
            target.save(update_fields=["paid_amount", "balance_amount", "status", "updated_at"])
        else:
            target.paid_amount = quantize_money(target.paid_amount + amount)
            if target.paid_amount > target.total_amount:
                raise ValidationError("Invoice paid amount cannot exceed invoice total amount.")
            target.balance_amount = quantize_money(target.total_amount - target.paid_amount)
            if target.balance_amount == ZERO_MONEY:
                target.status = BillStatus.PAID
            elif target.paid_amount > ZERO_MONEY:
                target.status = BillStatus.PARTIAL
            target.save(update_fields=["paid_amount", "balance_amount", "status", "updated_at"])
        return target

    @classmethod
    def post_advance_application_journal(
        cls,
        *,
        organization,
        branch,
        academic_year,
        student,
        amount: Decimal,
        entry_date_ad,
        entry_date_bs,
        posted_by=None,
        source_number: str = "",
    ) -> JournalEntry:
        debit_account = cls._get_account_by_code(organization_id=organization.id, code=cls.STUDENT_ADVANCE_REVENUE_CODE)
        credit_account = cls._get_account_by_code(organization_id=organization.id, code=cls.STUDENT_RECEIVABLE_CODE)
        entry_number = cls._generate_journal_entry_number(organization_id=organization.id)
        entry = JournalEntry.objects.create(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            entry_number=entry_number,
            entry_date_ad=entry_date_ad,
            entry_date_bs=entry_date_bs or "",
            description="Advance application to receivable",
            source_type=JournalEntry.SourceType.SYSTEM,
            source_app="billing",
            source_model="AdvanceApplication",
            source_number=source_number,
            status=JournalEntry.Status.APPROVED,
            is_system_generated=True,
            created_by=posted_by,
            approved_by=posted_by,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=organization,
            branch=branch,
            account=debit_account,
            debit_amount=amount,
            credit_amount=ZERO_MONEY,
            student_id=student.id,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=organization,
            branch=branch,
            account=credit_account,
            debit_amount=ZERO_MONEY,
            credit_amount=amount,
            student_id=student.id,
        )
        return AccountingPostingService.post_journal_entry(entry, posted_by=posted_by)


class BillingAdjustmentService(StudentPaymentService):
    @classmethod
    @transaction.atomic
    def approve_discount(cls, *, discount_id, approved_by):
        discount = BillingDiscount.objects.select_for_update().get(id=discount_id)
        cls._validate_maker_checker(discount=discount, approver=approved_by)
        amount = cls._resolve_discount_amount(discount=discount)
        target = cls._get_discount_target(discount)
        if amount <= ZERO_MONEY:
            raise ValidationError("Discount amount must be greater than zero.")
        if amount > target.balance_amount:
            raise ValidationError("Discount cannot exceed due/invoice balance.")

        cls._apply_discount_to_target(target=target, amount=amount)
        journal = cls._post_adjustment_journal(
            organization=discount.organization,
            branch=discount.branch,
            academic_year=discount.academic_year,
            student=discount.student,
            amount=amount,
            debit_code=cls.DISCOUNT_ALLOWED_CODE,
            credit_code=cls.STUDENT_RECEIVABLE_CODE,
            description="Discount approved",
            source_model="BillingDiscount",
            source_number=str(discount.id),
            posted_by=approved_by,
        )
        discount.status = BillingDiscount.Status.APPROVED
        discount.approved_by = approved_by
        discount.approved_at = timezone.now()
        discount._allow_immutable_update = True
        discount.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        AuditLogService.record(
            action=AuditAction.APPROVE,
            module=AuditModule.BILLING,
            obj=discount,
            user=approved_by,
            metadata={"event": "discount_approved", "amount": str(amount), "journal_entry_id": str(journal.id)},
        )
        return discount

    @classmethod
    @transaction.atomic
    def approve_waiver(cls, *, waiver_id, approved_by):
        waiver = BillingWaiver.objects.select_for_update().get(id=waiver_id)
        amount = quantize_money(waiver.waiver_amount)
        if amount <= ZERO_MONEY:
            raise ValidationError("Waiver amount must be greater than zero.")
        target = waiver.fee_due or waiver.invoice
        if target is None:
            raise ValidationError("Waiver must target either a due or an invoice.")
        if amount > target.balance_amount:
            raise ValidationError("Waiver cannot exceed due/invoice balance.")

        cls._apply_writeoff_to_target(target=target, amount=amount)
        journal = cls._post_adjustment_journal(
            organization=waiver.organization,
            branch=waiver.branch,
            academic_year=waiver.academic_year,
            student=waiver.student,
            amount=amount,
            debit_code=cls.BAD_DEBT_EXPENSE_CODE,
            credit_code=cls.STUDENT_RECEIVABLE_CODE,
            description="Waiver/write-off approved",
            source_model="BillingWaiver",
            source_number=str(waiver.id),
            posted_by=approved_by,
        )
        waiver.status = BillingWaiver.Status.APPROVED
        waiver.approved_by = approved_by
        waiver.approved_at = timezone.now()
        waiver._allow_immutable_update = True
        waiver.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        AuditLogService.record(
            action=AuditAction.APPROVE,
            module=AuditModule.BILLING,
            obj=waiver,
            user=approved_by,
            metadata={"event": "waiver_approved", "amount": str(amount), "journal_entry_id": str(journal.id)},
        )
        return waiver

    @classmethod
    @transaction.atomic
    def approve_fine(cls, *, fine_id, approved_by):
        fine = BillingFine.objects.select_for_update().get(id=fine_id)
        amount = quantize_money(fine.amount)
        if amount <= ZERO_MONEY:
            raise ValidationError("Fine amount must be greater than zero.")
        target = fine.fee_due or fine.invoice
        if target is None:
            raise ValidationError("Fine must target either a due or an invoice.")

        cls._apply_fine_to_target(target=target, amount=amount)
        journal = cls._post_adjustment_journal(
            organization=fine.organization,
            branch=fine.branch,
            academic_year=fine.academic_year,
            student=fine.student,
            amount=amount,
            debit_code=cls.STUDENT_RECEIVABLE_CODE,
            credit_code=cls.FINE_INCOME_CODE,
            description="Fine approved",
            source_model="BillingFine",
            source_number=str(fine.id),
            posted_by=approved_by,
        )
        fine.status = BillingFine.Status.APPROVED
        fine.approved_by = approved_by
        fine.approved_at = timezone.now()
        fine._allow_immutable_update = True
        fine.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        AuditLogService.record(
            action=AuditAction.APPROVE,
            module=AuditModule.BILLING,
            obj=fine,
            user=approved_by,
            metadata={"event": "fine_approved", "amount": str(amount), "journal_entry_id": str(journal.id)},
        )
        return fine

    @classmethod
    def reject_adjustment(cls, *, adjustment, rejected_by=None, reason: str = ""):
        if hasattr(adjustment, "Status"):
            rejected_value = getattr(adjustment.Status, "REJECTED", None)
            if rejected_value is None:
                raise ValidationError("Adjustment does not support rejection.")
            adjustment.status = rejected_value
            if hasattr(adjustment, "notes") and reason:
                adjustment.notes = f"{adjustment.notes}\nRejected: {reason}".strip()
            adjustment.save(update_fields=["status", "notes", "updated_at"] if hasattr(adjustment, "notes") else ["status", "updated_at"])
            AuditLogService.record(
                action=AuditAction.UPDATE,
                module=AuditModule.BILLING,
                obj=adjustment,
                user=rejected_by,
                metadata={"event": "adjustment_rejected", "reason": reason},
            )
        return adjustment

    @classmethod
    def cancel_adjustment_placeholder(cls, *, adjustment, cancelled_by=None, reason: str = ""):
        if hasattr(adjustment, "Status") and hasattr(adjustment.Status, "CANCELLED"):
            adjustment.status = adjustment.Status.CANCELLED
            if hasattr(adjustment, "notes") and reason:
                adjustment.notes = f"{adjustment.notes}\nCancelled: {reason}".strip()
            adjustment.save(update_fields=["status", "notes", "updated_at"] if hasattr(adjustment, "notes") else ["status", "updated_at"])
            AuditLogService.record(
                action=AuditAction.UPDATE,
                module=AuditModule.BILLING,
                obj=adjustment,
                user=cancelled_by,
                metadata={"event": "adjustment_cancelled", "reason": reason},
            )
        return adjustment

    @classmethod
    def _validate_maker_checker(cls, *, discount: BillingDiscount, approver) -> None:
        if hasattr(discount, "created_by_id") and discount.created_by_id and discount.created_by_id == approver.id:
            raise ValidationError("Maker-checker violation: creator cannot approve discount.")

    @classmethod
    def _resolve_discount_amount(cls, *, discount: BillingDiscount) -> Decimal:
        target = cls._get_discount_target(discount)
        if discount.discount_amount is not None:
            return quantize_money(discount.discount_amount)
        if discount.discount_percentage is None:
            raise ValidationError("Discount requires either amount or percentage.")
        return quantize_money(target.balance_amount * (discount.discount_percentage / Decimal("100")))

    @classmethod
    def _get_discount_target(cls, discount: BillingDiscount):
        target = discount.fee_due or discount.invoice
        if target is None:
            raise ValidationError("Discount must target either a due or an invoice.")
        return target

    @classmethod
    def _apply_discount_to_target(cls, *, target, amount: Decimal) -> None:
        if isinstance(target, StudentFeeDue):
            target.discount_amount = quantize_money(target.discount_amount + amount)
            target.net_amount = quantize_money(target.original_amount - target.discount_amount + target.fine_amount)
            if target.paid_amount > target.net_amount:
                raise ValidationError("Discount causes paid amount to exceed due net amount.")
            target.balance_amount = quantize_money(target.net_amount - target.paid_amount)
            if target.balance_amount == ZERO_MONEY and target.paid_amount == target.net_amount:
                target.status = BillStatus.PAID
            elif target.paid_amount > ZERO_MONEY:
                target.status = BillStatus.PARTIAL
            else:
                target.status = BillStatus.UNPAID
            target.save(update_fields=["discount_amount", "net_amount", "balance_amount", "status", "updated_at"])
        else:
            target.discount_amount = quantize_money(target.discount_amount + amount)
            target.total_amount = quantize_money(target.subtotal - target.discount_amount + target.fine_amount)
            if target.paid_amount > target.total_amount:
                raise ValidationError("Discount causes paid amount to exceed invoice total amount.")
            target.balance_amount = quantize_money(target.total_amount - target.paid_amount)
            if target.balance_amount == ZERO_MONEY and target.paid_amount == target.total_amount:
                target.status = BillStatus.PAID
            elif target.paid_amount > ZERO_MONEY:
                target.status = BillStatus.PARTIAL
            else:
                target.status = BillStatus.UNPAID
            target.save(update_fields=["discount_amount", "total_amount", "balance_amount", "status", "updated_at"])

    @classmethod
    def _apply_writeoff_to_target(cls, *, target, amount: Decimal) -> None:
        if isinstance(target, StudentFeeDue):
            target.paid_amount = quantize_money(target.paid_amount + amount)
            if target.paid_amount > target.net_amount:
                raise ValidationError("Waiver causes paid amount to exceed due net amount.")
            target.balance_amount = quantize_money(target.net_amount - target.paid_amount)
            target.status = BillStatus.WRITTEN_OFF if target.balance_amount == ZERO_MONEY else BillStatus.PARTIAL
            target.save(update_fields=["paid_amount", "balance_amount", "status", "updated_at"])
        else:
            target.paid_amount = quantize_money(target.paid_amount + amount)
            if target.paid_amount > target.total_amount:
                raise ValidationError("Waiver causes paid amount to exceed invoice total amount.")
            target.balance_amount = quantize_money(target.total_amount - target.paid_amount)
            target.status = BillStatus.WRITTEN_OFF if target.balance_amount == ZERO_MONEY else BillStatus.PARTIAL
            target.save(update_fields=["paid_amount", "balance_amount", "status", "updated_at"])

    @classmethod
    def _apply_fine_to_target(cls, *, target, amount: Decimal) -> None:
        if isinstance(target, StudentFeeDue):
            target.fine_amount = quantize_money(target.fine_amount + amount)
            target.net_amount = quantize_money(target.original_amount - target.discount_amount + target.fine_amount)
            target.balance_amount = quantize_money(target.net_amount - target.paid_amount)
            target.status = BillStatus.PARTIAL if target.paid_amount > ZERO_MONEY else BillStatus.UNPAID
            target.save(update_fields=["fine_amount", "net_amount", "balance_amount", "status", "updated_at"])
        else:
            target.fine_amount = quantize_money(target.fine_amount + amount)
            target.total_amount = quantize_money(target.subtotal - target.discount_amount + target.fine_amount)
            target.balance_amount = quantize_money(target.total_amount - target.paid_amount)
            target.status = BillStatus.PARTIAL if target.paid_amount > ZERO_MONEY else BillStatus.UNPAID
            target.save(update_fields=["fine_amount", "total_amount", "balance_amount", "status", "updated_at"])

    @classmethod
    def _post_adjustment_journal(
        cls,
        *,
        organization,
        branch,
        academic_year,
        student,
        amount: Decimal,
        debit_code: str,
        credit_code: str,
        description: str,
        source_model: str,
        source_number: str,
        posted_by=None,
    ) -> JournalEntry:
        debit = cls._get_account_by_code(organization_id=organization.id, code=debit_code)
        credit = cls._get_account_by_code(organization_id=organization.id, code=credit_code)
        entry = JournalEntry.objects.create(
            organization=organization,
            branch=branch,
            academic_year=academic_year,
            entry_number=cls._generate_journal_entry_number(organization_id=organization.id),
            entry_date_ad=timezone.now().date(),
            entry_date_bs="",
            description=description,
            source_type=JournalEntry.SourceType.SYSTEM,
            source_app="billing",
            source_model=source_model,
            source_number=source_number,
            status=JournalEntry.Status.APPROVED,
            is_system_generated=True,
            created_by=posted_by,
            approved_by=posted_by,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=organization,
            branch=branch,
            account=debit,
            debit_amount=amount,
            credit_amount=ZERO_MONEY,
            student_id=student.id,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=organization,
            branch=branch,
            account=credit,
            debit_amount=ZERO_MONEY,
            credit_amount=amount,
            student_id=student.id,
        )
        return AccountingPostingService.post_journal_entry(entry, posted_by=posted_by)


class StudentRefundService(StudentPaymentService):
    @classmethod
    @transaction.atomic
    def approve_refund(cls, *, refund_id, approved_by):
        refund = StudentRefund.objects.select_for_update().get(id=refund_id)
        if refund.requested_by_id and refund.requested_by_id == approved_by.id:
            raise ValidationError("Maker-checker violation: requester cannot approve refund.")
        if refund.status not in {StudentRefund.Status.DRAFT, StudentRefund.Status.PENDING_APPROVAL}:
            raise ValidationError("Only draft/pending refunds can be approved.")
        cls.validate_refund_source(refund=refund)
        refund.status = StudentRefund.Status.APPROVED
        refund.approved_by = approved_by
        refund.approved_at = timezone.now()
        refund.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        AuditLogService.record(
            action=AuditAction.APPROVE,
            module=AuditModule.BILLING,
            obj=refund,
            user=approved_by,
            metadata={"event": "refund_approved", "amount": str(refund.refund_amount)},
        )
        return refund

    @classmethod
    @transaction.atomic
    def pay_refund(cls, *, refund_id, paid_by):
        refund = StudentRefund.objects.select_for_update().get(id=refund_id)
        if refund.status != StudentRefund.Status.APPROVED:
            raise ValidationError("Only approved refunds can be paid.")
        cls.validate_refund_source(refund=refund)
        amount = quantize_money(refund.refund_amount)
        if amount <= ZERO_MONEY:
            raise ValidationError("Refund amount must be greater than zero.")

        advance = StudentAdvanceBalance.objects.select_for_update().filter(
            organization=refund.organization,
            branch=refund.branch,
            academic_year=refund.academic_year,
            student=refund.student,
        ).first()
        available = advance.balance_amount if advance else ZERO_MONEY
        if amount > available:
            raise ValidationError("Refund amount exceeds available advance balance.")

        AdvanceApplicationService.update_student_advance_balance(
            organization=refund.organization,
            branch=refund.branch,
            academic_year=refund.academic_year,
            student=refund.student,
            refunded_amount=amount,
        )
        journal = cls.post_refund_journal(refund=refund, posted_by=paid_by)
        refund.status = StudentRefund.Status.PAID
        refund.paid_by = paid_by
        refund.paid_at = timezone.now()
        refund._allow_immutable_update = True
        refund.save(update_fields=["status", "paid_by", "paid_at", "updated_at"])
        AuditLogService.record(
            action=AuditAction.POST,
            module=AuditModule.BILLING,
            obj=refund,
            user=paid_by,
            metadata={"event": "refund_paid", "amount": str(amount), "journal_entry_id": str(journal.id)},
        )
        return refund

    @classmethod
    def cancel_refund_placeholder(cls, *, refund_id, cancelled_by=None, reason: str = ""):
        refund = StudentRefund.objects.get(id=refund_id)
        if refund.status == StudentRefund.Status.PAID:
            raise ValidationError("Cannot cancel a paid refund.")
        refund.status = StudentRefund.Status.CANCELLED
        if reason:
            refund.notes = f"{refund.notes}\nCancelled: {reason}".strip()
        refund.save(update_fields=["status", "notes", "updated_at"])
        AuditLogService.record(
            action=AuditAction.UPDATE,
            module=AuditModule.BILLING,
            obj=refund,
            user=cancelled_by,
            metadata={"event": "refund_cancelled", "reason": reason},
        )
        return refund

    @classmethod
    def validate_refund_source(cls, *, refund: StudentRefund):
        if refund.original_payment_id:
            if not refund.original_payment.is_advance_payment:
                raise ValidationError(
                    "Refund from recognized revenue is blocked: accounting policy for recognized-revenue refund is not configured."
                )
        else:
            # Without original payment reference, only advance-balance-backed refund is allowed.
            advance = StudentAdvanceBalance.objects.filter(
                organization=refund.organization,
                branch=refund.branch,
                academic_year=refund.academic_year,
                student=refund.student,
            ).first()
            available = advance.balance_amount if advance else ZERO_MONEY
            if quantize_money(refund.refund_amount) > available:
                raise ValidationError("Refund requires sufficient advance balance when original payment is not provided.")

    @classmethod
    def post_refund_journal(cls, *, refund: StudentRefund, posted_by=None):
        debit = cls._get_account_by_code(organization_id=refund.organization_id, code=cls.STUDENT_ADVANCE_REVENUE_CODE)
        credit = cls._resolve_refund_cash_bank_account(refund=refund)
        amount = quantize_money(refund.refund_amount)
        entry = JournalEntry.objects.create(
            organization=refund.organization,
            branch=refund.branch,
            academic_year=refund.academic_year,
            entry_number=cls._generate_journal_entry_number(organization_id=refund.organization_id),
            entry_date_ad=refund.refund_date_ad or timezone.now().date(),
            entry_date_bs=refund.refund_date_bs or "",
            description=f"Student refund {refund.refund_voucher_number or refund.id}",
            source_type=JournalEntry.SourceType.SYSTEM,
            source_app="billing",
            source_model="StudentRefund",
            source_object_id=refund.id,
            source_number=refund.refund_voucher_number or "",
            status=JournalEntry.Status.APPROVED,
            is_system_generated=True,
            created_by=posted_by,
            approved_by=refund.approved_by or posted_by,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=refund.organization,
            branch=refund.branch,
            account=debit,
            debit_amount=amount,
            credit_amount=ZERO_MONEY,
            student_id=refund.student_id,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            organization=refund.organization,
            branch=refund.branch,
            account=credit,
            debit_amount=ZERO_MONEY,
            credit_amount=amount,
            student_id=refund.student_id,
        )
        return AccountingPostingService.post_journal_entry(entry, posted_by=posted_by)

    @classmethod
    def _resolve_refund_cash_bank_account(cls, *, refund: StudentRefund) -> Account:
        original = refund.original_payment
        if original and original.payment_method == StudentPayment.PaymentMethod.CASH:
            return cls._get_account_by_code(organization_id=refund.organization_id, code=cls.CASH_ACCOUNT_CODE)
        if original and original.payment_method == StudentPayment.PaymentMethod.WALLET:
            return cls._get_account_by_code(organization_id=refund.organization_id, code=cls.WALLET_ACCOUNT_CODE)
        return cls._get_account_by_code(organization_id=refund.organization_id, code=cls.BANK_ACCOUNT_CODE)
