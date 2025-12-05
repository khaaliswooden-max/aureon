"""
Risk Assessment Service

Provides comprehensive risk assessment for bid/no-bid decisions:
- Eligibility risk (set-asides, clearances, certifications)
- Technical risk (capability gaps, technology requirements)
- Pricing risk (competitive positioning, cost estimation)
- Resource risk (staffing, availability, capacity)
- Compliance risk (FAR/DFARS, regulatory requirements)
- Timeline risk (response preparation, performance period)
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from src.database.models import Organization, Opportunity


@dataclass
class RiskCategory:
    """Individual risk category assessment."""
    level: str  # low, medium, high, critical
    score: float  # 0.0 to 1.0 (higher = more risk)
    factors: List[str] = field(default_factory=list)


@dataclass
class RiskAssessmentResult:
    """Complete risk assessment result."""
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


class RiskAssessor:
    """
    Comprehensive risk assessment engine for bid/no-bid decisions.
    
    Evaluates multiple risk dimensions and provides actionable
    mitigation recommendations.
    """
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        "low": 0.25,
        "medium": 0.5,
        "high": 0.75,
        "critical": 1.0,
    }
    
    # Category weights for overall score
    CATEGORY_WEIGHTS = {
        "eligibility": 0.25,
        "technical": 0.20,
        "pricing": 0.15,
        "resource": 0.15,
        "compliance": 0.15,
        "timeline": 0.10,
    }
    
    def __init__(self):
        """Initialize risk assessor."""
        pass
    
    async def assess_risk(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> RiskAssessmentResult:
        """
        Perform comprehensive risk assessment.
        
        Args:
            organization: The organization profile
            opportunity: The procurement opportunity
            
        Returns:
            RiskAssessmentResult with all category assessments
        """
        # Assess each risk category
        eligibility_risk = self._assess_eligibility_risk(organization, opportunity)
        technical_risk = self._assess_technical_risk(organization, opportunity)
        pricing_risk = self._assess_pricing_risk(organization, opportunity)
        resource_risk = self._assess_resource_risk(organization, opportunity)
        compliance_risk = self._assess_compliance_risk(organization, opportunity)
        timeline_risk = self._assess_timeline_risk(organization, opportunity)
        
        # Calculate overall risk score
        overall_score = (
            eligibility_risk.score * self.CATEGORY_WEIGHTS["eligibility"] +
            technical_risk.score * self.CATEGORY_WEIGHTS["technical"] +
            pricing_risk.score * self.CATEGORY_WEIGHTS["pricing"] +
            resource_risk.score * self.CATEGORY_WEIGHTS["resource"] +
            compliance_risk.score * self.CATEGORY_WEIGHTS["compliance"] +
            timeline_risk.score * self.CATEGORY_WEIGHTS["timeline"]
        )
        
        # Determine overall risk level
        overall_level = self._score_to_level(overall_score)
        
        # Collect all risk factors
        all_factors = []
        for cat in [eligibility_risk, technical_risk, pricing_risk, 
                    resource_risk, compliance_risk, timeline_risk]:
            all_factors.extend(cat.factors)
        
        # Generate mitigation suggestions
        mitigations = self._generate_mitigations(
            eligibility_risk, technical_risk, pricing_risk,
            resource_risk, compliance_risk, timeline_risk
        )
        
        return RiskAssessmentResult(
            overall_risk_level=overall_level,
            overall_risk_score=round(overall_score, 4),
            eligibility_risk=eligibility_risk,
            technical_risk=technical_risk,
            pricing_risk=pricing_risk,
            resource_risk=resource_risk,
            compliance_risk=compliance_risk,
            timeline_risk=timeline_risk,
            risk_factors=all_factors,
            mitigation_suggestions=mitigations,
        )
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to risk level."""
        if score <= self.RISK_THRESHOLDS["low"]:
            return "low"
        elif score <= self.RISK_THRESHOLDS["medium"]:
            return "medium"
        elif score <= self.RISK_THRESHOLDS["high"]:
            return "high"
        else:
            return "critical"
    
    def _assess_eligibility_risk(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> RiskCategory:
        """
        Assess eligibility-related risks.
        
        Checks:
        - Set-aside qualification
        - Security clearance requirements
        - Certification requirements
        - Registration status
        """
        factors = []
        risk_score = 0.0
        
        # Check set-aside eligibility
        if opportunity.set_aside_type:
            opp_setaside = opportunity.set_aside_type.upper()
            org_setasides = [s.upper() for s in (organization.set_aside_types or [])]
            
            setaside_map = {
                "SDVOSB": ["SDVOSB"],
                "VOSB": ["VOSB", "SDVOSB"],
                "8(A)": ["8A", "8(A)"],
                "8A": ["8A", "8(A)"],
                "WOSB": ["WOSB", "EDWOSB"],
                "EDWOSB": ["EDWOSB"],
                "HUBZONE": ["HUBZONE"],
                "SDB": ["SDB", "8A", "8(A)"],
                "SB": ["SB", "SDB", "8A", "WOSB", "SDVOSB", "HUBZONE"],
            }
            
            eligible_types = setaside_map.get(opp_setaside, [opp_setaside])
            
            if not any(t in org_setasides for t in eligible_types):
                factors.append(f"Not eligible for {opp_setaside} set-aside")
                risk_score += 0.8  # Critical issue
        
        # Check security clearance
        if opportunity.security_clearance_required:
            clearance = opportunity.security_clearance_required.lower()
            if "secret" in clearance or "top secret" in clearance or "ts/sci" in clearance:
                # Would check organization's clearance status
                factors.append(f"Requires {opportunity.security_clearance_required} clearance")
                risk_score += 0.4  # Significant barrier if not held
        
        # Check registration (UEI/SAM)
        if not organization.uei:
            factors.append("No UEI on file - SAM.gov registration may be needed")
            risk_score += 0.3
        
        # Normalize score
        risk_score = min(1.0, risk_score)
        
        return RiskCategory(
            level=self._score_to_level(risk_score),
            score=risk_score,
            factors=factors,
        )
    
    def _assess_technical_risk(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> RiskCategory:
        """
        Assess technical capability risks.
        
        Checks:
        - NAICS alignment
        - PSC code matching
        - Capability narrative gaps
        """
        factors = []
        risk_score = 0.0
        
        # Check NAICS alignment
        if opportunity.naics_code and organization.naics_codes:
            opp_naics = opportunity.naics_code[:4]  # Check at 4-digit level
            matching = any(
                n.startswith(opp_naics[:2]) for n in organization.naics_codes
            )
            if not matching:
                factors.append(f"NAICS {opportunity.naics_code} outside core competencies")
                risk_score += 0.5
            elif not any(n.startswith(opp_naics) for n in organization.naics_codes):
                factors.append(f"NAICS {opportunity.naics_code} is adjacent to core codes")
                risk_score += 0.2
        
        # Check PSC code matching
        if opportunity.psc_code and organization.psc_codes:
            matching_psc = any(
                p.startswith(opportunity.psc_code[:2]) 
                for p in organization.psc_codes
            )
            if not matching_psc:
                factors.append(f"PSC {opportunity.psc_code} may require new capabilities")
                risk_score += 0.3
        
        # Check capabilities narrative completeness
        if not organization.capabilities_narrative:
            factors.append("No capabilities narrative on file for evaluation")
            risk_score += 0.2
        
        risk_score = min(1.0, risk_score)
        
        return RiskCategory(
            level=self._score_to_level(risk_score),
            score=risk_score,
            factors=factors,
        )
    
    def _assess_pricing_risk(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> RiskCategory:
        """
        Assess pricing and competitive risks.
        
        Checks:
        - Contract value vs organization size
        - Competition level indicators
        - Contract type complexity
        """
        factors = []
        risk_score = 0.0
        
        # Check contract value relative to organization
        if opportunity.estimated_value_max and organization.annual_revenue:
            ratio = float(opportunity.estimated_value_max) / float(organization.annual_revenue)
            
            if ratio > 2.0:
                factors.append(f"Contract value ({ratio:.1f}x revenue) may exceed capacity")
                risk_score += 0.6
            elif ratio > 1.0:
                factors.append(f"Contract value is {ratio:.1f}x annual revenue - significant commitment")
                risk_score += 0.3
        
        # Check contract type complexity
        if opportunity.contract_type:
            ct = opportunity.contract_type.lower()
            if "cost" in ct or "cpff" in ct or "cpaf" in ct:
                factors.append("Cost-reimbursement contract requires robust accounting systems")
                risk_score += 0.2
        
        # Check if multiple award expected (competition indicator)
        if opportunity.notice_type:
            nt = opportunity.notice_type.lower()
            if "sole source" in nt or "j&a" in nt:
                # Lower competition risk but limited opportunity
                pass
            elif "sources sought" in nt:
                factors.append("Early stage - competition level unknown")
                risk_score += 0.1
        
        risk_score = min(1.0, risk_score)
        
        return RiskCategory(
            level=self._score_to_level(risk_score),
            score=risk_score,
            factors=factors,
        )
    
    def _assess_resource_risk(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> RiskCategory:
        """
        Assess resource availability risks.
        
        Checks:
        - Employee count relative to likely staffing needs
        - Geographic presence
        """
        factors = []
        risk_score = 0.0
        
        # Check staffing capacity
        if organization.employee_count:
            emp_count = organization.employee_count
            
            # Rough estimate: $150K revenue per employee
            if opportunity.estimated_value_max:
                implied_staff = float(opportunity.estimated_value_max) / 150000
                
                if implied_staff > emp_count * 0.5:
                    factors.append(f"May require ~{implied_staff:.0f} staff ({emp_count} current employees)")
                    risk_score += 0.4
                elif implied_staff > emp_count * 0.3:
                    factors.append("Significant staffing effort required")
                    risk_score += 0.2
        
        # Check geographic presence
        if opportunity.place_of_performance_state:
            opp_state = opportunity.place_of_performance_state.upper()
            org_state = (organization.state or "").upper()
            
            if opp_state and org_state and opp_state != org_state:
                factors.append(f"Performance in {opp_state} (org based in {org_state})")
                risk_score += 0.2
        
        risk_score = min(1.0, risk_score)
        
        return RiskCategory(
            level=self._score_to_level(risk_score),
            score=risk_score,
            factors=factors,
        )
    
    def _assess_compliance_risk(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> RiskCategory:
        """
        Assess regulatory compliance risks.
        
        Checks:
        - FAR clause implications
        - Industry-specific requirements
        - Reporting requirements
        """
        factors = []
        risk_score = 0.0
        
        # Check for defense-related requirements
        if opportunity.contracting_office_name:
            office = opportunity.contracting_office_name.lower()
            
            if any(term in office for term in ["defense", "army", "navy", "air force", "dod"]):
                factors.append("DoD contract - DFARS compliance required")
                risk_score += 0.2
        
        # Check NAICS for regulated industries
        if opportunity.naics_code:
            naics = opportunity.naics_code[:3]
            
            regulated_sectors = {
                "541": "Professional services - may require specific certifications",
                "336": "Defense manufacturing - ITAR/EAR may apply",
                "562": "Environmental - EPA compliance required",
                "622": "Healthcare - HIPAA compliance required",
            }
            
            for sector, note in regulated_sectors.items():
                if naics.startswith(sector):
                    factors.append(note)
                    risk_score += 0.15
                    break
        
        # Check security requirements
        if opportunity.security_clearance_required:
            factors.append("Facility clearance and security protocols required")
            risk_score += 0.2
        
        risk_score = min(1.0, risk_score)
        
        return RiskCategory(
            level=self._score_to_level(risk_score),
            score=risk_score,
            factors=factors,
        )
    
    def _assess_timeline_risk(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> RiskCategory:
        """
        Assess timeline-related risks.
        
        Checks:
        - Response deadline proximity
        - Preparation time needed
        """
        factors = []
        risk_score = 0.0
        
        if opportunity.response_deadline:
            now = datetime.now(timezone.utc)
            deadline = opportunity.response_deadline
            
            # Make deadline timezone-aware if needed
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            
            days_remaining = (deadline - now).days
            
            if days_remaining < 0:
                factors.append("Response deadline has passed")
                risk_score = 1.0
            elif days_remaining < 7:
                factors.append(f"Only {days_remaining} days until deadline - urgent")
                risk_score += 0.7
            elif days_remaining < 14:
                factors.append(f"{days_remaining} days until deadline - tight timeline")
                risk_score += 0.4
            elif days_remaining < 30:
                factors.append(f"{days_remaining} days until deadline - manageable")
                risk_score += 0.2
        else:
            factors.append("No response deadline specified")
            risk_score += 0.1
        
        risk_score = min(1.0, risk_score)
        
        return RiskCategory(
            level=self._score_to_level(risk_score),
            score=risk_score,
            factors=factors,
        )
    
    def _generate_mitigations(
        self,
        eligibility: RiskCategory,
        technical: RiskCategory,
        pricing: RiskCategory,
        resource: RiskCategory,
        compliance: RiskCategory,
        timeline: RiskCategory,
    ) -> List[str]:
        """Generate mitigation suggestions based on identified risks."""
        mitigations = []
        
        # Eligibility mitigations
        if eligibility.score >= 0.5:
            for factor in eligibility.factors:
                if "set-aside" in factor.lower():
                    mitigations.append("Consider teaming with an eligible prime contractor")
                if "clearance" in factor.lower():
                    mitigations.append("Initiate facility clearance process if not already in progress")
                if "uei" in factor.lower():
                    mitigations.append("Complete SAM.gov registration immediately")
        
        # Technical mitigations
        if technical.score >= 0.4:
            for factor in technical.factors:
                if "naics" in factor.lower():
                    mitigations.append("Document relevant past performance in adjacent NAICS codes")
                if "capabilities" in factor.lower():
                    mitigations.append("Update capability statement before submission")
        
        # Pricing mitigations
        if pricing.score >= 0.4:
            for factor in pricing.factors:
                if "capacity" in factor.lower() or "revenue" in factor.lower():
                    mitigations.append("Consider teaming or subcontracting to share risk")
                if "accounting" in factor.lower():
                    mitigations.append("Verify DCAA-compliant accounting system is in place")
        
        # Resource mitigations
        if resource.score >= 0.4:
            for factor in resource.factors:
                if "staff" in factor.lower():
                    mitigations.append("Identify key personnel and confirm availability")
                    mitigations.append("Develop recruitment pipeline for required positions")
                if "performance in" in factor.lower():
                    mitigations.append("Consider local subcontractor or satellite office")
        
        # Compliance mitigations
        if compliance.score >= 0.3:
            for factor in compliance.factors:
                if "dfars" in factor.lower():
                    mitigations.append("Review DFARS flowdown requirements with contracts team")
                if "hipaa" in factor.lower() or "itar" in factor.lower():
                    mitigations.append("Engage compliance officer for regulatory review")
        
        # Timeline mitigations
        if timeline.score >= 0.5:
            for factor in timeline.factors:
                if "urgent" in factor.lower() or "tight" in factor.lower():
                    mitigations.append("Assign dedicated proposal team immediately")
                    mitigations.append("Request extension if allowable under solicitation")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_mitigations = []
        for m in mitigations:
            if m not in seen:
                seen.add(m)
                unique_mitigations.append(m)
        
        return unique_mitigations[:10]  # Limit to top 10

