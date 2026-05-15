from rest_framework import serializers

from .models import ApprovalRule, Branch, Organization, OrganizationSetting, TaxRate


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class OrganizationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSetting
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ApprovalRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRule
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
