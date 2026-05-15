from datetime import date

import pytest
from django.core.exceptions import ValidationError

from academic.models import AcademicPeriod, AcademicYear, AcademicYearRollover
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
def test_executed_rollover_cannot_be_edited_or_deleted(organization, academic_year):
    rollover = AcademicYearRollover.objects.create(
        organization=organization,
        from_academic_year=academic_year,
        status=AcademicYearRollover.Status.EXECUTED,
    )
    rollover.notes = "changed"
    with pytest.raises(ValidationError):
        rollover.save()
    with pytest.raises(ValidationError):
        rollover.delete()


@pytest.mark.django_db
def test_hard_closed_academic_year_cannot_be_modified_normally(academic_year):
    academic_year.status = AcademicYear.Status.HARD_CLOSED
    academic_year._allow_hard_closed_update = True
    academic_year.save(update_fields=["status", "updated_at"])
    del academic_year._allow_hard_closed_update

    academic_year.notes = "changed"
    with pytest.raises(ValidationError):
        academic_year.save()


@pytest.mark.django_db
def test_hard_closed_period_cannot_be_modified_normally(organization, academic_year):
    period = AcademicPeriod.objects.create(
        organization=organization,
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
        status=AcademicPeriod.Status.HARD_CLOSED,
    )

    period.name = "Changed"
    with pytest.raises(ValidationError):
        period.save()
