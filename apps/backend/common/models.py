import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ActiveQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)


class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().alive()


class AllObjectsManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    pass


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserAuditModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_%(class)s_records",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_%(class)s_records",
    )

    class Meta:
        abstract = True


class ActiveStatusModel(models.Model):
    is_active = models.BooleanField(default=True, db_index=True)

    objects = ActiveQuerySet.as_manager()

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])


class BaseModel(UUIDModel, TimestampedModel):
    class Meta:
        abstract = True


class AuditedBaseModel(BaseModel, UserAuditModel):
    class Meta:
        abstract = True


class SoftDeleteBaseModel(AuditedBaseModel, SoftDeleteModel):
    class Meta:
        abstract = True


class AuditLog(UUIDModel):
    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        POST = "post", "Post"
        REVERSE = "reverse", "Reverse"
        VOID = "void", "Void"
        APPROVE = "approve", "Approve"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        EXPORT = "export", "Export"
        SYSTEM = "system", "System"

    class Module(models.TextChoices):
        ACCOUNTS = "accounts", "Accounts"
        ORGANIZATIONS = "organizations", "Organizations"
        ACADEMIC = "academic", "Academic"
        ACCOUNTING = "accounting", "Accounting"
        BILLING = "billing", "Billing"
        PAYROLL = "payroll", "Payroll"
        STUDENTS = "students", "Students"
        TEACHERS = "teachers", "Teachers"
        CLASSES = "classes", "Classes"
        SYSTEM = "system", "System"

    organization = models.ForeignKey(
        "organizations.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    branch = models.ForeignKey(
        "organizations.Branch",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=Action.choices, db_index=True)
    module = models.CharField(max_length=50, choices=Module.choices, db_index=True)
    object_type = models.CharField(max_length=150, db_index=True)
    object_id = models.CharField(max_length=64, blank=True, db_index=True)
    object_repr = models.CharField(max_length=255, blank=True)
    before_data = models.JSONField(null=True, blank=True)
    after_data = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    reason = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "module", "action"]),
            models.Index(fields=["branch", "module", "action"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["object_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.module}.{self.action} {self.object_repr or self.object_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding and not getattr(self, "_allow_audit_log_mutation", False):
            raise ValidationError("Audit logs are append-only and cannot be edited.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not getattr(self, "_allow_audit_log_deletion", False):
            raise ValidationError("Audit logs are append-only and cannot be deleted.")
        return super().delete(*args, **kwargs)
