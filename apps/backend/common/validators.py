from decimal import Decimal
from uuid import UUID

from django.core.exceptions import ValidationError


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
