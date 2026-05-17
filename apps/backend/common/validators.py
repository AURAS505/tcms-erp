from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

from django.conf import settings
from django.core.exceptions import ValidationError

DEFAULT_ALLOWED_UPLOAD_EXTENSIONS = ("pdf", "jpg", "jpeg", "png", "doc", "docx")
DEFAULT_MAX_UPLOAD_SIZE_BYTES = 2 * 1024 * 1024


def validate_uuid(value) -> UUID:
    try:
        return value if isinstance(value, UUID) else UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise ValidationError("Enter a valid UUID.") from exc


def validate_non_negative_decimal(value) -> Decimal:
    amount = Decimal(str(value))
    if amount < Decimal("0"):
        raise ValidationError("Value cannot be negative.")
    return amount


def require_one_of(**values):
    populated = [name for name, value in values.items() if value not in (None, "")]
    if len(populated) != 1:
        field_names = ", ".join(values.keys())
        raise ValidationError(f"Exactly one of these fields is required: {field_names}.")
    return populated[0]


def require_at_least_one_of(**values):
    populated = [name for name, value in values.items() if value not in (None, "")]
    if not populated:
        field_names = ", ".join(values.keys())
        raise ValidationError(f"At least one of these fields is required: {field_names}.")
    return populated


def get_allowed_upload_extensions() -> set[str]:
    configured_extensions = getattr(settings, "ALLOWED_UPLOAD_EXTENSIONS", DEFAULT_ALLOWED_UPLOAD_EXTENSIONS)
    return {str(extension).lower().lstrip(".") for extension in configured_extensions if str(extension).strip()}


def get_max_upload_size_bytes() -> int:
    return int(getattr(settings, "MAX_UPLOAD_SIZE_BYTES", DEFAULT_MAX_UPLOAD_SIZE_BYTES))


def normalize_upload_extension(filename: str) -> str:
    extension = Path(filename or "").suffix.lower().lstrip(".")
    if not extension:
        raise ValidationError("Uploaded file must have an extension.")
    return extension


def validate_upload_extension(filename: str, allowed_extensions=None) -> str:
    extension = normalize_upload_extension(filename)
    allowed = {
        str(allowed_extension).lower().lstrip(".")
        for allowed_extension in (allowed_extensions or get_allowed_upload_extensions())
        if str(allowed_extension).strip()
    }
    if extension not in allowed:
        allowed_display = ", ".join(sorted(allowed))
        raise ValidationError(f"Unsupported file extension '.{extension}'. Allowed extensions: {allowed_display}.")
    return extension


def validate_upload_size(file_obj, max_size: int | None = None) -> int:
    size = getattr(file_obj, "size", None)
    if size is None:
        raise ValidationError("Unable to determine uploaded file size.")

    max_allowed_size = max_size if max_size is not None else get_max_upload_size_bytes()
    if int(size) > int(max_allowed_size):
        raise ValidationError(f"Uploaded file is too large. Maximum allowed size is {max_allowed_size} bytes.")
    return int(size)


def validate_uploaded_document(
    file_obj,
    *,
    filename: str | None = None,
    allowed_extensions=None,
    max_size: int | None = None,
) -> None:
    upload_name = filename or getattr(file_obj, "name", "")
    validate_upload_extension(upload_name, allowed_extensions=allowed_extensions)
    validate_upload_size(file_obj, max_size=max_size)


def secure_upload_path(module: str, document_type: str, original_filename: str) -> str:
    extension = validate_upload_extension(original_filename)
    module_component = _safe_path_component(module)
    document_component = _safe_path_component(document_type)
    return f"private/{module_component}/{document_component}/{uuid4().hex}.{extension}"


def _safe_path_component(value: str) -> str:
    component = "".join(character.lower() if character.isalnum() else "-" for character in str(value or "misc")).strip("-")
    return component or "misc"
