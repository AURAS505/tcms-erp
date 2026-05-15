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
    BillStatus,
    StudentAdvanceBalance,
    StudentFeeDue,
    StudentInvoice,
    StudentPayment,
    StudentPaymentAllocation,
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
        normalized: list[PaymentAllocationInput] = []
        for item in allocations:
            if isinstance(item, PaymentAllocationInput):
                normalized.append(item)
            else:
                normalized.append(
                    PaymentAllocationInput(
                        amount_allocated=quantize_money(item["amount_allocated"]),
                        fee_due_id=item.get("fee_due_id"),
                        invoice_id=item.get("invoice_id"),
                        invoice_item_id=item.get("invoice_item_id"),
                        notes=item.get("notes", ""),
                    )
                )
        return normalized

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

            if not any([item.fee_due_id, item.invoice_id, item.invoice_item_id]):
                raise ValidationError("Each allocation must target a due, invoice, or invoice item.")

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
