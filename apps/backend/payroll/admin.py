from django.contrib import admin

from .models import TeacherDeduction, TeacherEarning, TeacherPayment, TeacherPaymentAllocation, TeacherPaymentBatch


@admin.register(TeacherEarning)
class TeacherEarningAdmin(admin.ModelAdmin):
    list_display = ("teacher", "earning_source", "earning_date_ad", "net_amount", "paid_amount", "balance_amount", "status")
    list_filter = ("organization", "branch", "academic_year", "earning_source", "status")
    search_fields = ("teacher__employee_number", "teacher__full_name", "period_label")

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in {
            TeacherEarning.Status.POSTED,
            TeacherEarning.Status.PAID,
            TeacherEarning.Status.CANCELLED,
            TeacherEarning.Status.REVERSED,
        }:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in {
            TeacherEarning.Status.POSTED,
            TeacherEarning.Status.PAID,
            TeacherEarning.Status.CANCELLED,
            TeacherEarning.Status.REVERSED,
        }:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(TeacherPaymentBatch)
class TeacherPaymentBatchAdmin(admin.ModelAdmin):
    list_display = ("batch_number", "batch_date_ad", "total_amount", "status", "approved_by")
    list_filter = ("organization", "branch", "academic_year", "status")
    search_fields = ("batch_number",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == TeacherPaymentBatch.Status.POSTED:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == TeacherPaymentBatch.Status.POSTED:
            return False
        return super().has_delete_permission(request, obj)


class TeacherPaymentAllocationInline(admin.TabularInline):
    model = TeacherPaymentAllocation
    extra = 0

    def has_change_permission(self, request, obj=None):
        if obj and obj.status in {TeacherPayment.Status.POSTED, TeacherPayment.Status.VOIDED}:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in {TeacherPayment.Status.POSTED, TeacherPayment.Status.VOIDED}:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(TeacherPayment)
class TeacherPaymentAdmin(admin.ModelAdmin):
    list_display = ("voucher_number", "draft_voucher_number", "teacher", "payment_date_ad", "payment_method", "amount", "status")
    list_filter = ("organization", "branch", "academic_year", "payment_method", "status")
    search_fields = ("voucher_number", "draft_voucher_number", "teacher__employee_number", "teacher__full_name")
    inlines = [TeacherPaymentAllocationInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in {TeacherPayment.Status.POSTED, TeacherPayment.Status.VOIDED}:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in {TeacherPayment.Status.POSTED, TeacherPayment.Status.VOIDED}:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(TeacherPaymentAllocation)
class TeacherPaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ("teacher_payment", "teacher_earning", "amount_allocated")
    search_fields = ("teacher_payment__voucher_number", "teacher_earning__teacher__employee_number")


@admin.register(TeacherDeduction)
class TeacherDeductionAdmin(admin.ModelAdmin):
    list_display = ("teacher", "deduction_type", "amount", "status", "approved_by")
    list_filter = ("organization", "branch", "academic_year", "deduction_type", "status")
    search_fields = ("teacher__employee_number", "teacher__full_name", "reason")

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == TeacherDeduction.Status.APPROVED:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == TeacherDeduction.Status.APPROVED:
            return False
        return super().has_delete_permission(request, obj)
