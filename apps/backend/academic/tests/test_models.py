from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from academic.models import AcademicPeriod, AcademicYear, AcademicYearRollover, NepaliCalendarDay
from organizations.models import Organization


@pytest.fixture
def organization():
    return Organization.objects.create(legal_name="Auras Education Pvt. Ltd.", display_name="Auras Education")


@pytest.fixture
def academic_year(organization):
    return AcademicYear.objects.create(
        organization=organization,
        name="2081/2082",
        bs_start_year=2081,
        bs_end_year=2082,
        bs_start_date="2081-01-01",
        bs_end_date="2081-12-30",
        ad_start_date=date(2024, 4, 13),
        ad_end_date=date(2025, 4, 13),
        status=AcademicYear.Status.ACTIVE,
        is_active=True,
    )


@pytest.mark.django_db
def test_create_academic_year(organization):
    year = AcademicYear.objects.create(
        organization=organization,
        name="2081/2082",
        bs_start_year=2081,
        bs_end_year=2082,
        bs_start_date="2081-01-01",
        bs_end_date="2081-12-30",
        ad_start_date=date(2024, 4, 13),
        ad_end_date=date(2025, 4, 13),
    )

    assert str(year) == "Auras Education - 2081/2082"
    assert year.status == AcademicYear.Status.DRAFT
    assert year.is_active is False


@pytest.mark.django_db
def test_enforce_one_active_academic_year_per_organization(organization, academic_year):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            AcademicYear.objects.create(
                organization=organization,
                name="2082/2083",
                bs_start_year=2082,
                bs_end_year=2083,
                bs_start_date="2082-01-01",
                bs_end_date="2082-12-30",
                ad_start_date=date(2025, 4, 14),
                ad_end_date=date(2026, 4, 13),
                status=AcademicYear.Status.ACTIVE,
                is_active=True,
            )


@pytest.mark.django_db
def test_allow_different_organizations_to_each_have_active_year(academic_year):
    other = Organization.objects.create(legal_name="Other Institute Pvt. Ltd.", display_name="Other Institute")
    year = AcademicYear.objects.create(
        organization=other,
        name="2081/2082",
        bs_start_year=2081,
        bs_end_year=2082,
        bs_start_date="2081-01-01",
        bs_end_date="2081-12-30",
        ad_start_date=date(2024, 4, 13),
        ad_end_date=date(2025, 4, 13),
        status=AcademicYear.Status.ACTIVE,
        is_active=True,
    )

    assert year.organization == other


@pytest.mark.django_db
def test_create_academic_period(academic_year):
    period = AcademicPeriod.objects.create(
        organization=academic_year.organization,
        academic_year=academic_year,
        name="Shrawan 2081",
        period_order=1,
        bs_month=4,
        bs_month_name="Shrawan",
        bs_year=2081,
        bs_start_date="2081-04-01",
        bs_end_date="2081-04-31",
        ad_start_date=date(2024, 7, 16),
        ad_end_date=date(2024, 8, 15),
    )

    assert str(period) == "2081/2082 - Shrawan 2081"
    assert period.status == AcademicPeriod.Status.OPEN
    assert period.is_active is True


@pytest.mark.django_db
def test_enforce_unique_period_order_per_academic_year(academic_year):
    AcademicPeriod.objects.create(
        organization=academic_year.organization,
        academic_year=academic_year,
        name="Shrawan 2081",
        period_order=1,
        bs_month=4,
        bs_month_name="Shrawan",
        bs_year=2081,
        bs_start_date="2081-04-01",
        bs_end_date="2081-04-31",
        ad_start_date=date(2024, 7, 16),
        ad_end_date=date(2024, 8, 15),
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            AcademicPeriod.objects.create(
                organization=academic_year.organization,
                academic_year=academic_year,
                name="Bhadra 2081",
                period_order=1,
                bs_month=5,
                bs_month_name="Bhadra",
                bs_year=2081,
                bs_start_date="2081-05-01",
                bs_end_date="2081-05-31",
                ad_start_date=date(2024, 8, 16),
                ad_end_date=date(2024, 9, 15),
            )


@pytest.mark.django_db
def test_period_clean_requires_dates_inside_academic_year(academic_year):
    period = AcademicPeriod(
        organization=academic_year.organization,
        academic_year=academic_year,
        name="Outside",
        period_order=99,
        bs_month=1,
        bs_month_name="Baishakh",
        bs_year=2083,
        bs_start_date="2083-01-01",
        bs_end_date="2083-01-31",
        ad_start_date=date(2026, 4, 14),
        ad_end_date=date(2026, 5, 14),
    )

    with pytest.raises(ValidationError):
        period.full_clean()


@pytest.mark.django_db
def test_create_nepali_calendar_day():
    calendar_day = NepaliCalendarDay.objects.create(
        bs_date="2081-04-01",
        bs_year=2081,
        bs_month=4,
        bs_day=1,
        ad_date=date(2024, 7, 16),
        bs_month_name="Shrawan",
        is_month_start=True,
    )

    assert str(calendar_day) == "2081-04-01 / 2024-07-16"
    assert calendar_day.is_month_start is True
    assert calendar_day.is_month_end is False


@pytest.mark.django_db
def test_unique_bs_date_in_nepali_calendar_day():
    NepaliCalendarDay.objects.create(
        bs_date="2081-04-01",
        bs_year=2081,
        bs_month=4,
        bs_day=1,
        ad_date=date(2024, 7, 16),
        bs_month_name="Shrawan",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            NepaliCalendarDay.objects.create(
                bs_date="2081-04-01",
                bs_year=2081,
                bs_month=4,
                bs_day=1,
                ad_date=date(2024, 7, 17),
                bs_month_name="Shrawan",
            )


@pytest.mark.django_db
def test_create_academic_year_rollover_placeholder(academic_year):
    rollover = AcademicYearRollover.objects.create(
        organization=academic_year.organization,
        from_academic_year=academic_year,
        notes="Prepared for future rollover validation.",
    )

    assert str(rollover) == "Auras Education: rollover from 2081/2082"
    assert rollover.status == AcademicYearRollover.Status.DRAFT
    assert rollover.trial_balance_validated is False
    assert rollover.revenue_expense_closing_completed is False
    assert rollover.opening_balances_posted is False


@pytest.mark.django_db
def test_rollover_clean_requires_years_from_same_organization(academic_year):
    other = Organization.objects.create(legal_name="Other Institute Pvt. Ltd.", display_name="Other Institute")
    rollover = AcademicYearRollover(
        organization=other,
        from_academic_year=academic_year,
    )

    with pytest.raises(ValidationError):
        rollover.full_clean()
