"""Proposal Generation API endpoints."""
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.database.connection import get_db
from src.database.models import Organization, Opportunity
from src.services.proposal_generator import ProposalGenerator, ProposalSection

router = APIRouter()


class ProposalSectionRequest(BaseModel):
    """Request to generate a proposal section."""
    organization_id: uuid.UUID
    opportunity_id: uuid.UUID
    section_type: str  # executive_summary, technical_approach, management_approach, past_performance


class ProposalGenerateRequest(BaseModel):
    """Request to generate full proposal."""
    organization_id: uuid.UUID
    opportunity_id: uuid.UUID
    sections: Optional[List[str]] = None  # None = all sections


class ProposalSectionResponse(BaseModel):
    """Generated section response."""
    section_id: str
    title: str
    content: str
    word_count: int
    compliance_refs: List[str]
    confidence: float


class ProposalResponse(BaseModel):
    """Full proposal response."""
    opportunity_id: str
    organization_id: str
    sections: List[ProposalSectionResponse]
    executive_summary: str
    total_word_count: int
    compliance_matrix: dict


@router.post("/generate-section", response_model=ProposalSectionResponse)
async def generate_proposal_section(
    request: ProposalSectionRequest,
    db: AsyncSession = Depends(get_db),
) -> ProposalSectionResponse:
    """
    Generate a single proposal section using AI.
    
    Available sections:
    - executive_summary: Compelling summary of proposal
    - technical_approach: Detailed technical solution
    - management_approach: Management and staffing plan
    - past_performance: Relevant past performance narratives
    """
    # Validate section type
    valid_sections = ["executive_summary", "technical_approach", "management_approach", "past_performance"]
    if request.section_type not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section type. Valid types: {valid_sections}"
        )
    
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
    
    # Convert to dicts for generator
    org_dict = {
        "id": str(organization.id),
        "name": organization.name,
        "naics_codes": organization.naics_codes or [],
        "capabilities_narrative": organization.capabilities_narrative,
        "past_performance_summary": organization.past_performance_summary,
        "set_aside_types": organization.set_aside_types or [],
        "employee_count": organization.employee_count,
    }
    
    opp_dict = {
        "id": str(opportunity.id),
        "title": opportunity.title,
        "description": opportunity.description,
        "naics_code": opportunity.naics_code,
        "naics_description": opportunity.naics_description,
        "contracting_office_name": opportunity.contracting_office_name,
        "contract_type": opportunity.contract_type,
        "set_aside_type": opportunity.set_aside_type,
        "place_of_performance_city": opportunity.place_of_performance_city,
        "place_of_performance_state": opportunity.place_of_performance_state,
    }
    
    # Generate section
    generator = ProposalGenerator()
    section = await generator.generate_section(request.section_type, opp_dict, org_dict)
    
    return ProposalSectionResponse(
        section_id=section.section_id,
        title=section.title,
        content=section.content,
        word_count=section.word_count,
        compliance_refs=section.compliance_refs,
        confidence=section.confidence,
    )


@router.post("/generate", response_model=ProposalResponse)
async def generate_full_proposal(
    request: ProposalGenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> ProposalResponse:
    """
    Generate a complete proposal with all sections.
    
    Optionally specify which sections to generate.
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
    
    # Convert to dicts
    org_dict = {
        "id": str(organization.id),
        "name": organization.name,
        "naics_codes": organization.naics_codes or [],
        "capabilities_narrative": organization.capabilities_narrative,
        "past_performance_summary": organization.past_performance_summary,
        "set_aside_types": organization.set_aside_types or [],
        "employee_count": organization.employee_count,
    }
    
    opp_dict = {
        "id": str(opportunity.id),
        "title": opportunity.title,
        "description": opportunity.description,
        "naics_code": opportunity.naics_code,
        "naics_description": opportunity.naics_description,
        "contracting_office_name": opportunity.contracting_office_name,
        "contract_type": opportunity.contract_type,
        "set_aside_type": opportunity.set_aside_type,
        "place_of_performance_city": opportunity.place_of_performance_city,
        "place_of_performance_state": opportunity.place_of_performance_state,
    }
    
    # Generate proposal
    generator = ProposalGenerator()
    proposal = await generator.generate_proposal(opp_dict, org_dict, request.sections)
    
    return ProposalResponse(
        opportunity_id=proposal.opportunity_id,
        organization_id=proposal.organization_id,
        sections=[
            ProposalSectionResponse(
                section_id=s.section_id,
                title=s.title,
                content=s.content,
                word_count=s.word_count,
                compliance_refs=s.compliance_refs,
                confidence=s.confidence,
            )
            for s in proposal.sections
        ],
        executive_summary=proposal.executive_summary,
        total_word_count=proposal.total_word_count,
        compliance_matrix=proposal.compliance_matrix,
    )


@router.get("/templates")
async def list_proposal_templates():
    """List available proposal section templates."""
    return {
        "templates": [
            {
                "id": "executive_summary",
                "title": "Executive Summary",
                "description": "Compelling overview of the proposal",
                "max_words": 750,
            },
            {
                "id": "technical_approach",
                "title": "Technical Approach",
                "description": "Detailed technical solution and methodology",
                "max_words": 2000,
            },
            {
                "id": "management_approach",
                "title": "Management Approach",
                "description": "Management structure, staffing, and processes",
                "max_words": 1500,
            },
            {
                "id": "past_performance",
                "title": "Past Performance",
                "description": "Relevant contract history and outcomes",
                "max_words": 1000,
            },
        ]
    }

