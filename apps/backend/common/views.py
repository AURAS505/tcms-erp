from common.viewsets import BaseReadOnlyModelViewSet

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(BaseReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("organization", "branch", "user").all()
    serializer_class = AuditLogSerializer
    search_fields = ("module", "action", "object_type", "object_id", "object_repr", "reason")
    ordering_fields = ("created_at", "module", "action")
