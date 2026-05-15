from datetime import date, time
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from academic.models import AcademicYear
from classes.models import (
    ClassEnrollment,
    ClassEnrollmentBreak,
    ClassEnrollmentDiscount,
    ClassRoom,
    ClassSchedule,
    ClassTeacherTransfer,
    StudentWithdrawal,
    Subject,
)
from organizations.models import Branch, Organization
from students.models import Student
from teachers.models import Teacher


@pytest.fixture
def organization():
    return Organization.objects.create(legal_name="Auras Education Pvt. Ltd.", display_name="Auras Education")


@pytest.fixture
def branch(organization):
    return Branch.objects.create(organization=organization, code="MAIN", name="Main Branch", is_main_branch=True)


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


@pytest.fixture
def user():
    return get_user_model().objects.create_user(email="branch-admin@example.com", password="secure-password")


@pytest.fixture
def teacher(organization, branch):
    return Teacher.objects.create(
        organization=organization,
        branch=branch,
        employee_number="TCH-001",
        full_name="Anita Shrestha",
        phone="9800000001",
        status=Teacher.Status.ACTIVE,
    )


@pytest.fixture
def student(organization, branch, academic_year):
    return Student.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        admission_number="ADM-001",
        full_name="Sita Sharma",
        permanent_address="Kathmandu",
        status=Student.Status.ACTIVE,
    )


@pytest.fixture
def subject(organization, branch, academic_year):
    return Subject.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        subject_code="MATH",
        subject_name="Mathematics",
        description="Core mathematics subject.",
    )


@pytest.fixture
def class_room(organization, branch, academic_year, teacher, subject):
    room = ClassRoom.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        class_name="Grade 10 Mathematics",
        batch_name="Morning",
        section_name="A",
        primary_teacher=teacher,
        start_date_ad=date(2024, 4, 14),
        start_date_bs="2081-01-02",
        expected_end_date_ad=date(2025, 4, 12),
        expected_end_date_bs="2081-12-30",
        capacity=30,
        monthly_fee=Decimal("2500.00"),
        teacher_cut_percentage=Decimal("40.0000"),
        teacher_payment_type=ClassRoom.TeacherPaymentType.MONTHLY_CUT_PERCENTAGE,
        payment_due_rule=ClassRoom.PaymentDueRule.FIXED_BS_DAY,
        due_day=5,
        status=ClassRoom.Status.ACTIVE,
    )
    room.subjects.add(subject)
    return room


