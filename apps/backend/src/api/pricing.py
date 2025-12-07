"""Pricing Intelligence API endpoints."""
import uuid
from typing import Optional, List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from decimal import Decimal

from src.database.connection import get_db
from src.database.models import Opportunity
from src.services.pricing_intelligence import PricingIntelligenceService

router = APIRouter()


class PricingRecommendationRequest(BaseModel):
    """Request for pricing recommendation."""
    opportunity_id: uuid.UUID
    labor_mix: Optional[Dict[str, int]] = None  # labor_category -> FTE count


class ShouldCostRequest(BaseModel):
    """Request for should-cost calculation."""
    labor_mix: Dict[str, int]  # labor_category -> FTE count
    duration_months: int = 12
    overhead_rate: float = 1.5
    profit_margin: float = 0.10


class LaborRateBenchmarkResponse(BaseModel):
    """Labor rate benchmark response."""
    labor_category: str
    min_rate: float
    max_rate: float
    median_rate: float
    average_rate: float
    sample_size: int
    data_source: str


class ContractBenchmarkResponse(BaseModel):
    """Contract value benchmark response."""
    naics_code: str
    psc_code: Optional[str]
    min_value: float
    max_value: float
    median_value: float
    average_value: float
    sample_size: int
    period: str


@router.post("/recommendation")
async def get_pricing_recommendation(
    request: PricingRecommendationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI-powered pricing recommendation for an opportunity.
    
    Analyzes:
    - Historical award data for NAICS/PSC
    - Government estimate (if available)
    - Labor rate benchmarks
    - Competitive positioning
    """
    # Fetch opportunity
    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.id == request.opportunity_id)
    )
    opportunity = opp_result.scalar_one_or_none()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Convert to dict
    opp_dict = {
        "id": str(opportunity.id),
        "title": opportunity.title,
        "description": opportunity.description,
        "naics_code": opportunity.naics_code,
        "psc_code": opportunity.psc_code,
        "estimated_value_min": opportunity.estimated_value_min,
        "estimated_value_max": opportunity.estimated_value_max,
        "set_aside_type": opportunity.set_aside_type,
        "contract_type": opportunity.contract_type,
    }
    
    # Get recommendation
    service = PricingIntelligenceService()
    result = await service.get_pricing_recommendation(
        opportunity=opp_dict,
        labor_mix=request.labor_mix,
    )
    
    return {
        "opportunity_id": result.opportunity_id,
        "recommended_price_min": float(result.recommended_price_min),
        "recommended_price_max": float(result.recommended_price_max),
        "competitive_position": result.competitive_position,
        "confidence": result.confidence,
        "factors": result.factors,
        "labor_rates": [
            {
                "labor_category": lr.labor_category,
                "median_rate": float(lr.median_rate),
                "min_rate": float(lr.min_rate),
                "max_rate": float(lr.max_rate),
            }
            for lr in result.labor_rates
        ],
        "notes": result.notes,
        "generated_at": result.generated_at.isoformat(),
    }


@router.post("/should-cost")
async def calculate_should_cost(request: ShouldCostRequest):
    """
    Calculate should-cost estimate based on labor mix.
    
    Provides detailed cost breakdown:
    - Direct labor costs by category
    - Overhead/G&A
    - Profit
    - Total price
    
    Labor categories available:
    - program_manager, project_manager
    - senior_engineer, engineer, junior_engineer
    - senior_analyst, analyst
    - security_engineer, data_scientist, cloud_architect
    - consultant_senior, consultant, subject_matter_expert
    - admin_assistant, executive_assistant
    """
    service = PricingIntelligenceService()
    
    result = await service.calculate_should_cost(
        labor_mix=request.labor_mix,
        duration_months=request.duration_months,
        overhead_rate=request.overhead_rate,
        profit_margin=request.profit_margin,
    )
    
    return result


@router.get("/labor-rates", response_model=List[LaborRateBenchmarkResponse])
async def get_labor_rate_benchmarks(
    categories: Optional[str] = None,  # Comma-separated list
):
    """
    Get labor rate benchmarks.
    
    Optionally filter by category keys (comma-separated).
    """
    service = PricingIntelligenceService()
    
    category_list = categories.split(",") if categories else None
    benchmarks = await service.get_labor_rate_benchmarks(category_list)
    
    return [
        LaborRateBenchmarkResponse(
            labor_category=b.labor_category,
            min_rate=float(b.min_rate),
            max_rate=float(b.max_rate),
            median_rate=float(b.median_rate),
            average_rate=float(b.average_rate),
            sample_size=b.sample_size,
            data_source=b.data_source,
        )
        for b in benchmarks
    ]


@router.get("/labor-rates/categories")
async def list_labor_categories():
    """List available labor rate categories."""
    service = PricingIntelligenceService()
    
    return {
        "categories": [
            {
                "key": key,
                "name": benchmark.labor_category,
                "median_rate": float(benchmark.median_rate),
            }
            for key, benchmark in service.LABOR_RATE_BENCHMARKS.items()
        ]
    }


@router.get("/contract-benchmarks", response_model=List[ContractBenchmarkResponse])
async def get_contract_benchmarks(
    naics_codes: Optional[str] = None,  # Comma-separated list
):
    """
    Get contract value benchmarks by NAICS code.
    
    Optionally filter by NAICS codes (comma-separated).
    """
    service = PricingIntelligenceService()
    
    code_list = naics_codes.split(",") if naics_codes else None
    benchmarks = await service.get_contract_benchmarks(code_list)
    
    return [
        ContractBenchmarkResponse(
            naics_code=b.naics_code,
            psc_code=b.psc_code,
            min_value=float(b.min_value),
            max_value=float(b.max_value),
            median_value=float(b.median_value),
            average_value=float(b.average_value),
            sample_size=b.sample_size,
            period=b.period,
        )
        for b in benchmarks
    ]

