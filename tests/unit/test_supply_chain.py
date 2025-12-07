"""Unit tests for Supply Chain Compliance Service."""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend'))

import pytest

from src.services.supply_chain import SupplyChainComplianceService


class TestSection889Compliance:
    """Tests for Section 889 prohibited entity screening."""
    
    @pytest.fixture
    def service(self):
        return SupplyChainComplianceService()
    
    @pytest.mark.asyncio
    async def test_prohibited_entity_huawei(self, service):
        """Test that Huawei is flagged as prohibited."""
        result = await service.check_section_889("Huawei Technologies")
        assert result.status.value == "prohibited"
        assert len(result.prohibited_entities_matched) > 0
    
    @pytest.mark.asyncio
    async def test_prohibited_entity_zte(self, service):
        """Test that ZTE is flagged as prohibited."""
        result = await service.check_section_889("ZTE Corporation")
        assert result.status.value == "prohibited"
    
    @pytest.mark.asyncio
    async def test_prohibited_entity_hikvision(self, service):
        """Test that Hikvision is flagged as prohibited."""
        result = await service.check_section_889("Hikvision Camera Systems")
        assert result.status.value == "prohibited"
    
    @pytest.mark.asyncio
    async def test_compliant_supplier(self, service):
        """Test that a compliant supplier passes."""
        result = await service.check_section_889("Acme Technology Solutions")
        assert result.status.value == "compliant"
        assert len(result.prohibited_entities_matched) == 0
    
    @pytest.mark.asyncio
    async def test_telecom_equipment_requires_review(self, service):
        """Test that telecom equipment triggers review flag."""
        result = await service.check_section_889("Generic Telecom Equipment Inc")
        assert len(result.risk_indicators) > 0 or result.status.value == "requires_review"
    
    @pytest.mark.asyncio
    async def test_component_check(self, service):
        """Test that components are checked for prohibited entities."""
        components = [
            {"name": "Network Switch", "manufacturer": "Huawei"}
        ]
        result = await service.check_section_889("Distributor Corp", components=components)
        assert result.status.value == "prohibited"


class TestTAACompliance:
    """Tests for TAA country-of-origin compliance."""
    
    @pytest.fixture
    def service(self):
        return SupplyChainComplianceService()
    
    @pytest.mark.asyncio
    async def test_usa_is_compliant(self, service):
        """Test that USA is TAA compliant."""
        result = await service.check_taa_compliance("US")
        assert result.status.value == "compliant"
        assert result.is_designated_country is True
    
    @pytest.mark.asyncio
    async def test_canada_is_compliant(self, service):
        """Test that Canada is TAA compliant."""
        result = await service.check_taa_compliance("CA")
        assert result.status.value == "compliant"
        assert result.is_designated_country is True
    
    @pytest.mark.asyncio
    async def test_germany_is_compliant(self, service):
        """Test that Germany is TAA compliant."""
        result = await service.check_taa_compliance("DE")
        assert result.status.value == "compliant"
        assert result.is_designated_country is True
    
    @pytest.mark.asyncio
    async def test_china_is_non_compliant(self, service):
        """Test that China is NOT TAA compliant."""
        result = await service.check_taa_compliance("CN")
        assert result.status.value == "non_compliant"
        assert result.is_designated_country is False
    
    @pytest.mark.asyncio
    async def test_north_korea_is_prohibited(self, service):
        """Test that North Korea is prohibited (sanctioned)."""
        result = await service.check_taa_compliance("KP")
        assert result.status.value == "prohibited"
        assert result.is_prohibited is True
    
    @pytest.mark.asyncio
    async def test_iran_is_prohibited(self, service):
        """Test that Iran is prohibited (sanctioned)."""
        result = await service.check_taa_compliance("IR")
        assert result.status.value == "prohibited"
        assert result.is_prohibited is True
    
    @pytest.mark.asyncio
    async def test_russia_is_prohibited(self, service):
        """Test that Russia is prohibited (sanctioned)."""
        result = await service.check_taa_compliance("RU")
        assert result.status.value == "prohibited"
        assert result.is_prohibited is True
    
    @pytest.mark.asyncio
    async def test_unknown_country(self, service):
        """Test that unknown country code returns unknown status."""
        result = await service.check_taa_compliance("XX")
        assert result.status.value == "unknown"


class TestSupplierVerification:
    """Tests for complete supplier verification."""
    
    @pytest.fixture
    def service(self):
        return SupplyChainComplianceService()
    
    @pytest.mark.asyncio
    async def test_compliant_us_supplier(self, service):
        """Test verification of a compliant US supplier."""
        result = await service.verify_supplier(
            supplier_name="Acme Corp",
            country_of_origin="US"
        )
        assert result.verified is True
        assert result.risk_level == "low"
        assert result.section_889_result.status.value == "compliant"
        assert result.taa_result.status.value == "compliant"
    
    @pytest.mark.asyncio
    async def test_prohibited_supplier(self, service):
        """Test verification of a prohibited supplier."""
        result = await service.verify_supplier(
            supplier_name="Huawei Equipment",
            country_of_origin="CN"
        )
        assert result.risk_level == "critical"
        assert result.section_889_result.status.value == "prohibited"
    
    @pytest.mark.asyncio
    async def test_non_taa_supplier(self, service):
        """Test verification of a supplier from non-TAA country."""
        result = await service.verify_supplier(
            supplier_name="Thai Components Ltd",
            country_of_origin="TH"
        )
        assert result.taa_result.status.value == "non_compliant"
        assert result.risk_level in ["medium", "high"]
    
    @pytest.mark.asyncio
    async def test_missing_country_adds_risk(self, service):
        """Test that missing country adds risk factor."""
        result = await service.verify_supplier(
            supplier_name="Mystery Corp"
        )
        assert any("country" in f.lower() for f in result.risk_factors)