@pytest.fixture
def enrollment(organization, branch, academic_year, student, class_room):
    return ClassEnrollment.objects.create(
        organization=organization,
        branch=branch,
        academic_year=academic_year,
        student=student,
        class_room=class_room,
        joined_date_ad=date(2024, 5, 1),
        joined_date_bs="2081-01-19",
        status=ClassEnrollment.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_create_subject(subject):
    assert str(subject) == "MATH - Mathematics"
    assert subject.is_active is True


@pytest.mark.django_db
def test_enforce_unique_subject_code_per_organization(subject, organization):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Subject.objects.create(
                organization=organization,
                subject_code="MATH",
                subject_name="Duplicate Mathematics",
            )


@pytest.mark.django_db
def test_create_class_room(class_room, subject):
    assert str(class_room) == "Grade 10 Mathematics - Morning - A"
    assert class_room.subjects.get() == subject
    assert class_room.status == ClassRoom.Status.ACTIVE


@pytest.mark.django_db
def test_enforce_class_uniqueness_per_scope(class_room, organization, branch, academic_year):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ClassRoom.objects.create(
                organization=organization,
                branch=branch,
                academic_year=academic_year,
                class_name="Grade 10 Mathematics",
                batch_name="Morning",
                section_name="A",
            )


@pytest.mark.django_db
def test_create_class_schedule(class_room):
    schedule = ClassSchedule.objects.create(
        class_room=class_room,
        day_of_week=ClassSchedule.DayOfWeek.SUNDAY,
        start_time=time(7, 0),
        end_time=time(8, 30),
        room_name="Room 101",
    )

    assert "Sunday" in str(schedule)
    assert schedule.is_active is True


@pytest.mark.django_db
def test_create_class_enrollment(enrollment):
    assert str(enrollment) == "ADM-001 -> Grade 10 Mathematics - Morning - A"
    assert enrollment.status == ClassEnrollment.Status.ACTIVE


@pytest.mark.django_db
def test_prevent_duplicate_active_enrollment(enrollment, organization, branch, academic_year, student, class_room):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ClassEnrollment.objects.create(
                organization=organization,
                branch=branch,
                academic_year=academic_year,
                student=student,
                class_room=class_room,
                joined_date_ad=date(2024, 5, 2),
                status=ClassEnrollment.Status.ACTIVE,
            )


@pytest.mark.django_db
def test_create_enrollment_break(enrollment, user):
    break_record = ClassEnrollmentBreak.objects.create(
        enrollment=enrollment,
        break_start_date_ad=date(2024, 8, 1),
        break_start_date_bs="2081-04-17",
        expected_return_date_ad=date(2024, 8, 15),
        expected_return_date_bs="2081-04-31",
        reason="Medical leave.",
        status=ClassEnrollmentBreak.Status.APPROVED,
        approved_by=user,
    )

    assert "break from" in str(break_record)
    assert break_record.approved_by == user


@pytest.mark.django_db
def test_create_enrollment_discount(enrollment, user):
    discount = ClassEnrollmentDiscount.objects.create(
        enrollment=enrollment,
        discount_type=ClassEnrollmentDiscount.DiscountType.SCHOLARSHIP,
        discount_percentage=Decimal("10.0000"),
        effective_from_ad=date(2024, 5, 1),
        reason="Scholarship approved by management.",
        status=ClassEnrollmentDiscount.Status.APPROVED,
        approved_by=user,
    )

    assert str(discount) == "ADM-001 -> Grade 10 Mathematics - Morning - A - Scholarship"
    assert discount.approved_by == user


@pytest.mark.django_db
def test_create_student_withdrawal(enrollment, user):
    withdrawal = StudentWithdrawal.objects.create(
        enrollment=enrollment,
        student=enrollment.student,
        organization=enrollment.organization,
        branch=enrollment.branch,
        academic_year=enrollment.academic_year,
        last_attendance_date_ad=date(2024, 9, 1),
        last_attendance_date_bs="2081-05-16",
        reason="Student moved to another city.",
        status=StudentWithdrawal.Status.PENDING_REVIEW,
        reviewed_by=user,
    )

    assert str(withdrawal) == "ADM-001 withdrawal from Grade 10 Mathematics - Morning - A"
    assert withdrawal.reviewed_by == user


@pytest.mark.django_db
def test_create_teacher_transfer(class_room, organization, branch, user):
    new_teacher = Teacher.objects.create(
        organization=organization,
        branch=branch,
        employee_number="TCH-002",
        full_name="Bikash Karki",
        phone="9800000002",
        status=Teacher.Status.ACTIVE,
    )

    transfer = ClassTeacherTransfer.objects.create(
        class_room=class_room,
        from_teacher=class_room.primary_teacher,
        to_teacher=new_teacher,
        effective_date_ad=date(2024, 6, 1),
        effective_date_bs="2081-02-19",
        reason="Teacher schedule adjustment.",
        status=ClassTeacherTransfer.Status.APPROVED,
        approved_by=user,
    )

    assert str(transfer) == "Grade 10 Mathematics - Morning - A teacher transfer to TCH-002"
    assert transfer.approved_by == user


@pytest.mark.django_db
def test_branch_organization_academic_year_relationships(enrollment, class_room):
    assert enrollment.organization == class_room.organization
    assert enrollment.branch == class_room.branch
    assert enrollment.academic_year == class_room.academic_year
    assert enrollment.student.branch == class_room.branch
