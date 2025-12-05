"""
Core domain entities for Aureon.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum

from aureon_domain.types import (
    SetAsideType,
    RiskLevel,
    NoticeType,
    ContractType,
    OrganizationStatus,
    OpportunityStatus,
)


@dataclass
class Address:
    """Physical address."""
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "USA"


@dataclass
class Contact:
    """Contact information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None


@dataclass
class Organization:
    """Organization/company in the procurement ecosystem."""
    id: str
    name: str
    legal_name: Optional[str] = None
    uei: Optional[str] = None
    duns_number: Optional[str] = None
    cage_code: Optional[str] = None
    ein: Optional[str] = None
    
    naics_codes: List[str] = field(default_factory=list)
    psc_codes: List[str] = field(default_factory=list)
    set_aside_types: List[SetAsideType] = field(default_factory=list)
    
    primary_address: Optional[Address] = None
    primary_contact: Optional[Contact] = None
    
    employee_count: Optional[int] = None
    annual_revenue: Optional[Decimal] = None
    founded_year: Optional[int] = None
    
    capabilities_narrative: Optional[str] = None
    core_competencies: List[str] = field(default_factory=list)
    past_performance_summary: Optional[str] = None
    
    status: OrganizationStatus = OrganizationStatus.ACTIVE
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractingOffice:
    """Contracting office information."""
    name: Optional[str] = None
    address: Optional[Address] = None
    agency_code: Optional[str] = None
    agency_name: Optional[str] = None


@dataclass
class Opportunity:
    """Procurement opportunity."""
    id: str
    source_id: str
    source_system: str
    
    title: str
    description: Optional[str] = None
    notice_type: NoticeType = NoticeType.OTHER
    solicitation_number: Optional[str] = None
    
    naics_code: Optional[str] = None
    naics_description: Optional[str] = None
    psc_code: Optional[str] = None
    psc_description: Optional[str] = None
    set_aside_type: Optional[SetAsideType] = None
    
    posted_date: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    archive_date: Optional[datetime] = None
    
    contract_type: Optional[ContractType] = None
    estimated_value_min: Optional[Decimal] = None
    estimated_value_max: Optional[Decimal] = None
    
    place_of_performance: Optional[Address] = None
    contracting_office: Optional[ContractingOffice] = None
    primary_contact: Optional[Contact] = None
    
    status: OpportunityStatus = OpportunityStatus.ACTIVE
    security_clearance_required: Optional[str] = None
    
    raw_data: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    ingested_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskCategory:
    """Individual risk category assessment."""
    level: RiskLevel
    score: float  # 0.0 to 1.0
    factors: List[str] = field(default_factory=list)


@dataclass
class RelevanceScore:
    """Relevance score between organization and opportunity."""
    id: str
    organization_id: str
    opportunity_id: str
    
    overall_score: float  # 0.0 to 1.0
    
    naics_score: Optional[float] = None
    semantic_score: Optional[float] = None
    geographic_score: Optional[float] = None
    size_score: Optional[float] = None
    past_performance_score: Optional[float] = None
    
    component_weights: Dict[str, float] = field(default_factory=dict)
    explanation: Optional[str] = None
    
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    model_version: str = "v1.0.0"


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment for bid/no-bid decision."""
    id: str
    organization_id: str
    opportunity_id: str
    
    overall_risk_level: RiskLevel
    overall_risk_score: float  # 0.0 to 1.0
    
    eligibility_risk: RiskCategory = field(default_factory=lambda: RiskCategory(RiskLevel.LOW, 0.0))
    technical_risk: RiskCategory = field(default_factory=lambda: RiskCategory(RiskLevel.LOW, 0.0))
    pricing_risk: RiskCategory = field(default_factory=lambda: RiskCategory(RiskLevel.LOW, 0.0))
    resource_risk: RiskCategory = field(default_factory=lambda: RiskCategory(RiskLevel.LOW, 0.0))
    compliance_risk: RiskCategory = field(default_factory=lambda: RiskCategory(RiskLevel.LOW, 0.0))
    timeline_risk: RiskCategory = field(default_factory=lambda: RiskCategory(RiskLevel.LOW, 0.0))
    
    risk_factors: List[str] = field(default_factory=list)
    mitigation_suggestions: List[str] = field(default_factory=list)
    
    assessed_at: datetime = field(default_factory=datetime.utcnow)
    model_version: str = "v1.0.0"

