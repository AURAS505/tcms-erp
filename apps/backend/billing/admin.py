from django.contrib import admin

from .models import (
    BillingDiscount,
    BillingFine,
    BillingWaiver,
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


class FeePlanItemInline(admin.TabularInline):
    model = FeePlanItem
    extra = 0


@admin.register(FeePlan)
class FeePlanAdmin(admin.ModelAdmin):
    list_display = ("name", "branch", "academic_year", "class_room", "fee_plan_type", "billing_frequency", "is_active")
    list_filter = ("organization", "branch", "academic_year", "fee_plan_type", "billing_frequency", "is_active")
    search_fields = ("name", "class_room__class_name")
    inlines = [FeePlanItemInline]


@admin.register(FeePlanItem)
class FeePlanItemAdmin(admin.ModelAdmin):
    list_display = ("fee_plan", "item_name", "fee_type", "amount", "is_recurring", "sort_order")
    list_filter = ("fee_type", "is_recurring")
    search_fields = ("fee_plan__name", "item_name")


@admin.register(StudentFeeDue)
class StudentFeeDueAdmin(admin.ModelAdmin):
    list_display = ("student", "period_label", "due_date_ad", "net_amount", "paid_amount", "balance_amount", "status")
    list_filter = ("organization", "branch", "academic_year", "academic_period", "status")
    search_fields = ("student__admission_number", "student__full_name", "period_label")


class StudentInvoiceItemInline(admin.TabularInline):
    model = StudentInvoiceItem
    extra = 0


@admin.register(StudentInvoice)
class StudentInvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "student", "invoice_date_ad", "total_amount", "paid_amount", "balance_amount", "status")
    list_filter = ("organization", "branch", "academic_year", "academic_period", "status")
    search_fields = ("invoice_number", "student__admission_number", "student__full_name")
    inlines = [StudentInvoiceItemInline]


@admin.register(StudentInvoiceItem)
class StudentInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "description", "fee_type", "quantity", "unit_amount", "line_total")
    list_filter = ("fee_type",)
    search_fields = ("invoice__invoice_number", "description")


class StudentPaymentAllocationInline(admin.TabularInline):
    model = StudentPaymentAllocation
    extra = 0

    def has_change_permission(self, request, obj=None):
        if obj and obj.status in {StudentPayment.Status.POSTED, StudentPayment.Status.VOIDED, StudentPayment.Status.REFUNDED}:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in {StudentPayment.Status.POSTED, StudentPayment.Status.VOIDED, StudentPayment.Status.REFUNDED}:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "draft_receipt_number", "student", "payment_date_ad", "payment_method", "amount", "status")
    list_filter = ("organization", "branch", "academic_year", "payment_method", "status", "is_advance_payment")
    search_fields = ("receipt_number", "draft_receipt_number", "student__admission_number", "student__full_name")
    inlines = [StudentPaymentAllocationInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in {StudentPayment.Status.POSTED, StudentPayment.Status.VOIDED, StudentPayment.Status.REFUNDED}:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in {StudentPayment.Status.POSTED, StudentPayment.Status.VOIDED, StudentPayment.Status.REFUNDED}:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(StudentPaymentAllocation)
class StudentPaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ("payment", "fee_due", "invoice", "invoice_item", "amount_allocated")
    search_fields = ("payment__receipt_number", "payment__draft_receipt_number", "invoice__invoice_number")


@admin.register(StudentAdvanceBalance)
class StudentAdvanceBalanceAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_year", "opening_amount", "received_amount", "applied_amount", "refunded_amount", "balance_amount")
    list_filter = ("organization", "branch", "academic_year")
    search_fields = ("student__admission_number", "student__full_name")


@admin.register(BillingDiscount)
class BillingDiscountAdmin(admin.ModelAdmin):
    list_display = ("student", "discount_type", "discount_percentage", "discount_amount", "status", "approved_by")
    list_filter = ("organization", "branch", "academic_year", "discount_type", "status")
    search_fields = ("student__admission_number", "student__full_name", "reason")


@admin.register(BillingWaiver)
class BillingWaiverAdmin(admin.ModelAdmin):
    list_display = ("student", "waiver_amount", "status", "approved_by")
    list_filter = ("organization", "branch", "academic_year", "status")
    search_fields = ("student__admission_number", "student__full_name", "reason")


@admin.register(BillingFine)
class BillingFineAdmin(admin.ModelAdmin):
    list_display = ("student", "fine_type", "amount", "status", "approved_by")
    list_filter = ("organization", "branch", "academic_year", "fine_type", "status")
    search_fields = ("student__admission_number", "student__full_name", "reason")


@admin.register(StudentRefund)
class StudentRefundAdmin(admin.ModelAdmin):
    list_display = ("refund_voucher_number", "student", "refund_date_ad", "refund_amount", "status", "approved_by", "paid_by")
    list_filter = ("organization", "branch", "academic_year", "status")
    search_fields = ("refund_voucher_number", "student__admission_number", "student__full_name", "refund_reason")
