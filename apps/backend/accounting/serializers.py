from rest_framework import serializers

from academic.models import AcademicPeriod, AcademicYear
from organizations.models import Branch, Organization

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


class ManualJournalLineSerializer(serializers.Serializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.filter(is_active=True))
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)
    debit_amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0, required=False, default=0)
    credit_amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0, required=False, default=0)

    def validate(self, attrs):
        debit = attrs.get("debit_amount") or 0
        credit = attrs.get("credit_amount") or 0
        if debit and credit:
            raise serializers.ValidationError("A journal line cannot have both debit and credit.")
        if not debit and not credit:
            raise serializers.ValidationError("A journal line must have either debit or credit.")
        return attrs


class ManualJournalCreateSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    academic_period = serializers.PrimaryKeyRelatedField(
        queryset=AcademicPeriod.objects.all(),
        required=False,
        allow_null=True,
    )
    entry_date_ad = serializers.DateField()
    entry_date_bs = serializers.CharField(required=False, allow_blank=True, max_length=10)
    description = serializers.CharField(max_length=255)
    narration = serializers.CharField(required=False, allow_blank=True)
    lines = ManualJournalLineSerializer(many=True)


class EmptyAccountingActionSerializer(serializers.Serializer):
    pass


class JournalReverseSerializer(serializers.Serializer):
    reversal_date_ad = serializers.DateField(required=False)
    narration = serializers.CharField(required=False, allow_blank=True)


class AccountingDocumentCreateSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=AccountingDocument.DocumentType.choices)
    reference_number = serializers.CharField(required=False, allow_blank=True, max_length=100)
    file_path = serializers.CharField(required=False, allow_blank=True, max_length=500)
    description = serializers.CharField(required=False, allow_blank=True)


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
