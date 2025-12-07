"""Win Probability API endpoints."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.database.connection import get_db
from src.database.models import Organization, Opportunity
from src.services.win_probability import WinProbabilityModel, WinProbabilityResult

router = APIRouter()


class WinProbabilityRequest(BaseModel):
    """Request to calculate win probability."""
    organization_id: uuid.UUID
    opportunity_id: uuid.UUID


class WinProbabilityResponse(BaseModel):
    """Win probability response."""
    opportunity_id: str
    win_probability: float
    match_score: float
    factors: dict
    recommendation: str
    confidence: float
    analysis: dict


@router.post("/calculate", response_model=WinProbabilityResponse)
async def calculate_win_probability(
    request: WinProbabilityRequest,
    db: AsyncSession = Depends(get_db),
) -> WinProbabilityResponse:
    """
    Calculate win probability for an organization-opportunity pair.
    
    Uses AI/ML model to predict likelihood of winning based on:
    - Capability alignment (NAICS/PSC)
    - Set-aside eligibility
    - Past performance relevance
    - Agency relationships
    - Geographic fit
    - Competition level
    - Pricing position
    """
    # Fetch organization
    org_result = await db.execute(
        select(Organization).where(Organization.id == request.organization_id)
    )
    organization = org_result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Fetch opportunity
    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.id == request.opportunity_id)
    )
    opportunity = opp_result.scalar_one_or_none()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Calculate win probability
    model = WinProbabilityModel()
    result = await model.calculate_win_probability(organization, opportunity)
    
    return WinProbabilityResponse(
        opportunity_id=result.opportunity_id,
        win_probability=result.win_probability,
        match_score=result.match_score,
        factors=result.factors,
        recommendation=result.recommendation,
        confidence=result.confidence,
        analysis=result.analysis,
    )


@router.post("/batch")
async def batch_win_probability(
    organization_id: uuid.UUID,
    opportunity_ids: list[uuid.UUID],
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate win probability for multiple opportunities.
    
    Returns sorted list from highest to lowest win probability.
    """
    # Fetch organization
    org_result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = org_result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Fetch opportunities
    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.id.in_(opportunity_ids))
    )
    opportunities = opp_result.scalars().all()
    
    # Calculate for each opportunity
    model = WinProbabilityModel()
    results = []
    
    for opportunity in opportunities:
        result = await model.calculate_win_probability(organization, opportunity)
        results.append({
            "opportunity_id": str(opportunity.id),
            "title": opportunity.title,
            "win_probability": result.win_probability,
            "match_score": result.match_score,
            "recommendation": result.recommendation,
        })
    
    # Sort by win probability descending
    results.sort(key=lambda x: x["win_probability"], reverse=True)
    
    return {
        "organization_id": str(organization_id),
        "results": results,
        "total": len(results),
    }

