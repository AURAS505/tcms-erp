from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.utils import timezone

from accounts.models import Role
from organizations.models import ApprovalRule, Branch, Organization, OrganizationSetting, TaxRate


@pytest.fixture
def organization():
    return Organization.objects.create(
        legal_name="Auras Education Pvt. Ltd.",
        display_name="Auras Education",
        registration_number="REG-001",
        vat_pan_number="PAN-001",
        email="info@example.com",
        phone="+977-1-5555555",
        website="https://example.com",
        address="Kathmandu",
    )


@pytest.mark.django_db
def test_create_organization():
    organization = Organization.objects.create(
        legal_name="TCMS Institute Pvt. Ltd.",
        display_name="TCMS Institute",
        default_currency="NPR",
    )

    assert str(organization) == "TCMS Institute"
    assert organization.is_active is True
    assert organization.default_currency == "NPR"


@pytest.mark.django_db
def test_create_branch(organization):
    branch = Branch.objects.create(
        organization=organization,
        code="MAIN",
        name="Main Branch",
        address="Kathmandu",
        is_main_branch=True,
    )

    assert str(branch) == "Auras Education - Main Branch"
    assert branch.organization == organization
    assert branch.is_active is True


@pytest.mark.django_db
def test_unique_branch_code_per_organization(organization):
    Branch.objects.create(organization=organization, code="MAIN", name="Main Branch")

    with pytest.raises(IntegrityError):
        Branch.objects.create(organization=organization, code="MAIN", name="Duplicate Branch")


@pytest.mark.django_db
def test_same_branch_code_allowed_for_different_organizations(organization):
    other = Organization.objects.create(legal_name="Other Pvt. Ltd.", display_name="Other")
    Branch.objects.create(organization=organization, code="MAIN", name="Main Branch")
    branch = Branch.objects.create(organization=other, code="MAIN", name="Other Main Branch")

    assert branch.organization == other


@pytest.mark.django_db
def test_only_one_main_branch_per_organization(organization):
    Branch.objects.create(organization=organization, code="MAIN", name="Main Branch", is_main_branch=True)

    with pytest.raises(IntegrityError):
        Branch.objects.create(organization=organization, code="ALT", name="Alt Branch", is_main_branch=True)


@pytest.mark.django_db
def test_create_organization_setting(organization):
    setting = OrganizationSetting.objects.create(
        organization=organization,
        key="billing.default_due_day",
        value={"day": 1},
        description="Default Nepali month due day placeholder.",
        is_system_setting=True,
    )

    assert str(setting) == "Auras Education: billing.default_due_day"
    assert setting.value == {"day": 1}


@pytest.mark.django_db
def test_unique_organization_setting_key_per_organization(organization):
    OrganizationSetting.objects.create(organization=organization, key="currency", value={"code": "NPR"})

    with pytest.raises(IntegrityError):
        OrganizationSetting.objects.create(organization=organization, key="currency", value={"code": "USD"})


@pytest.mark.django_db
def test_create_tax_rate(organization):
    tax_rate = TaxRate.objects.create(
        organization=organization,
        name="VAT 13",
        rate_percentage=Decimal("13.0000"),
        tax_type=TaxRate.TaxType.VAT,
        effective_from=timezone.localdate(),
        notes="Placeholder tax configuration.",
    )

    assert str(tax_rate) == "VAT 13 (13.0000%)"
    assert tax_rate.is_active is True


@pytest.mark.django_db
def test_create_approval_rule(organization):
    branch = Branch.objects.create(organization=organization, code="MAIN", name="Main Branch", is_main_branch=True)
    required_role = Role.objects.create(code=Role.RoleCode.ACCOUNTANT, name="Accountant")
    escalation_role = Role.objects.create(code=Role.RoleCode.INSTITUTE_OWNER, name="Institute Owner")

    rule = ApprovalRule.objects.create(
        organization=organization,
        branch=branch,
        module_name="billing",
        action_name="payment_approval",
        minimum_amount=Decimal("1000.00"),
        maximum_amount=Decimal("100000.00"),
        required_role=required_role,
        escalation_role=escalation_role,
    )

    assert str(rule) == "Auras Education: billing.payment_approval (Main Branch)"
    assert rule.required_role == required_role
    assert rule.escalation_role == escalation_role
    assert rule.is_active is True


@pytest.mark.django_db
def test_relationship_behavior(organization):
    branch = Branch.objects.create(organization=organization, code="MAIN", name="Main Branch")
    OrganizationSetting.objects.create(organization=organization, key="locale", value={"timezone": "Asia/Kathmandu"})
    TaxRate.objects.create(organization=organization, name="VAT", rate_percentage=Decimal("13.0000"))

    assert list(organization.branches.all()) == [branch]
    assert organization.settings.count() == 1
    assert organization.tax_rates.count() == 1
