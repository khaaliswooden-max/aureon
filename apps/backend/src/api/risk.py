"""Risk Assessment API endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import Organization, Opportunity, RiskAssessment
from src.services.risk_assessor import RiskAssessor
from src.api.schemas import RiskAssessmentRequest, RiskAssessmentResponse, RiskCategory

router = APIRouter()
assessor = RiskAssessor()


@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risk(
    request: RiskAssessmentRequest,
    db: AsyncSession = Depends(get_db),
) -> RiskAssessmentResponse:
    """
    Perform comprehensive risk assessment for a bid/no-bid decision.
    
    Evaluates:
    - Eligibility risk (set-asides, clearances, certifications)
    - Technical risk (capability gaps, technology requirements)
    - Pricing risk (competitive positioning, cost estimation)
    - Resource risk (staffing, availability, capacity)
    - Compliance risk (FAR/DFARS, regulatory requirements)
    - Timeline risk (response preparation, performance period)
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
    
    # Perform assessment
    result = await assessor.assess_risk(organization, opportunity)
    
    # Store or update assessment
    existing = await db.execute(
        select(RiskAssessment).where(
            RiskAssessment.organization_id == request.organization_id,
            RiskAssessment.opportunity_id == request.opportunity_id,
        )
    )
    assessment_record = existing.scalar_one_or_none()
    
    # Convert risk categories to dict for storage
    def risk_to_dict(risk):
        return {
            "level": risk.level,
            "score": risk.score,
            "factors": risk.factors,
        }
    
    if assessment_record:
        # Update existing
        assessment_record.overall_risk_level = result.overall_risk_level
        assessment_record.overall_risk_score = result.overall_risk_score
        assessment_record.eligibility_risk = risk_to_dict(result.eligibility_risk)
        assessment_record.technical_risk = risk_to_dict(result.technical_risk)
        assessment_record.pricing_risk = risk_to_dict(result.pricing_risk)
        assessment_record.resource_risk = risk_to_dict(result.resource_risk)
        assessment_record.compliance_risk = risk_to_dict(result.compliance_risk)
        assessment_record.timeline_risk = risk_to_dict(result.timeline_risk)
        assessment_record.risk_factors = result.risk_factors
        assessment_record.mitigation_suggestions = result.mitigation_suggestions
    else:
        # Create new
        assessment_record = RiskAssessment(
            organization_id=request.organization_id,
            opportunity_id=request.opportunity_id,
            overall_risk_level=result.overall_risk_level,
            overall_risk_score=result.overall_risk_score,
            eligibility_risk=risk_to_dict(result.eligibility_risk),
            technical_risk=risk_to_dict(result.technical_risk),
            pricing_risk=risk_to_dict(result.pricing_risk),
            resource_risk=risk_to_dict(result.resource_risk),
            compliance_risk=risk_to_dict(result.compliance_risk),
            timeline_risk=risk_to_dict(result.timeline_risk),
            risk_factors=result.risk_factors,
            mitigation_suggestions=result.mitigation_suggestions,
        )
        db.add(assessment_record)
    
    await db.commit()
    await db.refresh(assessment_record)
    
    # Convert back to response format
    def dict_to_risk_category(d):
        return RiskCategory(
            level=d["level"],
            score=d["score"],
            factors=d["factors"],
        )
    
    return RiskAssessmentResponse(
        id=assessment_record.id,
        organization_id=assessment_record.organization_id,
        opportunity_id=assessment_record.opportunity_id,
        overall_risk_level=assessment_record.overall_risk_level,
        overall_risk_score=float(assessment_record.overall_risk_score),
        eligibility_risk=dict_to_risk_category(assessment_record.eligibility_risk),
        technical_risk=dict_to_risk_category(assessment_record.technical_risk),
        pricing_risk=dict_to_risk_category(assessment_record.pricing_risk),
        resource_risk=dict_to_risk_category(assessment_record.resource_risk),
        compliance_risk=dict_to_risk_category(assessment_record.compliance_risk),
        timeline_risk=dict_to_risk_category(assessment_record.timeline_risk),
        risk_factors=assessment_record.risk_factors,
        mitigation_suggestions=assessment_record.mitigation_suggestions,
        assessed_at=assessment_record.assessed_at,
    )


@router.get("/{assessment_id}", response_model=RiskAssessmentResponse)
async def get_assessment(
    assessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RiskAssessmentResponse:
    """Get a specific risk assessment by ID."""
    stmt = select(RiskAssessment).where(RiskAssessment.id == assessment_id)
    result = await db.execute(stmt)
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    def dict_to_risk_category(d):
        return RiskCategory(
            level=d["level"],
            score=d["score"],
            factors=d["factors"],
        )
    
    return RiskAssessmentResponse(
        id=assessment.id,
        organization_id=assessment.organization_id,
        opportunity_id=assessment.opportunity_id,
        overall_risk_level=assessment.overall_risk_level,
        overall_risk_score=float(assessment.overall_risk_score),
        eligibility_risk=dict_to_risk_category(assessment.eligibility_risk),
        technical_risk=dict_to_risk_category(assessment.technical_risk),
        pricing_risk=dict_to_risk_category(assessment.pricing_risk),
        resource_risk=dict_to_risk_category(assessment.resource_risk),
        compliance_risk=dict_to_risk_category(assessment.compliance_risk),
        timeline_risk=dict_to_risk_category(assessment.timeline_risk),
        risk_factors=assessment.risk_factors,
        mitigation_suggestions=assessment.mitigation_suggestions,
        assessed_at=assessment.assessed_at,
    )


@router.get("/organization/{organization_id}/summary")
async def get_organization_risk_summary(
    organization_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get risk assessment summary for an organization's opportunities."""
    stmt = select(RiskAssessment).where(
        RiskAssessment.organization_id == organization_id
    )
    result = await db.execute(stmt)
    assessments = result.scalars().all()
    
    if not assessments:
        return {
            "organization_id": str(organization_id),
            "total_assessed": 0,
            "by_risk_level": {},
            "average_risk_score": None,
        }
    
    # Summarize by risk level
    by_level = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    total_score = 0.0
    
    for a in assessments:
        level = a.overall_risk_level.lower()
        if level in by_level:
            by_level[level] += 1
        total_score += float(a.overall_risk_score)
    
    return {
        "organization_id": str(organization_id),
        "total_assessed": len(assessments),
        "by_risk_level": by_level,
        "average_risk_score": round(total_score / len(assessments), 4),
    }

