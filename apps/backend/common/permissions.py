from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated

from accounts.models import Role


def user_has_role(user, *role_codes: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    return user.role_assignments.filter(role__code__in=role_codes, is_active=True, role__is_active=True).exists()


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
    "BranchScopedPermission",
]
