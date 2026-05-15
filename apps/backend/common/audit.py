from contextvars import ContextVar
from dataclasses import dataclass


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
