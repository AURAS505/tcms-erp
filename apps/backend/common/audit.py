from contextvars import ContextVar
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.forms.models import model_to_dict

from common.models import AuditLog


@dataclass(frozen=True)
class AuditContext:
    user_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None


_audit_context: ContextVar[AuditContext | None] = ContextVar("audit_context", default=None)


def set_audit_context(context: AuditContext):
    return _audit_context.set(context)


def get_audit_context() -> AuditContext | None:
    return _audit_context.get()


def reset_audit_context(token) -> None:
    _audit_context.reset(token)


def clear_audit_context() -> None:
    _audit_context.set(None)


AuditAction = AuditLog.Action
AuditModule = AuditLog.Module


def serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    return value


def serialize_model_instance(instance, *, fields: list[str] | None = None) -> dict:
    data = model_to_dict(instance, fields=fields)
    return serialize_value(data)


class AuditLogService:
    @staticmethod
    def record(
        *,
        action,
        module,
        obj=None,
        organization=None,
        branch=None,
        user=None,
        object_type: str = "",
        object_id: str = "",
        object_repr: str = "",
        before_data=None,
        after_data=None,
        metadata=None,
        reason: str = "",
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str | None = None,
    ) -> AuditLog:
        context = get_audit_context()
        if context:
            ip_address = ip_address or context.ip_address
            user_agent = user_agent or context.user_agent
            request_id = request_id or context.request_id

        if obj is not None:
            organization = organization if organization is not None else getattr(obj, "organization", None)
            branch = branch if branch is not None else getattr(obj, "branch", None)
            object_type = object_type or f"{obj.__class__.__module__}.{obj.__class__.__name__}"
            object_id = object_id or str(getattr(obj, "pk", ""))
            object_repr = object_repr or str(obj)

        if user is None and context and context.user_id:
            user_id = context.user_id
        else:
            user_id = getattr(user, "id", None)

        return AuditLog.objects.create(
            organization=organization,
            branch=branch,
            user_id=user_id,
            action=action,
            module=module,
            object_type=object_type,
            object_id=object_id,
            object_repr=object_repr,
            before_data=serialize_value(before_data),
            after_data=serialize_value(after_data),
            metadata=serialize_value(metadata),
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent or "",
            request_id=request_id or "",
        )

    @classmethod
    def record_model_change(
        cls,
        *,
        action,
        module,
        instance,
        before_data=None,
        after_data=None,
        user=None,
        reason: str = "",
        metadata=None,
    ) -> AuditLog:
        return cls.record(
            action=action,
            module=module,
            obj=instance,
            user=user,
            before_data=before_data,
            after_data=after_data,
            metadata=metadata,
            reason=reason,
        )
