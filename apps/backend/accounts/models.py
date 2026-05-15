import hashlib
import secrets
import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils import timezone

from common.models import BaseModel, TimestampedModel, UUIDModel

from .managers import UserManager


class User(UUIDModel, TimestampedModel, AbstractBaseUser):
    class UserStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"
        INVITED = "invited", "Invited"

    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=UserStatus.choices, default=UserStatus.ACTIVE, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    force_password_change = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["email"]
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def has_perm(self, perm, obj=None) -> bool:
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label) -> bool:
        return self.is_active and self.is_staff


class Role(BaseModel):
    class RoleCode(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        INSTITUTE_OWNER = "institute_owner", "Institute Owner"
        BRANCH_ADMIN = "branch_admin", "Branch Admin"
        ACCOUNTANT = "accountant", "Accountant"
        RECEPTIONIST = "receptionist", "Receptionist"
        TEACHER = "teacher", "Teacher"
        AUDITOR = "auditor", "Auditor"
        STUDENT_PORTAL_USER = "student_portal_user", "Future Student Portal User"
        PARENT_PORTAL_USER = "parent_portal_user", "Future Parent Portal User"

    code = models.CharField(max_length=64, choices=RoleCode.choices, unique=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)
    is_read_only = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Permission(BaseModel):
    code = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    is_read_only = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["module", "code"]
        indexes = [models.Index(fields=["module", "is_active"])]

    def __str__(self) -> str:
        return self.code


class UserRole(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_assignments")
    assigned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_user_roles",
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["user__email", "role__name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "role"], condition=models.Q(is_active=True), name="unique_active_user_role"),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.role}"


class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permission_assignments")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_assignments")
    assigned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_role_permissions",
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["role__name", "permission__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                condition=models.Q(is_active=True),
                name="unique_active_role_permission",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.role} -> {self.permission}"


class UserBranchAssignment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="branch_assignments")
    organization_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    branch_id = models.UUIDField(db_index=True)
    assigned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_branch_users",
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["user__email", "branch_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "branch_id"],
                condition=models.Q(is_active=True),
                name="unique_active_user_branch_assignment",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.branch_id}"


class PasswordResetToken(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token_hash = models.CharField(max_length=128, unique=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    requested_ip = models.GenericIPAddressField(null=True, blank=True)
    requested_user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Password reset token for {self.user}"

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def create_for_user(cls, user: User, *, expires_at, **extra_fields):
        raw_token = secrets.token_urlsafe(32)
        token = cls.objects.create(
            user=user,
            token_hash=cls.hash_token(raw_token),
            expires_at=expires_at,
            **extra_fields,
        )
        return raw_token, token

    def matches(self, raw_token: str) -> bool:
        return secrets.compare_digest(self.token_hash, self.hash_token(raw_token))

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at


class LoginSession(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_sessions")
    session_key_hash = models.CharField(max_length=128, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_from = models.CharField(max_length=50, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Login session for {self.user}"

    @staticmethod
    def hash_session_key(raw_session_key: str) -> str:
        return hashlib.sha256(raw_session_key.encode("utf-8")).hexdigest()

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None
