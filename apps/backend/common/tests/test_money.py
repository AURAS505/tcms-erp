from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from common.money import add_money, quantize_money, to_decimal, validate_money_amount


def test_quantize_money_uses_two_decimal_places():
    assert quantize_money("10.125") == Decimal("10.13")


def test_money_rejects_float_input():
    with pytest.raises(TypeError):
        to_decimal(10.5)


def test_validate_money_rejects_negative_by_default():
    with pytest.raises(ValidationError):
        validate_money_amount("-1.00")


def test_add_money_returns_decimal_safe_total():
    assert add_money("10.10", Decimal("2.20"), "-0.30") == Decimal("12.00")
