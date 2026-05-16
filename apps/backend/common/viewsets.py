from rest_framework import filters, viewsets

from common.pagination import StandardResultsSetPagination
from common.permissions import BranchScopedPermission, get_user_assigned_branch_ids, user_has_global_branch_access


class ScopedQuerySetMixin:
    filterset_fields: tuple[str, ...] = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request
        organization_id = request.query_params.get("organization")
        branch_id = request.query_params.get("branch")
        academic_year_id = request.query_params.get("academic_year")
        status = request.query_params.get("status")

        if organization_id and hasattr(queryset.model, "organization_id"):
            queryset = queryset.filter(organization_id=organization_id)
        if branch_id and hasattr(queryset.model, "branch_id"):
            queryset = queryset.filter(branch_id=branch_id)
        if academic_year_id and hasattr(queryset.model, "academic_year_id"):
            queryset = queryset.filter(academic_year_id=academic_year_id)
        if status and hasattr(queryset.model, "status"):
            queryset = queryset.filter(status=status)

        user = request.user
        if user.is_authenticated and hasattr(queryset.model, "branch_id") and not user_has_global_branch_access(user):
            assigned_branch_ids = get_user_assigned_branch_ids(user)
            if assigned_branch_ids:
                queryset = queryset.filter(branch_id__in=assigned_branch_ids)
            else:
                queryset = queryset.none()
        return queryset


class BaseModelViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    permission_classes = [BranchScopedPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering = ["-created_at"]


class BaseReadOnlyModelViewSet(ScopedQuerySetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [BranchScopedPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering = ["-created_at"]
