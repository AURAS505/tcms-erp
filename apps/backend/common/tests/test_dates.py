from datetime import date

import pytest

from common.dates import NepaliDate, ad_to_bs, bs_to_ad, format_bs_date, parse_bs_date


def test_nepali_date_formats_as_iso_like_bs_date():
    assert NepaliDate(2081, 1, 5).isoformat() == "2081-01-05"


def test_parse_bs_date_returns_nepali_date():
    assert parse_bs_date("2081-12-30") == NepaliDate(2081, 12, 30)


def test_format_bs_date_uses_standard_string_format():
    assert format_bs_date(NepaliDate(2081, 4, 1)) == "2081-04-01"


def test_invalid_bs_date_shape_raises_value_error():
    with pytest.raises(ValueError):
        parse_bs_date("2081/01/01")


def test_conversion_placeholders_require_approved_calendar_source():
    with pytest.raises(NotImplementedError):
        bs_to_ad(NepaliDate(2081, 1, 1))
    with pytest.raises(NotImplementedError):
        ad_to_bs(date(2024, 4, 13))
