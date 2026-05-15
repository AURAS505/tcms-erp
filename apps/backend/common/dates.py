from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class NepaliDate:
    year: int
    month: int
    day: int

    def __post_init__(self) -> None:
        if self.year < 1900:
            raise ValueError("Nepali date year is outside the supported placeholder range.")
        if not 1 <= self.month <= 12:
            raise ValueError("Nepali date month must be between 1 and 12.")
        if not 1 <= self.day <= 32:
            raise ValueError("Nepali date day must be between 1 and 32.")

    def isoformat(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"


def parse_bs_date(value: str) -> NepaliDate:
    try:
        year, month, day = (int(part) for part in value.split("-", 2))
    except ValueError as exc:
        raise ValueError("Nepali date must use YYYY-MM-DD format.") from exc
    return NepaliDate(year=year, month=month, day=day)


def format_bs_date(value: NepaliDate) -> str:
    return value.isoformat()


def bs_to_ad(_value: NepaliDate) -> date:
    raise NotImplementedError("BS to AD conversion requires an approved Nepali calendar source.")


def ad_to_bs(_value: date) -> NepaliDate:
    raise NotImplementedError("AD to BS conversion requires an approved Nepali calendar source.")
