"""
Aureon Core Domain - Python Package

Provides domain models and types for the Aureon procurement substrate.
"""

from aureon_domain.entities import (
    Organization,
    Opportunity,
    RelevanceScore,
    RiskAssessment,
)
from aureon_domain.types import (
    SetAsideType,
    RiskLevel,
    NoticeType,
    ContractType,
    OrganizationStatus,
    OpportunityStatus,
)

__version__ = "0.1.0"
__all__ = [
    "Organization",
    "Opportunity",
    "RelevanceScore",
    "RiskAssessment",
    "SetAsideType",
    "RiskLevel",
    "NoticeType",
    "ContractType",
    "OrganizationStatus",
    "OpportunityStatus",
]

