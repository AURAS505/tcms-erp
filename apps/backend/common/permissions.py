from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated

from accounts.models import Role


def user_has_role(user, role_code_or_name: str) -> bool:
    return user_has_any_role(user, [role_code_or_name])


def user_has_any_role(user, role_codes_or_names) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    values = [str(value) for value in role_codes_or_names if value]
    return user.role_assignments.filter(
        Q(role__code__in=values) | Q(role__name__in=values),
        is_active=True,
        role__is_active=True,
    ).exists()


def user_has_permission_code(user, permission_code: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    return user.role_assignments.filter(
        is_active=True,
        role__is_active=True,
        role__permission_assignments__is_active=True,
        role__permission_assignments__permission__code=permission_code,
        role__permission_assignments__permission__is_active=True,
    ).exists()


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser) or user_has_role(
            request.user, Role.RoleCode.SUPER_ADMIN
        )


class IsInstituteOwner(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, Role.RoleCode.INSTITUTE_OWNER)


class IsBranchAdmin(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, Role.RoleCode.BRANCH_ADMIN)


class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, Role.RoleCode.ACCOUNTANT)


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, Role.RoleCode.RECEPTIONIST)


class IsAuditorReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return False
        return user_has_role(request.user, Role.RoleCode.AUDITOR)


class IsReadOnlyAuditor(IsAuditorReadOnly):
    pass


class IsPaymentDraftCreator(BasePermission):
    allowed_roles = (
        Role.RoleCode.SUPER_ADMIN,
        Role.RoleCode.INSTITUTE_OWNER,
        Role.RoleCode.BRANCH_ADMIN,
        Role.RoleCode.ACCOUNTANT,
        Role.RoleCode.RECEPTIONIST,
    )

    def has_permission(self, request, view):
        return user_has_any_role(request.user, self.allowed_roles) or user_has_permission_code(
            request.user,
            "billing.student_payment.create_draft",
        )


class IsFinancialApprover(BasePermission):
    allowed_roles = (
        Role.RoleCode.SUPER_ADMIN,
        Role.RoleCode.INSTITUTE_OWNER,
        Role.RoleCode.ACCOUNTANT,
    )
    allowed_permission_codes = (
        "billing.student_payment.approve",
        "billing.student_payment.post",
    )

    def has_permission(self, request, view):
        return user_has_any_role(request.user, self.allowed_roles) or any(
            user_has_permission_code(request.user, permission_code) for permission_code in self.allowed_permission_codes
        )


class BranchScopedPermission(BasePermission):
    """
    Placeholder for branch isolation. It enforces authenticated access now and
    allows superusers globally. Branch assignment object checks can tighten this
    once auth/session workflows are implemented.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if getattr(user, "is_superuser", False):
            return True
        branch_id = getattr(obj, "branch_id", None)
        organization_id = getattr(obj, "organization_id", None)
        if branch_id is None:
            return True
        return user.branch_assignments.filter(
            branch_id=branch_id,
            organization_id=organization_id,
            is_active=True,
        ).exists()


__all__ = [
    "IsAuthenticated",
    "IsSuperAdmin",
    "IsInstituteOwner",
    "IsBranchAdmin",
    "IsAccountant",
    "IsReceptionist",
    "IsAuditorReadOnly",
    "IsReadOnlyAuditor",
    "IsPaymentDraftCreator",
    "IsFinancialApprover",
    "BranchScopedPermission",
    "user_has_role",
    "user_has_any_role",
    "user_has_permission_code",
]
