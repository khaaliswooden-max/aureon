"""Supply Chain Compliance API endpoints."""
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.supply_chain import (
    SupplyChainComplianceService,
    ComplianceStatus,
)

router = APIRouter()


class SupplierVerifyRequest(BaseModel):
    """Request to verify a supplier."""
    supplier_name: str
    supplier_id: Optional[str] = None
    country_of_origin: Optional[str] = None
    components: Optional[List[dict]] = None


class Section889CheckRequest(BaseModel):
    """Request to check Section 889 compliance."""
    supplier_name: str
    components: Optional[List[dict]] = None


class TAACheckRequest(BaseModel):
    """Request to check TAA compliance."""
    country_code: str


class TAABatchCheckRequest(BaseModel):
    """Request to check multiple countries for TAA compliance."""
    country_codes: List[str]


class Section889Response(BaseModel):
    """Section 889 check response."""
    supplier_name: str
    status: str
    prohibited_entities_matched: List[str]
    risk_indicators: List[str]
    recommendation: str
    checked_at: str


class TAAResponse(BaseModel):
    """TAA check response."""
    country_code: str
    country_name: str
    status: str
    is_designated_country: bool
    is_prohibited: bool
    notes: str
    checked_at: str


class SupplierVerificationResponse(BaseModel):
    """Complete supplier verification response."""
    supplier_id: str
    supplier_name: str
    verified: bool
    section_889_status: str
    taa_status: Optional[str]
    overall_risk_score: float
    risk_level: str
    risk_factors: List[str]
    recommendations: List[str]
    verified_at: str


@router.post("/verify", response_model=SupplierVerificationResponse)
async def verify_supplier(request: SupplierVerifyRequest) -> SupplierVerificationResponse:
    """
    Perform complete supplier verification.
    
    Checks:
    - Section 889 prohibited entity screening
    - TAA country-of-origin compliance (if country provided)
    - Overall risk assessment
    
    Returns verification result with recommendations.
    """
    service = SupplyChainComplianceService()
    
    result = await service.verify_supplier(
        supplier_name=request.supplier_name,
        supplier_id=request.supplier_id,
        country_of_origin=request.country_of_origin,
        components=request.components,
    )
    
    return SupplierVerificationResponse(
        supplier_id=result.supplier_id,
        supplier_name=result.supplier_name,
        verified=result.verified,
        section_889_status=result.section_889_result.status.value,
        taa_status=result.taa_result.status.value if result.taa_result else None,
        overall_risk_score=result.overall_risk_score,
        risk_level=result.risk_level,
        risk_factors=result.risk_factors,
        recommendations=result.recommendations,
        verified_at=result.verified_at.isoformat(),
    )


@router.post("/section-889/check", response_model=Section889Response)
async def check_section_889(request: Section889CheckRequest) -> Section889Response:
    """
    Check supplier against Section 889 prohibited entities.
    
    Section 889 of the NDAA FY2019 prohibits federal agencies from:
    - Part A: Procuring covered telecommunications equipment
    - Part B: Contracting with entities using covered equipment
    
    Prohibited entities include:
    - Huawei Technologies
    - ZTE Corporation
    - Hytera Communications
    - Hangzhou Hikvision
    - Dahua Technology
    - And their subsidiaries/affiliates
    """
    service = SupplyChainComplianceService()
    
    result = await service.check_section_889(
        supplier_name=request.supplier_name,
        components=request.components,
    )
    
    return Section889Response(
        supplier_name=result.supplier_name,
        status=result.status.value,
        prohibited_entities_matched=result.prohibited_entities_matched,
        risk_indicators=result.risk_indicators,
        recommendation=result.recommendation,
        checked_at=result.checked_at.isoformat(),
    )


@router.post("/taa/check", response_model=TAAResponse)
async def check_taa_compliance(request: TAACheckRequest) -> TAAResponse:
    """
    Check TAA (Trade Agreements Act) compliance for country of origin.
    
    TAA requires that products acquired by the federal government be
    manufactured or substantially transformed in the US or a designated country.
    
    Accepts ISO 2-letter country codes (e.g., US, CA, CN, DE).
    """
    service = SupplyChainComplianceService()
    
    result = await service.check_taa_compliance(request.country_code)
    
    return TAAResponse(
        country_code=result.country_code,
        country_name=result.country_name,
        status=result.status.value,
        is_designated_country=result.is_designated_country,
        is_prohibited=result.is_prohibited,
        notes=result.notes,
        checked_at=result.checked_at.isoformat(),
    )


@router.post("/taa/batch-check")
async def batch_check_taa(request: TAABatchCheckRequest):
    """
    Check multiple countries for TAA compliance.
    
    Useful for validating supply chain with multiple country sources.
    """
    service = SupplyChainComplianceService()
    
    results = await service.batch_check_countries(request.country_codes)
    
    return {
        "results": {
            code: {
                "country_name": result.country_name,
                "status": result.status.value,
                "is_designated": result.is_designated_country,
                "is_prohibited": result.is_prohibited,
            }
            for code, result in results.items()
        },
        "summary": {
            "total_checked": len(results),
            "compliant": sum(1 for r in results.values() if r.status == ComplianceStatus.COMPLIANT),
            "non_compliant": sum(1 for r in results.values() if r.status == ComplianceStatus.NON_COMPLIANT),
            "prohibited": sum(1 for r in results.values() if r.status == ComplianceStatus.PROHIBITED),
        }
    }


@router.get("/taa/designated-countries")
async def list_taa_designated_countries():
    """
    List all TAA designated countries.
    
    Returns countries where products can be procured from for federal contracts.
    """
    service = SupplyChainComplianceService()
    
    return {
        "designated_countries": [
            {"code": code, "name": name}
            for code, (name, _) in service.TAA_DESIGNATED_COUNTRIES.items()
        ],
        "total": len(service.TAA_DESIGNATED_COUNTRIES),
    }


@router.get("/section-889/prohibited-entities")
async def list_prohibited_entities():
    """
    List Section 889 prohibited entities.
    
    Returns the current list of prohibited telecommunications equipment providers.
    """
    service = SupplyChainComplianceService()
    
    return {
        "prohibited_entities": [
            {"key": key, "name": name}
            for key, name in service.PROHIBITED_ENTITIES.items()
        ],
        "total": len(service.PROHIBITED_ENTITIES),
        "note": "This list includes primary entities and known subsidiaries. Additional verification may be required.",
    }

