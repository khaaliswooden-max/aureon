"""Pydantic schemas for API request/response models."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


# ============ Organization Schemas ============

class OrganizationBase(BaseModel):
    """Base organization fields."""
    name: str = Field(..., min_length=1, max_length=500)
    legal_name: Optional[str] = Field(None, max_length=500)
    uei: Optional[str] = Field(None, max_length=12)
    duns_number: Optional[str] = Field(None, max_length=13)
    cage_code: Optional[str] = Field(None, max_length=10)
    naics_codes: Optional[List[str]] = None
    psc_codes: Optional[List[str]] = None
    set_aside_types: Optional[List[str]] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: str = "USA"
    employee_count: Optional[int] = Field(None, ge=0)
    annual_revenue: Optional[Decimal] = Field(None, ge=0)
    capabilities_narrative: Optional[str] = None
    past_performance_summary: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    legal_name: Optional[str] = None
    naics_codes: Optional[List[str]] = None
    psc_codes: Optional[List[str]] = None
    set_aside_types: Optional[List[str]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[Decimal] = None
    capabilities_narrative: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    """Schema for organization responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ============ Opportunity Schemas ============

class OpportunityBase(BaseModel):
    """Base opportunity fields."""
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    notice_type: Optional[str] = None
    solicitation_number: Optional[str] = None
    naics_code: Optional[str] = None
    psc_code: Optional[str] = None
    set_aside_type: Optional[str] = None
    response_deadline: Optional[datetime] = None
    posted_date: Optional[datetime] = None
    contract_type: Optional[str] = None
    estimated_value_min: Optional[Decimal] = None
    estimated_value_max: Optional[Decimal] = None
    place_of_performance_city: Optional[str] = None
    place_of_performance_state: Optional[str] = None
    contracting_office_name: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    """Schema for creating an opportunity."""
    source_id: str
    source_system: str = "manual"


class OpportunityResponse(OpportunityBase):
    """Schema for opportunity responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    source_id: str
    source_system: str
    status: str
    created_at: datetime
    updated_at: datetime


class OpportunitySearchParams(BaseModel):
    """Search parameters for opportunities."""
    query: Optional[str] = None
    naics_codes: Optional[List[str]] = None
    set_aside_types: Optional[List[str]] = None
    states: Optional[List[str]] = None
    notice_types: Optional[List[str]] = None
    posted_after: Optional[datetime] = None
    deadline_after: Optional[datetime] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    status: Optional[str] = "active"
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = "posted_date"
    sort_order: str = "desc"


class OpportunityListResponse(BaseModel):
    """Paginated list of opportunities."""
    items: List[OpportunityResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============ Relevance Scoring Schemas ============

class RelevanceScoreRequest(BaseModel):
    """Request to calculate relevance score."""
    organization_id: uuid.UUID
    opportunity_id: uuid.UUID


class RelevanceScoreBatchRequest(BaseModel):
    """Request to calculate relevance scores for multiple opportunities."""
    organization_id: uuid.UUID
    opportunity_ids: List[uuid.UUID] = Field(..., max_length=100)


class RelevanceScoreResponse(BaseModel):
    """Relevance score response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    organization_id: uuid.UUID
    opportunity_id: uuid.UUID
    overall_score: float
    naics_score: Optional[float] = None
    semantic_score: Optional[float] = None
    geographic_score: Optional[float] = None
    size_score: Optional[float] = None
    past_performance_score: Optional[float] = None
    explanation: Optional[str] = None
    calculated_at: datetime


class RelevanceScoreListResponse(BaseModel):
    """List of relevance scores."""
    items: List[RelevanceScoreResponse]
    organization_id: uuid.UUID


# ============ Risk Assessment Schemas ============

class RiskAssessmentRequest(BaseModel):
    """Request to perform risk assessment."""
    organization_id: uuid.UUID
    opportunity_id: uuid.UUID


class RiskCategory(BaseModel):
    """Risk category details."""
    level: str = Field(..., pattern="^(low|medium|high|critical)$")
    score: float = Field(..., ge=0, le=1)
    factors: List[str] = []


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    organization_id: uuid.UUID
    opportunity_id: uuid.UUID
    overall_risk_level: str
    overall_risk_score: float
    eligibility_risk: RiskCategory
    technical_risk: RiskCategory
    pricing_risk: RiskCategory
    resource_risk: RiskCategory
    compliance_risk: RiskCategory
    timeline_risk: RiskCategory
    risk_factors: List[str]
    mitigation_suggestions: List[str]
    assessed_at: datetime


# ============ Ingestion Schemas ============

class IngestionRequest(BaseModel):
    """Request to trigger data ingestion."""
    source: str = Field(..., pattern="^(sam_gov|grants_gov|state_portal)$")
    params: Optional[Dict[str, Any]] = None


class IngestionStatusResponse(BaseModel):
    """Ingestion status response."""
    id: uuid.UUID
    source_system: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_fetched: int
    records_inserted: int
    records_updated: int
    records_failed: int
    error_message: Optional[str] = None

