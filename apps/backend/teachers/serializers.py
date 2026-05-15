from rest_framework import serializers

from .models import Teacher, TeacherActivity, TeacherContract, TeacherStatusHistory


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TeacherContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherContract
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TeacherActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherActivity
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TeacherStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherStatusHistory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
