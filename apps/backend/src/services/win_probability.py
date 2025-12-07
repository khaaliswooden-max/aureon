"""
Win Probability Prediction Service

AI-powered opportunity scoring for federal contracts based on:
- Past performance similarity
- NAICS/PSC match to core capabilities
- Set-aside eligibility
- Geographic presence
- Agency relationship history
- Competition analysis
- Price competitiveness indicators
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal

from src.database.models import Organization, Opportunity


@dataclass
class WinProbabilityResult:
    """Result of win probability calculation."""
    opportunity_id: str
    win_probability: float
    match_score: float
    factors: Dict[str, float]
    recommendation: str
    confidence: float
    analysis: Dict[str, str]


class WinProbabilityModel:
    """
    AI model to predict win probability for federal opportunities.
    
    Factors considered:
    - Past performance on similar contracts
    - NAICS/PSC match to core capabilities
    - Set-aside eligibility
    - Geographic presence
    - Agency relationship history
    - Competition analysis
    - Price competitiveness
    """
    
    # Factor weights for win probability calculation
    FACTOR_WEIGHTS = {
        "capability_match": 0.20,
        "setaside_eligibility": 0.20,
        "past_performance": 0.20,
        "agency_relationship": 0.15,
        "geographic_fit": 0.10,
        "competition_level": 0.10,
        "pricing_position": 0.05,
    }
    
    # Set-aside type compatibility mapping
    SET_ASIDE_ELIGIBLE = {
        "SB": ["SB", "SDB", "8A", "WOSB", "EDWOSB", "HUBZone", "VOSB", "SDVOSB"],
        "8A": ["8A", "8(A)"],
        "8(A)": ["8A", "8(A)"],
        "WOSB": ["WOSB", "EDWOSB"],
        "EDWOSB": ["EDWOSB"],
        "SDVOSB": ["SDVOSB", "VOSB"],
        "VOSB": ["VOSB", "SDVOSB"],
        "HUBZone": ["HUBZone"],
        "HUBZONE": ["HUBZone", "HUBZONE"],
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize model with optional custom weights."""
        self.weights = weights or self.FACTOR_WEIGHTS
    
    async def calculate_win_probability(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> WinProbabilityResult:
        """
        Calculate win probability for an organization-opportunity pair.
        
        Args:
            organization: The organization profile
            opportunity: The procurement opportunity
            
        Returns:
            WinProbabilityResult with probability, factors, and recommendation
        """
        factors = {}
        analysis = {}
        
        # 1. Capability match (NAICS/PSC alignment)
        cap_score, cap_analysis = self._score_capability_match(organization, opportunity)
        factors['capability_match'] = cap_score
        analysis['capability_match'] = cap_analysis
        
        # 2. Set-aside eligibility
        setaside_score, setaside_analysis = self._score_setaside_eligibility(organization, opportunity)
        factors['setaside_eligibility'] = setaside_score
        analysis['setaside_eligibility'] = setaside_analysis
        
        # 3. Past performance
        pp_score, pp_analysis = self._score_past_performance(organization, opportunity)
        factors['past_performance'] = pp_score
        analysis['past_performance'] = pp_analysis
        
        # 4. Agency relationship
        agency_score, agency_analysis = self._score_agency_relationship(organization, opportunity)
        factors['agency_relationship'] = agency_score
        analysis['agency_relationship'] = agency_analysis
        
        # 5. Geographic fit
        geo_score, geo_analysis = self._score_geographic_fit(organization, opportunity)
        factors['geographic_fit'] = geo_score
        analysis['geographic_fit'] = geo_analysis
        
        # 6. Competition level
        comp_score, comp_analysis = self._score_competition_level(opportunity)
        factors['competition_level'] = comp_score
        analysis['competition_level'] = comp_analysis
        
        # 7. Pricing position
        pricing_score, pricing_analysis = self._score_pricing_position(organization, opportunity)
        factors['pricing_position'] = pricing_score
        analysis['pricing_position'] = pricing_analysis
        
        # Calculate weighted win probability
        win_probability = sum(
            factors[k] * self.weights[k] for k in factors
        )
        
        # Calculate match score (simpler capability + eligibility score)
        match_score = (factors['capability_match'] + factors['setaside_eligibility']) / 2
        
        # Generate recommendation
        recommendation = self._generate_recommendation(win_probability, factors)
        
        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(organization, opportunity, factors)
        
        return WinProbabilityResult(
            opportunity_id=str(opportunity.id),
            win_probability=round(win_probability, 4),
            match_score=round(match_score, 4),
            factors=factors,
            recommendation=recommendation,
            confidence=round(confidence, 4),
            analysis=analysis,
        )
    
    def _score_capability_match(
        self, 
        organization: Organization, 
        opportunity: Opportunity
    ) -> tuple[float, str]:
        """Score alignment with organization capabilities."""
        score = 0.0
        reasons = []
        
        # NAICS match
        if opportunity.naics_code and organization.naics_codes:
            opp_naics = opportunity.naics_code.strip()
            
            for org_naics in organization.naics_codes:
                org_naics = org_naics.strip()
                
                # Calculate matching prefix length
                match_length = 0
                for i, (c1, c2) in enumerate(zip(opp_naics, org_naics)):
                    if c1 == c2:
                        match_length = i + 1
                    else:
                        break
                
                if match_length >= 6:
                    score = max(score, 1.0)
                    reasons.append(f"Exact NAICS {opp_naics} match")
                elif match_length >= 5:
                    score = max(score, 0.9)
                    reasons.append(f"Strong NAICS match (5-digit)")
                elif match_length >= 4:
                    score = max(score, 0.75)
                    reasons.append(f"Good NAICS match (4-digit)")
                elif match_length >= 3:
                    score = max(score, 0.5)
                    reasons.append(f"Partial NAICS match (3-digit)")
                elif match_length >= 2:
                    score = max(score, 0.25)
                    reasons.append(f"Related industry sector")
        
        # PSC code match bonus
        if opportunity.psc_code and organization.psc_codes:
            if opportunity.psc_code in organization.psc_codes:
                score = min(1.0, score + 0.15)
                reasons.append(f"PSC {opportunity.psc_code} match")
        
        # Keyword match in description
        if organization.capabilities_narrative and opportunity.description:
            keywords = self._extract_capability_keywords(organization.capabilities_narrative)
            desc_lower = (opportunity.description or "").lower()
            matches = sum(1 for kw in keywords if kw.lower() in desc_lower)
            if matches > 3:
                score = min(1.0, score + 0.1)
                reasons.append(f"Strong keyword alignment ({matches} matches)")
        
        analysis = "; ".join(reasons) if reasons else "Limited capability data for analysis"
        return round(score, 4), analysis
    
    def _score_setaside_eligibility(
        self, 
        organization: Organization, 
        opportunity: Opportunity
    ) -> tuple[float, str]:
        """Score set-aside eligibility."""
        if not opportunity.set_aside_type:
            return 0.6, "Full and open competition - no set-aside restrictions"
        
        opp_setaside = opportunity.set_aside_type.upper().strip()
        org_setasides = [s.upper().strip() for s in (organization.set_aside_types or [])]
        
        if not org_setasides:
            # Check if it's a small business set-aside
            if any(term in opp_setaside for term in ["SB", "SMALL"]):
                return 0.3, f"Set-aside type '{opportunity.set_aside_type}' - eligibility unknown"
            return 0.5, "No set-aside certifications on file"
        
        # Check direct eligibility
        eligible_types = self.SET_ASIDE_ELIGIBLE.get(opp_setaside, [opp_setaside])
        
        for eligible_type in eligible_types:
            if eligible_type in org_setasides:
                return 1.0, f"Eligible for {opportunity.set_aside_type} set-aside"
        
        return 0.1, f"Not eligible for {opportunity.set_aside_type} set-aside"
    
    def _score_past_performance(
        self, 
        organization: Organization, 
        opportunity: Opportunity
    ) -> tuple[float, str]:
        """Score past performance relevance."""
        if not organization.past_performance_summary:
            return 0.4, "No past performance summary on file"
        
        pp_summary = organization.past_performance_summary.lower()
        score = 0.4  # Base score for having PP
        reasons = []
        
        # Check NAICS relevance
        if opportunity.naics_code:
            naics_desc = (opportunity.naics_description or "").lower()
            if any(word in pp_summary for word in naics_desc.split()[:3] if len(word) > 3):
                score += 0.2
                reasons.append("Relevant industry experience")
        
        # Check agency experience
        if opportunity.contracting_office_name:
            office_words = opportunity.contracting_office_name.lower().split()[:2]
            if any(word in pp_summary for word in office_words if len(word) > 3):
                score += 0.2
                reasons.append("Agency experience")
        
        # Check contract type experience
        contract_keywords = {
            "ffp": ["fixed", "firm"],
            "t&m": ["time", "materials"],
            "cpff": ["cost", "plus"],
            "idiq": ["idiq", "task order"],
        }
        
        if opportunity.contract_type:
            ct = opportunity.contract_type.lower()
            for ct_type, keywords in contract_keywords.items():
                if ct_type in ct and any(kw in pp_summary for kw in keywords):
                    score += 0.15
                    reasons.append(f"{ct_type.upper()} contract experience")
                    break
        
        analysis = "; ".join(reasons) if reasons else "General past performance on file"
        return round(min(1.0, score), 4), analysis
    
    def _score_agency_relationship(
        self, 
        organization: Organization, 
        opportunity: Opportunity
    ) -> tuple[float, str]:
        """Score existing agency relationships."""
        if not opportunity.contracting_office_name:
            return 0.5, "Contracting office not specified"
        
        if not organization.past_performance_summary:
            return 0.3, "No agency relationship history available"
        
        office = opportunity.contracting_office_name.lower()
        pp = organization.past_performance_summary.lower()
        
        # Check for agency name mentions
        agency_keywords = {
            "dod": ["defense", "army", "navy", "air force", "marine", "pentagon"],
            "va": ["veterans", "va ", "vha", "vba"],
            "dhs": ["homeland", "fema", "tsa", "ice", "cbp"],
            "hhs": ["health", "human services", "cdc", "fda", "nih"],
            "gsa": ["gsa", "federal acquisition", "public building"],
            "doj": ["justice", "fbi", "dea", "atf", "marshal"],
            "treasury": ["treasury", "irs", "mint"],
        }
        
        score = 0.3  # Base score
        reasons = []
        
        for agency, keywords in agency_keywords.items():
            if any(kw in office for kw in keywords):
                if any(kw in pp for kw in keywords):
                    score = 0.8
                    reasons.append(f"Prior {agency.upper()} experience")
                    break
        
        # Generic relationship indicator
        if not reasons and len(pp) > 100:
            score = 0.5
            reasons.append("General federal contracting experience")
        
        analysis = "; ".join(reasons) if reasons else "No direct agency relationship identified"
        return round(score, 4), analysis
    
    def _score_geographic_fit(
        self, 
        organization: Organization, 
        opportunity: Opportunity
    ) -> tuple[float, str]:
        """Score geographic alignment."""
        org_state = (organization.state or "").upper()
        opp_state = (opportunity.place_of_performance_state or "").upper()
        
        if not org_state or not opp_state:
            return 0.6, "Geographic location not specified"
        
        # Exact match
        if org_state == opp_state:
            return 1.0, f"Located in {opp_state}"
        
        # DC metro area special case
        dc_metro = {"DC", "VA", "MD"}
        if org_state in dc_metro and opp_state in dc_metro:
            return 0.9, "DC metro area presence"
        
        # Adjacent state check
        adjacent_states = {
            "VA": ["DC", "MD", "WV", "NC", "TN", "KY"],
            "MD": ["DC", "VA", "WV", "PA", "DE"],
            "DC": ["VA", "MD"],
            "CA": ["OR", "NV", "AZ"],
            "TX": ["NM", "OK", "AR", "LA"],
            "FL": ["GA", "AL"],
            "NY": ["NJ", "CT", "PA", "VT", "MA"],
            "IL": ["WI", "IN", "MO", "IA", "KY"],
        }
        
        if org_state in adjacent_states and opp_state in adjacent_states.get(org_state, []):
            return 0.75, f"Adjacent to {opp_state}"
        
        # Remote work check
        if opportunity.description:
            desc_lower = opportunity.description.lower()
            if "remote" in desc_lower or "telework" in desc_lower:
                return 0.8, "Remote/telework eligible"
        
        return 0.4, f"Located in {org_state}, opportunity in {opp_state}"
    
    def _score_competition_level(self, opportunity: Opportunity) -> tuple[float, str]:
        """Score based on competition level indicators."""
        if not opportunity.notice_type:
            return 0.5, "Competition level unknown"
        
        notice = opportunity.notice_type.lower()
        
        if "sole source" in notice or "j&a" in notice:
            return 0.2, "Sole source - pre-selected vendor likely"
        
        if "sources sought" in notice or "rfi" in notice:
            return 0.7, "Market research phase - early opportunity"
        
        if "presolicitation" in notice:
            return 0.6, "Presolicitation - good time for positioning"
        
        if "combined" in notice or "solicitation" in notice:
            return 0.5, "Active solicitation - competitive"
        
        if "award" in notice:
            return 0.1, "Award notice - opportunity closed"
        
        return 0.5, "Standard competition expected"
    
    def _score_pricing_position(
        self, 
        organization: Organization, 
        opportunity: Opportunity
    ) -> tuple[float, str]:
        """Score pricing position and capacity."""
        if not opportunity.estimated_value_max or not organization.annual_revenue:
            return 0.6, "Contract value or revenue data unavailable"
        
        ratio = float(opportunity.estimated_value_max) / float(organization.annual_revenue)
        
        if ratio < 0.1:
            return 0.9, f"Contract size ({ratio:.1%} of revenue) - very manageable"
        elif ratio < 0.3:
            return 1.0, f"Ideal contract size ({ratio:.1%} of revenue)"
        elif ratio < 0.5:
            return 0.85, f"Good fit ({ratio:.1%} of revenue)"
        elif ratio < 1.0:
            return 0.6, f"Stretch opportunity ({ratio:.1%} of revenue)"
        elif ratio < 2.0:
            return 0.4, f"Significant commitment ({ratio:.1%} of revenue)"
        else:
            return 0.2, f"Contract may exceed capacity ({ratio:.1%} of revenue)"
    
    def _generate_recommendation(self, win_prob: float, factors: Dict[str, float]) -> str:
        """Generate pursuit recommendation based on win probability."""
        if win_prob >= 0.70:
            return "STRONG PURSUE - High probability opportunity aligned with capabilities"
        elif win_prob >= 0.55:
            return "PURSUE - Good fit, develop strong differentiators"
        elif win_prob >= 0.40:
            return "EVALUATE - Consider teaming or targeted pursuit"
        elif win_prob >= 0.25:
            return "SELECTIVE - Only pursue if strategically important"
        else:
            return "MONITOR ONLY - Low probability, preserve bid resources"
    
    def _calculate_confidence(
        self,
        organization: Organization,
        opportunity: Opportunity,
        factors: Dict[str, float],
    ) -> float:
        """Calculate confidence in the prediction based on data completeness."""
        confidence = 0.5  # Base confidence
        
        # Organization data completeness
        if organization.naics_codes:
            confidence += 0.1
        if organization.past_performance_summary:
            confidence += 0.1
        if organization.set_aside_types:
            confidence += 0.05
        if organization.annual_revenue:
            confidence += 0.05
        
        # Opportunity data completeness
        if opportunity.naics_code:
            confidence += 0.05
        if opportunity.description and len(opportunity.description) > 100:
            confidence += 0.05
        if opportunity.estimated_value_max:
            confidence += 0.05
        
        # Higher confidence when factors have clear signals
        extreme_factors = sum(1 for v in factors.values() if v > 0.8 or v < 0.2)
        confidence += extreme_factors * 0.02
        
        return min(0.95, confidence)
    
    def _extract_capability_keywords(self, text: str) -> List[str]:
        """Extract meaningful capability keywords from text."""
        import re
        
        text = text.lower()
        words = re.findall(r'\b[a-z]{4,}\b', text)
        
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
            'had', 'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been',
            'will', 'with', 'this', 'that', 'from', 'they', 'which', 'their',
            'would', 'there', 'could', 'other', 'into', 'more', 'some', 'such',
            'than', 'them', 'then', 'these', 'only', 'over', 'also', 'after',
            'services', 'service', 'shall', 'must', 'provide', 'including',
            'company', 'organization', 'team', 'experience', 'years'
        }
        
        keywords = [w for w in words if w not in stop_words]
        return list(set(keywords))[:50]  # Return unique keywords, limited

