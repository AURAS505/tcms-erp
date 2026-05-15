from rest_framework import serializers

from .models import Account, AccountingDocument, JournalEntry, JournalEntryLine, LedgerSnapshot


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class JournalEntryLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntryLine
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AccountingDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingDocument
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class LedgerSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerSnapshot
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
