"""Relevance Scoring API endpoints."""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import Organization, Opportunity, RelevanceScore
from src.services.relevance_scorer import RelevanceScorer
from src.api.schemas import (
    RelevanceScoreRequest, RelevanceScoreBatchRequest,
    RelevanceScoreResponse, RelevanceScoreListResponse
)

router = APIRouter()
scorer = RelevanceScorer()


@router.post("/calculate", response_model=RelevanceScoreResponse)
async def calculate_relevance_score(
    request: RelevanceScoreRequest,
    db: AsyncSession = Depends(get_db),
) -> RelevanceScoreResponse:
    """
    Calculate relevance score between an organization and an opportunity.
    
    The score considers:
    - NAICS code alignment
    - Semantic similarity between capabilities and requirements
    - Geographic proximity
    - Size and capacity appropriateness
    - Past performance relevance
    """
    # Get organization
    org_result = await db.execute(
        select(Organization).where(Organization.id == request.organization_id)
    )
    organization = org_result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get opportunity
    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.id == request.opportunity_id)
    )
    opportunity = opp_result.scalar_one_or_none()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Calculate score
    result = await scorer.calculate_score(organization, opportunity)
    
    # Store or update score
    existing = await db.execute(
        select(RelevanceScore).where(
            RelevanceScore.organization_id == request.organization_id,
            RelevanceScore.opportunity_id == request.opportunity_id,
        )
    )
    score_record = existing.scalar_one_or_none()
    
    if score_record:
        # Update existing
        score_record.overall_score = result.overall_score
        score_record.naics_score = result.naics_score
        score_record.semantic_score = result.semantic_score
        score_record.geographic_score = result.geographic_score
        score_record.size_score = result.size_score
        score_record.past_performance_score = result.past_performance_score
        score_record.component_weights = result.component_weights
        score_record.explanation = result.explanation
    else:
        # Create new
        score_record = RelevanceScore(
            organization_id=request.organization_id,
            opportunity_id=request.opportunity_id,
            overall_score=result.overall_score,
            naics_score=result.naics_score,
            semantic_score=result.semantic_score,
            geographic_score=result.geographic_score,
            size_score=result.size_score,
            past_performance_score=result.past_performance_score,
            component_weights=result.component_weights,
            explanation=result.explanation,
        )
        db.add(score_record)
    
    await db.commit()
    await db.refresh(score_record)
    
    return RelevanceScoreResponse.model_validate(score_record)


@router.post("/batch", response_model=RelevanceScoreListResponse)
async def calculate_batch_scores(
    request: RelevanceScoreBatchRequest,
    db: AsyncSession = Depends(get_db),
) -> RelevanceScoreListResponse:
    """
    Calculate relevance scores for multiple opportunities.
    
    Useful for scoring a pipeline of opportunities for an organization.
    """
    # Get organization
    org_result = await db.execute(
        select(Organization).where(Organization.id == request.organization_id)
    )
    organization = org_result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get opportunities
    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.id.in_(request.opportunity_ids))
    )
    opportunities = opp_result.scalars().all()
    
    if len(opportunities) != len(request.opportunity_ids):
        raise HTTPException(
            status_code=400, 
            detail="Some opportunity IDs were not found"
        )
    
    scores = []
    for opportunity in opportunities:
        result = await scorer.calculate_score(organization, opportunity)
        
        score_record = RelevanceScore(
            organization_id=request.organization_id,
            opportunity_id=opportunity.id,
            overall_score=result.overall_score,
            naics_score=result.naics_score,
            semantic_score=result.semantic_score,
            geographic_score=result.geographic_score,
            size_score=result.size_score,
            past_performance_score=result.past_performance_score,
            component_weights=result.component_weights,
            explanation=result.explanation,
        )
        
        # Merge (insert or update)
        score_record = await db.merge(score_record)
        scores.append(RelevanceScoreResponse.model_validate(score_record))
    
    await db.commit()
    
    return RelevanceScoreListResponse(
        items=sorted(scores, key=lambda x: x.overall_score, reverse=True),
        organization_id=request.organization_id,
    )


@router.get("/organization/{organization_id}", response_model=RelevanceScoreListResponse)
async def get_organization_scores(
    organization_id: uuid.UUID,
    min_score: float = 0.0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> RelevanceScoreListResponse:
    """
    Get all relevance scores for an organization.
    
    Returns scores sorted by overall_score descending.
    """
    stmt = select(RelevanceScore).where(
        RelevanceScore.organization_id == organization_id,
        RelevanceScore.overall_score >= min_score,
    ).order_by(RelevanceScore.overall_score.desc()).limit(limit)
    
    result = await db.execute(stmt)
    scores = result.scalars().all()
    
    return RelevanceScoreListResponse(
        items=[RelevanceScoreResponse.model_validate(s) for s in scores],
        organization_id=organization_id,
    )


@router.get("/{score_id}", response_model=RelevanceScoreResponse)
async def get_score(
    score_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RelevanceScoreResponse:
    """Get a specific relevance score by ID."""
    stmt = select(RelevanceScore).where(RelevanceScore.id == score_id)
    result = await db.execute(stmt)
    score = result.scalar_one_or_none()
    
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return RelevanceScoreResponse.model_validate(score)

