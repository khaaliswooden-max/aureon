"""SQLAlchemy ORM models for Aureon."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    Column, String, Text, Integer, Numeric, DateTime, Boolean,
    ForeignKey, CheckConstraint, UniqueConstraint, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database.connection import Base


class Organization(Base):
    """Organization/company profile."""
    __tablename__ = "organizations"
    __table_args__ = {"schema": "aureon"}
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(500))
    duns_number: Mapped[Optional[str]] = mapped_column(String(13), unique=True)
    uei: Mapped[Optional[str]] = mapped_column(String(12), unique=True)
    cage_code: Mapped[Optional[str]] = mapped_column(String(10))
    ein: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Classification codes
    naics_codes: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    psc_codes: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    set_aside_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    
    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    zip_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(100), default="USA")
    
    # Company details
    website: Mapped[Optional[str]] = mapped_column(String(500))
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    annual_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    founded_year: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Narratives
    capabilities_narrative: Mapped[Optional[str]] = mapped_column(Text)
    past_performance_summary: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, name="metadata")
    
    # Relationships
    relevance_scores: Mapped[List["RelevanceScore"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    risk_assessments: Mapped[List["RiskAssessment"]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class Opportunity(Base):
    """Procurement opportunity."""
    __tablename__ = "opportunities"
    __table_args__ = (
        UniqueConstraint("source_id", "source_system", name="uq_opportunity_source"),
        {"schema": "aureon"}
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False, default="sam.gov")
    
    # Basic info
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    notice_type: Mapped[Optional[str]] = mapped_column(String(100))
    solicitation_number: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Classification
    naics_code: Mapped[Optional[str]] = mapped_column(String(10))
    naics_description: Mapped[Optional[str]] = mapped_column(Text)
    psc_code: Mapped[Optional[str]] = mapped_column(String(20))
    psc_description: Mapped[Optional[str]] = mapped_column(Text)
    set_aside_type: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Dates
    response_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    posted_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    archive_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Contract details
    contract_type: Mapped[Optional[str]] = mapped_column(String(50))
    estimated_value_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    estimated_value_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    
    # Place of performance
    place_of_performance_city: Mapped[Optional[str]] = mapped_column(String(100))
    place_of_performance_state: Mapped[Optional[str]] = mapped_column(String(50))
    place_of_performance_zip: Mapped[Optional[str]] = mapped_column(String(20))
    place_of_performance_country: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Contracting office
    contracting_office_name: Mapped[Optional[str]] = mapped_column(String(500))
    contracting_office_address: Mapped[Optional[str]] = mapped_column(Text)
    contracting_officer_name: Mapped[Optional[str]] = mapped_column(String(200))
    contracting_officer_email: Mapped[Optional[str]] = mapped_column(String(255))
    contracting_officer_phone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Point of contact
    point_of_contact_name: Mapped[Optional[str]] = mapped_column(String(200))
    point_of_contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    point_of_contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Award info
    award_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    award_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    awardee_name: Mapped[Optional[str]] = mapped_column(String(500))
    awardee_uei: Mapped[Optional[str]] = mapped_column(String(12))
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")
    classification_code: Mapped[Optional[str]] = mapped_column(String(50))
    security_clearance_required: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Attachments and amendments
    attachments: Mapped[list] = mapped_column(JSONB, default=list)
    amendments: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Raw data and timestamps
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    relevance_scores: Mapped[List["RelevanceScore"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    risk_assessments: Mapped[List["RiskAssessment"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")


class RelevanceScore(Base):
    """Relevance score between organization and opportunity."""
    __tablename__ = "relevance_scores"
    __table_args__ = (
        UniqueConstraint("organization_id", "opportunity_id", name="uq_relevance_org_opp"),
        CheckConstraint("overall_score >= 0 AND overall_score <= 1", name="chk_overall_score"),
        {"schema": "aureon"}
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aureon.organizations.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aureon.opportunities.id", ondelete="CASCADE"), nullable=False
    )
    
    # Scores (0.0 to 1.0)
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    naics_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    semantic_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    geographic_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    size_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    past_performance_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    competition_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    
    # Metadata
    component_weights: Mapped[dict] = mapped_column(JSONB, default=dict)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0.0")
    
    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="relevance_scores")
    opportunity: Mapped["Opportunity"] = relationship(back_populates="relevance_scores")


class RiskAssessment(Base):
    """Risk assessment for organization-opportunity pair."""
    __tablename__ = "risk_assessments"
    __table_args__ = (
        UniqueConstraint("organization_id", "opportunity_id", name="uq_risk_org_opp"),
        CheckConstraint(
            "overall_risk_level IN ('low', 'medium', 'high', 'critical')",
            name="chk_risk_level"
        ),
        {"schema": "aureon"}
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aureon.organizations.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aureon.opportunities.id", ondelete="CASCADE"), nullable=False
    )
    
    # Overall assessment
    overall_risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    overall_risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    
    # Risk categories (JSONB with score, level, factors)
    eligibility_risk: Mapped[dict] = mapped_column(JSONB, default=dict)
    technical_risk: Mapped[dict] = mapped_column(JSONB, default=dict)
    pricing_risk: Mapped[dict] = mapped_column(JSONB, default=dict)
    resource_risk: Mapped[dict] = mapped_column(JSONB, default=dict)
    compliance_risk: Mapped[dict] = mapped_column(JSONB, default=dict)
    timeline_risk: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Details
    risk_factors: Mapped[list] = mapped_column(JSONB, default=list)
    mitigation_suggestions: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Metadata
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0.0")
    
    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="risk_assessments")
    opportunity: Mapped["Opportunity"] = relationship(back_populates="risk_assessments")


class IngestionLog(Base):
    """Log of data ingestion runs."""
    __tablename__ = "ingestion_logs"
    __table_args__ = {"schema": "ingestion"}
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_system: Mapped[str] = mapped_column(String(50), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="running")
    records_fetched: Mapped[int] = mapped_column(Integer, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    extra_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, name="metadata")

