from django.contrib import admin

from .models import AcademicPeriod, AcademicYear, AcademicYearRollover, NepaliCalendarDay


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "status", "is_active", "bs_start_date", "bs_end_date", "ad_start_date", "ad_end_date"]
    list_filter = ["organization", "status", "is_active", "bs_start_year", "bs_end_year"]
    search_fields = ["name", "organization__display_name", "notes"]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == AcademicYear.Status.HARD_CLOSED:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ["name", "academic_year", "period_order", "bs_month_name", "bs_year", "status", "is_active"]
    list_filter = ["organization", "academic_year", "status", "is_active", "bs_year", "bs_month"]
    search_fields = ["name", "academic_year__name", "organization__display_name"]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == AcademicPeriod.Status.HARD_CLOSED:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(NepaliCalendarDay)
class NepaliCalendarDayAdmin(admin.ModelAdmin):
    list_display = ["bs_date", "ad_date", "bs_month_name", "is_month_start", "is_month_end", "is_holiday"]
    list_filter = ["bs_year", "bs_month", "is_month_start", "is_month_end", "is_holiday"]
    search_fields = ["bs_date", "bs_month_name", "notes"]


@admin.register(AcademicYearRollover)
class AcademicYearRolloverAdmin(admin.ModelAdmin):
    list_display = [
        "organization",
        "from_academic_year",
        "to_academic_year",
        "status",
        "trial_balance_validated",
        "revenue_expense_closing_completed",
        "opening_balances_posted",
        "executed_at",
    ]
    list_filter = ["organization", "status", "trial_balance_validated", "revenue_expense_closing_completed"]
    search_fields = ["organization__display_name", "from_academic_year__name", "to_academic_year__name", "notes"]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == AcademicYearRollover.Status.EXECUTED:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == AcademicYearRollover.Status.EXECUTED:
            return False
        return super().has_delete_permission(request, obj)
