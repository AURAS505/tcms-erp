from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models

MONEY_MAX_DIGITS = 18
MONEY_DECIMAL_PLACES = 2
MONEY_QUANTIZER = Decimal("0.01")
ZERO_MONEY = Decimal("0.00")


def to_decimal(value) -> Decimal:
    if isinstance(value, float):
        raise TypeError("Money values must not be created from float.")

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError("Enter a valid money amount.") from exc


def quantize_money(value) -> Decimal:
    return to_decimal(value).quantize(MONEY_QUANTIZER, rounding=ROUND_HALF_UP)


def validate_money_amount(value, *, allow_negative: bool = False) -> Decimal:
    amount = quantize_money(value)
    if not allow_negative and amount < ZERO_MONEY:
        raise ValidationError("Money amount cannot be negative.")
    return amount


def add_money(*values) -> Decimal:
    total = ZERO_MONEY
    for value in values:
        total += validate_money_amount(value, allow_negative=True)
    return quantize_money(total)


def money_field(*, default=ZERO_MONEY, **kwargs) -> models.DecimalField:
    return models.DecimalField(
        max_digits=kwargs.pop("max_digits", MONEY_MAX_DIGITS),
        decimal_places=kwargs.pop("decimal_places", MONEY_DECIMAL_PLACES),
        default=default,
        **kwargs,
    )
