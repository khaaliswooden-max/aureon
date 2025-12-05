"""
Domain type definitions for Aureon.
"""
from enum import Enum


class SetAsideType(str, Enum):
    """Federal set-aside program types."""
    SB = "SB"           # Small Business
    SDB = "SDB"         # Small Disadvantaged Business
    EIGHT_A = "8A"      # 8(a) Program
    WOSB = "WOSB"       # Women-Owned Small Business
    EDWOSB = "EDWOSB"   # Economically Disadvantaged WOSB
    VOSB = "VOSB"       # Veteran-Owned Small Business
    SDVOSB = "SDVOSB"   # Service-Disabled VOSB
    HUBZONE = "HUBZone" # HUBZone
    ISBEE = "ISBEE"     # Indian Small Business
    NONE = "NONE"       # No set-aside


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NoticeType(str, Enum):
    """Procurement notice types."""
    PRESOLICITATION = "presolicitation"
    SOLICITATION = "solicitation"
    COMBINED_SYNOPSIS = "combined_synopsis"
    SOURCES_SOUGHT = "sources_sought"
    SPECIAL_NOTICE = "special_notice"
    AWARD_NOTICE = "award_notice"
    JUSTIFICATION = "justification"
    INTENT_TO_BUNDLE = "intent_to_bundle"
    MODIFICATION = "modification"
    CANCELLATION = "cancellation"
    OTHER = "other"


class ContractType(str, Enum):
    """Contract types."""
    FIRM_FIXED_PRICE = "firm_fixed_price"
    TIME_AND_MATERIALS = "time_and_materials"
    LABOR_HOUR = "labor_hour"
    COST_PLUS_FIXED_FEE = "cost_plus_fixed_fee"
    COST_PLUS_AWARD_FEE = "cost_plus_award_fee"
    COST_PLUS_INCENTIVE_FEE = "cost_plus_incentive_fee"
    FIXED_PRICE_INCENTIVE = "fixed_price_incentive"
    IDIQ = "idiq"
    BPA = "bpa"
    OTHER = "other"


class OrganizationStatus(str, Enum):
    """Organization operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class OpportunityStatus(str, Enum):
    """Opportunity lifecycle status."""
    FORECAST = "forecast"
    PRESOLICITATION = "presolicitation"
    ACTIVE = "active"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


# Set-aside eligibility mapping
SET_ASIDE_ELIGIBILITY = {
    SetAsideType.SB: [
        SetAsideType.SB, SetAsideType.SDB, SetAsideType.EIGHT_A,
        SetAsideType.WOSB, SetAsideType.EDWOSB, SetAsideType.VOSB,
        SetAsideType.SDVOSB, SetAsideType.HUBZONE
    ],
    SetAsideType.SDB: [SetAsideType.SDB, SetAsideType.EIGHT_A],
    SetAsideType.EIGHT_A: [SetAsideType.EIGHT_A],
    SetAsideType.WOSB: [SetAsideType.WOSB, SetAsideType.EDWOSB],
    SetAsideType.EDWOSB: [SetAsideType.EDWOSB],
    SetAsideType.VOSB: [SetAsideType.VOSB, SetAsideType.SDVOSB],
    SetAsideType.SDVOSB: [SetAsideType.SDVOSB],
    SetAsideType.HUBZONE: [SetAsideType.HUBZONE],
    SetAsideType.ISBEE: [SetAsideType.ISBEE],
    SetAsideType.NONE: [],
}


def is_eligible_for_set_aside(
    org_set_asides: list[SetAsideType],
    opp_set_aside: SetAsideType | None
) -> bool:
    """Check if organization qualifies for opportunity's set-aside."""
    if not opp_set_aside or opp_set_aside == SetAsideType.NONE:
        return True
    
    eligible_types = SET_ASIDE_ELIGIBILITY.get(opp_set_aside, [])
    return any(t in eligible_types for t in org_set_asides)


def get_risk_level(score: float) -> RiskLevel:
    """Convert numeric score to risk level."""
    if score <= 0.25:
        return RiskLevel.LOW
    elif score <= 0.50:
        return RiskLevel.MEDIUM
    elif score <= 0.75:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL

