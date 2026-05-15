from django.contrib import admin

from .models import Account, AccountingDocument, JournalEntry, JournalEntryLine, LedgerSnapshot


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "organization", "account_type", "normal_balance", "is_system_account", "is_active"]
    list_filter = ["organization", "account_type", "normal_balance", "is_system_account", "is_active"]
    search_fields = ["code", "name", "organization__display_name", "description"]


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 0
    fields = ["account", "description", "debit_amount", "credit_amount", "branch"]


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ["entry_number", "organization", "branch", "academic_year", "entry_date_ad", "status", "is_system_generated"]
    list_filter = ["organization", "branch", "academic_year", "academic_period", "status", "source_type", "is_system_generated"]
    search_fields = ["entry_number", "description", "narration", "source_number"]
    inlines = [JournalEntryLineInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_immutable:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_immutable:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(JournalEntryLine)
class JournalEntryLineAdmin(admin.ModelAdmin):
    list_display = ["journal_entry", "account", "debit_amount", "credit_amount", "branch"]
    list_filter = ["organization", "branch", "account__account_type"]
    search_fields = ["journal_entry__entry_number", "account__code", "account__name", "description"]


@admin.register(AccountingDocument)
class AccountingDocumentAdmin(admin.ModelAdmin):
    list_display = ["document_type", "reference_number", "organization", "journal_entry", "uploaded_by", "created_at"]
    list_filter = ["organization", "document_type"]
    search_fields = ["reference_number", "description", "journal_entry__entry_number"]


@admin.register(LedgerSnapshot)
class LedgerSnapshotAdmin(admin.ModelAdmin):
    list_display = ["organization", "account", "academic_year", "academic_period", "balance", "snapshot_at"]
    list_filter = ["organization", "academic_year", "academic_period"]
    search_fields = ["account__code", "account__name", "organization__display_name"]
