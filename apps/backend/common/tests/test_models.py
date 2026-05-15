import uuid

import pytest
from django.db import connection, models
from django.utils import timezone

from common.models import ActiveStatusModel, SoftDeleteBaseModel

pytestmark = pytest.mark.django_db(transaction=True)


class CommonUtilityTestModel(SoftDeleteBaseModel, ActiveStatusModel):
    name = models.CharField(max_length=64)

    class Meta:
        app_label = "common"
        db_table = "common_utility_test_model"
        managed = False


@pytest.fixture
def common_utility_table():
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(CommonUtilityTestModel)
    try:
        yield
    finally:
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CommonUtilityTestModel)


def test_uuid_primary_key_is_created(common_utility_table):
    instance = CommonUtilityTestModel.objects.create(name="Example")

    assert isinstance(instance.id, uuid.UUID)


def test_timestamp_fields_are_created(common_utility_table):
    instance = CommonUtilityTestModel.objects.create(name="Example")

    assert instance.created_at is not None
    assert instance.updated_at is not None


def test_soft_delete_hides_record_from_default_manager(common_utility_table):
    instance = CommonUtilityTestModel.objects.create(name="Example")

    instance.delete()

    assert instance.deleted_at is not None
    assert CommonUtilityTestModel.objects.filter(id=instance.id).exists() is False
    assert CommonUtilityTestModel.all_objects.filter(id=instance.id).exists() is True


def test_restore_returns_record_to_default_manager(common_utility_table):
    instance = CommonUtilityTestModel.objects.create(name="Example", deleted_at=timezone.now())

    instance.restore()

    assert instance.deleted_at is None
    assert CommonUtilityTestModel.objects.filter(id=instance.id).exists() is True


def test_active_status_manager_filters_active_records(common_utility_table):
    active = CommonUtilityTestModel.objects.create(name="Active")
    CommonUtilityTestModel.objects.create(name="Inactive", is_active=False)

    assert list(CommonUtilityTestModel.all_objects.active()) == [active]
