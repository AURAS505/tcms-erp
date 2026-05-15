from rest_framework import serializers

from .models import Family, Guardian, StudentGuardian


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentGuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGuardian
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
