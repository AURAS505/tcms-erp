from rest_framework import serializers

from .models import (
    Student,
    StudentAcademicRecord,
    StudentDocument,
    StudentInquiry,
    StudentNote,
    StudentSchoolHistory,
    StudentStatusHistory,
)


class StudentInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInquiry
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentAcademicRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAcademicRecord
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentSchoolHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSchoolHistory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentStatusHistory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNote
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
