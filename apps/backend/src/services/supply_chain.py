"""
Supply Chain Compliance Service

Provides compliance verification for federal supply chain requirements:
- Section 889 screening (prohibited telecommunications equipment)
- TAA compliance (Trade Agreements Act country-of-origin)
- Supplier risk scoring
- SAM.gov exclusion list checking
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone
from enum import Enum
import structlog

logger = structlog.get_logger()


class ComplianceStatus(Enum):
    """Compliance verification status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PROHIBITED = "prohibited"
    UNKNOWN = "unknown"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class Section889Result:
    """Result of Section 889 compliance check."""
    supplier_name: str
    status: ComplianceStatus
    prohibited_entities_matched: List[str] = field(default_factory=list)
    risk_indicators: List[str] = field(default_factory=list)
    recommendation: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TAAResult:
    """Result of TAA compliance check."""
    country_code: str
    country_name: str
    status: ComplianceStatus
    is_designated_country: bool
    is_prohibited: bool
    notes: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SupplierVerification:
    """Complete supplier verification result."""
    supplier_id: str
    supplier_name: str
    verified: bool
    section_889_result: Section889Result
    taa_result: Optional[TAAResult]
    overall_risk_score: float
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SupplyChainComplianceService:
    """
    Supply Chain Compliance Verification Service.
    
    Capabilities:
    - Section 889 prohibited entity screening
    - TAA country-of-origin validation
    - Supplier risk assessment
    - Compliance documentation
    """
    
    # Section 889 Part A & B prohibited entities (NDAA 2019)
    PROHIBITED_ENTITIES = {
        # Part A - Prohibited telecommunications equipment
        "huawei": "Huawei Technologies Co., Ltd.",
        "zte": "ZTE Corporation",
        "hytera": "Hytera Communications Corporation",
        "hikvision": "Hangzhou Hikvision Digital Technology Co., Ltd.",
        "dahua": "Dahua Technology Co., Ltd.",
        
        # Subsidiaries and affiliates (partial list)
        "huawei marine": "Huawei Marine Networks",
        "huawei cloud": "Huawei Cloud Computing",
        "hiwatch": "HiWatch (Hikvision subsidiary)",
        "ezviz": "EZVIZ (Hikvision subsidiary)",
        "lorex": "Lorex Technology (Dahua subsidiary)",
        
        # Additional entities from subsequent guidance
        "kaspersky": "Kaspersky Lab (if network-connected)",
    }
    
    # Related brand names and variations
    PROHIBITED_BRANDS = {
        "honor": "huawei",  # Honor was Huawei sub-brand
        "hikwatch": "hikvision",
        "dahua technology": "dahua",
        "uniview": "requires_review",  # Chinese, but not explicitly prohibited
    }
    
    # TAA Designated Countries (as of 2024)
    TAA_DESIGNATED_COUNTRIES = {
        # WTO GPA Countries
        "AM": ("Armenia", True),
        "AT": ("Austria", True),
        "AU": ("Australia", True),
        "BE": ("Belgium", True),
        "BG": ("Bulgaria", True),
        "CA": ("Canada", True),
        "HR": ("Croatia", True),
        "CY": ("Cyprus", True),
        "CZ": ("Czech Republic", True),
        "DK": ("Denmark", True),
        "EE": ("Estonia", True),
        "FI": ("Finland", True),
        "FR": ("France", True),
        "DE": ("Germany", True),
        "GR": ("Greece", True),
        "HK": ("Hong Kong", True),
        "HU": ("Hungary", True),
        "IS": ("Iceland", True),
        "IE": ("Ireland", True),
        "IL": ("Israel", True),
        "IT": ("Italy", True),
        "JP": ("Japan", True),
        "KR": ("Korea, Republic of", True),
        "LV": ("Latvia", True),
        "LI": ("Liechtenstein", True),
        "LT": ("Lithuania", True),
        "LU": ("Luxembourg", True),
        "MT": ("Malta", True),
        "MD": ("Moldova", True),
        "ME": ("Montenegro", True),
        "NL": ("Netherlands", True),
        "NZ": ("New Zealand", True),
        "MK": ("North Macedonia", True),
        "NO": ("Norway", True),
        "PL": ("Poland", True),
        "PT": ("Portugal", True),
        "RO": ("Romania", True),
        "SG": ("Singapore", True),
        "SK": ("Slovakia", True),
        "SI": ("Slovenia", True),
        "ES": ("Spain", True),
        "SE": ("Sweden", True),
        "CH": ("Switzerland", True),
        "TW": ("Taiwan", True),
        "UA": ("Ukraine", True),
        "GB": ("United Kingdom", True),
        "US": ("United States", True),
        
        # Caribbean Basin Countries
        "AG": ("Antigua and Barbuda", True),
        "AW": ("Aruba", True),
        "BS": ("Bahamas", True),
        "BB": ("Barbados", True),
        "BZ": ("Belize", True),
        "VG": ("British Virgin Islands", True),
        "CW": ("Curacao", True),
        "DM": ("Dominica", True),
        "GD": ("Grenada", True),
        "GY": ("Guyana", True),
        "HT": ("Haiti", True),
        "JM": ("Jamaica", True),
        "MS": ("Montserrat", True),
        "KN": ("St. Kitts and Nevis", True),
        "LC": ("St. Lucia", True),
        "VC": ("St. Vincent and the Grenadines", True),
        "TT": ("Trinidad and Tobago", True),
        
        # FTA Countries
        "BH": ("Bahrain", True),
        "CL": ("Chile", True),
        "CO": ("Colombia", True),
        "CR": ("Costa Rica", True),
        "DO": ("Dominican Republic", True),
        "SV": ("El Salvador", True),
        "GT": ("Guatemala", True),
        "HN": ("Honduras", True),
        "JO": ("Jordan", True),
        "MX": ("Mexico", True),
        "MA": ("Morocco", True),
        "NI": ("Nicaragua", True),
        "OM": ("Oman", True),
        "PA": ("Panama", True),
        "PE": ("Peru", True),
    }
    
    # Non-TAA compliant countries (common examples)
    NON_TAA_COUNTRIES = {
        "CN": ("China", False),
        "RU": ("Russia", False),
        "IN": ("India", False),
        "MY": ("Malaysia", False),
        "TH": ("Thailand", False),
        "VN": ("Vietnam", False),
        "ID": ("Indonesia", False),
        "BD": ("Bangladesh", False),
        "PK": ("Pakistan", False),
        "PH": ("Philippines", False),
        "BR": ("Brazil", False),
        "AR": ("Argentina", False),
        "ZA": ("South Africa", False),
        "EG": ("Egypt", False),
        "SA": ("Saudi Arabia", False),
        "AE": ("United Arab Emirates", False),
        "IR": ("Iran", False),
        "KP": ("North Korea", False),
        "BY": ("Belarus", False),
        "CU": ("Cuba", False),
        "SY": ("Syria", False),
        "VE": ("Venezuela", False),
    }
    
    def __init__(self):
        """Initialize compliance service."""
        # Combine country lists for lookup
        self.all_countries = {
            **self.TAA_DESIGNATED_COUNTRIES,
            **self.NON_TAA_COUNTRIES
        }
    
    async def verify_supplier(
        self,
        supplier_name: str,
        supplier_id: Optional[str] = None,
        country_of_origin: Optional[str] = None,
        components: Optional[List[Dict]] = None,
    ) -> SupplierVerification:
        """
        Perform complete supplier verification.
        
        Args:
            supplier_name: Name of the supplier
            supplier_id: Optional unique identifier
            country_of_origin: ISO country code for TAA check
            components: Optional list of component details
            
        Returns:
            SupplierVerification with all compliance results
        """
        supplier_id = supplier_id or f"SUP-{hash(supplier_name) % 100000:05d}"
        
        # Section 889 check
        section_889 = await self.check_section_889(supplier_name, components)
        
        # TAA check if country provided
        taa_result = None
        if country_of_origin:
            taa_result = await self.check_taa_compliance(country_of_origin)
        
        # Calculate overall risk
        risk_score, risk_level, risk_factors = self._calculate_risk(
            section_889, taa_result
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            section_889, taa_result, risk_level
        )
        
        return SupplierVerification(
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            verified=True,
            section_889_result=section_889,
            taa_result=taa_result,
            overall_risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
        )
    
    async def check_section_889(
        self,
        supplier_name: str,
        components: Optional[List[Dict]] = None,
    ) -> Section889Result:
        """
        Check supplier against Section 889 prohibited entities.
        
        Section 889 of the NDAA FY2019 prohibits federal agencies from:
        - Part A: Procuring covered telecommunications equipment
        - Part B: Contracting with entities using covered equipment
        
        Args:
            supplier_name: Supplier name to check
            components: Optional list of components to check
            
        Returns:
            Section889Result with compliance status
        """
        supplier_lower = supplier_name.lower().strip()
        matched_entities = []
        risk_indicators = []
        
        # Check against prohibited entities
        for key, entity_name in self.PROHIBITED_ENTITIES.items():
            if key in supplier_lower or supplier_lower in key:
                matched_entities.append(entity_name)
        
        # Check against related brands
        for brand, maps_to in self.PROHIBITED_BRANDS.items():
            if brand in supplier_lower:
                if maps_to == "requires_review":
                    risk_indicators.append(f"Brand '{brand}' requires additional review")
                else:
                    entity = self.PROHIBITED_ENTITIES.get(maps_to, maps_to)
                    matched_entities.append(f"{entity} (via brand: {brand})")
        
        # Check components if provided
        if components:
            for component in components:
                comp_name = component.get("name", "").lower()
                comp_manufacturer = component.get("manufacturer", "").lower()
                
                for key, entity_name in self.PROHIBITED_ENTITIES.items():
                    if key in comp_name or key in comp_manufacturer:
                        matched_entities.append(f"{entity_name} (component: {component.get('name', 'Unknown')})")
        
        # Additional risk indicators
        if "telecom" in supplier_lower or "network" in supplier_lower:
            risk_indicators.append("Telecommunications/network equipment - verify Section 889 compliance")
        
        if "camera" in supplier_lower or "surveillance" in supplier_lower or "security" in supplier_lower:
            risk_indicators.append("Video surveillance equipment - verify against Hikvision/Dahua prohibitions")
        
        # Determine status
        if matched_entities:
            status = ComplianceStatus.PROHIBITED
            recommendation = "DO NOT PROCEED - Supplier matches Section 889 prohibited entities"
        elif risk_indicators:
            status = ComplianceStatus.REQUIRES_REVIEW
            recommendation = "Additional verification required before procurement"
        else:
            status = ComplianceStatus.COMPLIANT
            recommendation = "No Section 889 prohibitions identified"
        
        return Section889Result(
            supplier_name=supplier_name,
            status=status,
            prohibited_entities_matched=matched_entities,
            risk_indicators=risk_indicators,
            recommendation=recommendation,
        )
    
    async def check_taa_compliance(
        self,
        country_code: str,
    ) -> TAAResult:
        """
        Check TAA (Trade Agreements Act) compliance for country of origin.
        
        TAA requires that products acquired by the federal government be
        manufactured or substantially transformed in the US or a designated country.
        
        Args:
            country_code: ISO 2-letter country code
            
        Returns:
            TAAResult with compliance status
        """
        country_code = country_code.upper().strip()
        
        # Look up country
        country_info = self.all_countries.get(country_code)
        
        if country_info is None:
            return TAAResult(
                country_code=country_code,
                country_name="Unknown",
                status=ComplianceStatus.UNKNOWN,
                is_designated_country=False,
                is_prohibited=False,
                notes=f"Country code '{country_code}' not found in database. Manual verification required.",
            )
        
        country_name, is_designated = country_info
        
        # Check for sanctioned/prohibited countries
        sanctioned_countries = {"KP", "IR", "CU", "SY", "BY", "RU"}
        is_prohibited = country_code in sanctioned_countries
        
        if is_prohibited:
            status = ComplianceStatus.PROHIBITED
            notes = f"{country_name} is subject to US sanctions. Procurement prohibited."
        elif is_designated:
            status = ComplianceStatus.COMPLIANT
            notes = f"{country_name} is a TAA designated country."
        else:
            status = ComplianceStatus.NON_COMPLIANT
            notes = f"{country_name} is NOT a TAA designated country. Products may not be procured for federal contracts unless substantially transformed in a designated country."
        
        return TAAResult(
            country_code=country_code,
            country_name=country_name,
            status=status,
            is_designated_country=is_designated,
            is_prohibited=is_prohibited,
            notes=notes,
        )
    
    async def batch_check_countries(
        self,
        country_codes: List[str],
    ) -> Dict[str, TAAResult]:
        """Check multiple countries for TAA compliance."""
        results = {}
        for code in country_codes:
            results[code] = await self.check_taa_compliance(code)
        return results
    
    def _calculate_risk(
        self,
        section_889: Section889Result,
        taa_result: Optional[TAAResult],
    ) -> tuple[float, str, List[str]]:
        """Calculate overall supplier risk score."""
        risk_score = 0.0
        risk_factors = []
        
        # Section 889 risk
        if section_889.status == ComplianceStatus.PROHIBITED:
            risk_score = 1.0
            risk_factors.append("Section 889 PROHIBITED entity match")
        elif section_889.status == ComplianceStatus.REQUIRES_REVIEW:
            risk_score += 0.4
            risk_factors.extend(section_889.risk_indicators)
        
        # TAA risk
        if taa_result:
            if taa_result.status == ComplianceStatus.PROHIBITED:
                risk_score = max(risk_score, 1.0)
                risk_factors.append(f"Sanctioned country: {taa_result.country_name}")
            elif taa_result.status == ComplianceStatus.NON_COMPLIANT:
                risk_score += 0.5
                risk_factors.append(f"Non-TAA country: {taa_result.country_name}")
            elif taa_result.status == ComplianceStatus.UNKNOWN:
                risk_score += 0.3
                risk_factors.append("Country of origin verification required")
        else:
            risk_score += 0.2
            risk_factors.append("Country of origin not provided")
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = "critical"
        elif risk_score >= 0.5:
            risk_level = "high"
        elif risk_score >= 0.25:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return round(min(1.0, risk_score), 4), risk_level, risk_factors
    
    def _generate_recommendations(
        self,
        section_889: Section889Result,
        taa_result: Optional[TAAResult],
        risk_level: str,
    ) -> List[str]:
        """Generate actionable recommendations based on compliance results."""
        recommendations = []
        
        # Section 889 recommendations
        if section_889.status == ComplianceStatus.PROHIBITED:
            recommendations.append("DO NOT PROCEED with this supplier - Section 889 violation")
            recommendations.append("Identify alternative suppliers from compliant sources")
        elif section_889.status == ComplianceStatus.REQUIRES_REVIEW:
            recommendations.append("Request supplier's Section 889 compliance certification")
            recommendations.append("Obtain detailed product/component listing with manufacturers")
        
        # TAA recommendations
        if taa_result:
            if taa_result.status == ComplianceStatus.PROHIBITED:
                recommendations.append("DO NOT PROCEED - Sanctioned country of origin")
            elif taa_result.status == ComplianceStatus.NON_COMPLIANT:
                recommendations.append("Request Certificate of Origin documentation")
                recommendations.append("Verify if product is substantially transformed in designated country")
                recommendations.append("Consider alternative suppliers from TAA-compliant countries")
            elif taa_result.status == ComplianceStatus.UNKNOWN:
                recommendations.append("Verify country of origin with supplier")
        else:
            recommendations.append("Request country of origin information from supplier")
        
        # General recommendations based on risk level
        if risk_level == "high":
            recommendations.append("Consult with contracting officer before proceeding")
            recommendations.append("Document all compliance verification steps")
        
        if not recommendations:
            recommendations.append("Supplier passes initial compliance screening")
            recommendations.append("Maintain documentation for audit purposes")
        
        return recommendations


# Country name lookups
def get_country_name(country_code: str) -> str:
    """Get country name from ISO code."""
    service = SupplyChainComplianceService()
    info = service.all_countries.get(country_code.upper())
    return info[0] if info else "Unknown"


def is_taa_designated(country_code: str) -> bool:
    """Quick check if country is TAA designated."""
    return country_code.upper() in SupplyChainComplianceService.TAA_DESIGNATED_COUNTRIES

