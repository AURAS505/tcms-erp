from django.contrib.auth import get_user_model, password_validation
from django.db.models import Q
from rest_framework import serializers

from .models import PasswordResetToken


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=254)
    password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate(self, attrs):
        identifier = attrs["username_or_email"].strip().lower()
        password = attrs["password"]
        user = User.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier)).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials."]})
        if not user.is_active or user.status != User.UserStatus.ACTIVE:
            raise serializers.ValidationError({"non_field_errors": ["User account is not active."]})

        attrs["user"] = user
        return attrs


class RoleSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()
    is_read_only = serializers.BooleanField()


class PermissionSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()
    module = serializers.CharField()
    is_read_only = serializers.BooleanField()


class BranchAssignmentSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    branch_id = serializers.UUIDField()
    is_primary = serializers.BooleanField()


class CurrentUserSerializer(serializers.Serializer):
    def to_representation(self, user):
        role_assignments = user.role_assignments.select_related("role").filter(is_active=True, role__is_active=True)
        roles = [assignment.role for assignment in role_assignments]

        permissions_by_code = {}
        for role in roles:
            permission_assignments = role.permission_assignments.select_related("permission").filter(
                is_active=True,
                permission__is_active=True,
            )
            for assignment in permission_assignments:
                permissions_by_code[assignment.permission.code] = assignment.permission

        branch_assignments = user.branch_assignments.filter(is_active=True)

        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "status": user.status,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "force_password_change": user.force_password_change,
            "roles": RoleSummarySerializer(roles, many=True).data,
            "permissions": PermissionSummarySerializer(permissions_by_code.values(), many=True).data,
            "branch_assignments": BranchAssignmentSummarySerializer(branch_assignments, many=True).data,
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(trim_whitespace=False)
    new_password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        token_hash = PasswordResetToken.hash_token(attrs["token"])
        reset_token = PasswordResetToken.objects.select_related("user").filter(token_hash=token_hash).first()

        if reset_token is None or reset_token.is_used or reset_token.is_expired or not reset_token.user.is_active:
            raise serializers.ValidationError({"token": ["Invalid or expired password reset token."]})

        attrs["reset_token"] = reset_token
        return attrs


class ForcePasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(trim_whitespace=False, write_only=True)
    new_password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context["request"].user)
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": ["Current password is incorrect."]})
        return attrs
