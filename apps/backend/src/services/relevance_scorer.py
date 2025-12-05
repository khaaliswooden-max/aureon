"""
Relevance Scoring Service

Calculates relevance scores between organizations and opportunities
based on multiple factors:
- NAICS code matching (taxonomy alignment)
- Semantic similarity (capabilities vs requirements)
- Geographic proximity
- Size/capacity appropriateness
- Past performance indicators
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import re

from src.database.models import Organization, Opportunity
from src.config import get_settings

settings = get_settings()


@dataclass
class RelevanceScoreResult:
    """Result of relevance scoring calculation."""
    overall_score: float
    naics_score: float
    semantic_score: float
    geographic_score: float
    size_score: float
    past_performance_score: float
    component_weights: Dict[str, float]
    explanation: str


class RelevanceScorer:
    """
    Multi-factor relevance scoring engine.
    
    Combines multiple scoring dimensions to produce an overall
    relevance score between an organization and an opportunity.
    """
    
    # Default weights for score components
    DEFAULT_WEIGHTS = {
        "naics": 0.25,
        "semantic": 0.30,
        "geographic": 0.15,
        "size": 0.15,
        "past_performance": 0.15,
    }
    
    # State adjacency map for geographic scoring
    STATE_ADJACENCY = {
        "VA": ["DC", "MD", "WV", "NC", "TN", "KY"],
        "MD": ["DC", "VA", "WV", "PA", "DE"],
        "DC": ["VA", "MD"],
        "CA": ["OR", "NV", "AZ"],
        "TX": ["NM", "OK", "AR", "LA"],
        "FL": ["GA", "AL"],
        # Add more as needed
    }
    
    # Set-aside type compatibility
    SET_ASIDE_ELIGIBLE = {
        "SB": ["SB", "SDB", "8A", "WOSB", "EDWOSB", "HUBZone", "VOSB", "SDVOSB"],
        "8A": ["8A"],
        "WOSB": ["WOSB", "EDWOSB"],
        "EDWOSB": ["EDWOSB"],
        "SDVOSB": ["SDVOSB", "VOSB"],
        "VOSB": ["VOSB", "SDVOSB"],
        "HUBZone": ["HUBZone"],
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize scorer with optional custom weights."""
        self.weights = weights or self.DEFAULT_WEIGHTS
    
    async def calculate_score(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> RelevanceScoreResult:
        """
        Calculate overall relevance score between organization and opportunity.
        
        Args:
            organization: The organization profile
            opportunity: The procurement opportunity
            
        Returns:
            RelevanceScoreResult with all component scores and explanation
        """
        # Calculate individual component scores
        naics_score = self._calculate_naics_score(organization, opportunity)
        semantic_score = await self._calculate_semantic_score(organization, opportunity)
        geographic_score = self._calculate_geographic_score(organization, opportunity)
        size_score = self._calculate_size_score(organization, opportunity)
        past_performance_score = self._calculate_past_performance_score(organization, opportunity)
        
        # Calculate weighted overall score
        overall_score = (
            naics_score * self.weights["naics"] +
            semantic_score * self.weights["semantic"] +
            geographic_score * self.weights["geographic"] +
            size_score * self.weights["size"] +
            past_performance_score * self.weights["past_performance"]
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            organization, opportunity,
            naics_score, semantic_score, geographic_score, 
            size_score, past_performance_score, overall_score
        )
        
        return RelevanceScoreResult(
            overall_score=round(overall_score, 4),
            naics_score=round(naics_score, 4),
            semantic_score=round(semantic_score, 4),
            geographic_score=round(geographic_score, 4),
            size_score=round(size_score, 4),
            past_performance_score=round(past_performance_score, 4),
            component_weights=self.weights,
            explanation=explanation,
        )
    
    def _calculate_naics_score(
        self, 
        organization: Organization, 
        opportunity: Opportunity
    ) -> float:
        """
        Calculate NAICS code alignment score.
        
        Scoring logic:
        - Exact 6-digit match: 1.0
        - 5-digit match: 0.9
        - 4-digit match: 0.75
        - 3-digit match: 0.5
        - 2-digit match: 0.25
        - No match: 0.0
        """
        if not opportunity.naics_code or not organization.naics_codes:
            return 0.5  # Neutral when data unavailable
        
        opp_naics = opportunity.naics_code.strip()
        
        best_score = 0.0
        for org_naics in organization.naics_codes:
            org_naics = org_naics.strip()
            
            # Calculate matching prefix length
            match_length = 0
            for i, (c1, c2) in enumerate(zip(opp_naics, org_naics)):
                if c1 == c2:
                    match_length = i + 1
                else:
                    break
            
            # Score based on match length
            if match_length >= 6:
                score = 1.0
            elif match_length >= 5:
                score = 0.9
            elif match_length >= 4:
                score = 0.75
            elif match_length >= 3:
                score = 0.5
            elif match_length >= 2:
                score = 0.25
            else:
                score = 0.0
            
            best_score = max(best_score, score)
            
            if best_score == 1.0:
                break  # Can't do better
        
        return best_score
    
    async def _calculate_semantic_score(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> float:
        """
        Calculate semantic similarity between organization capabilities
        and opportunity requirements.
        
        Uses keyword overlap as a baseline. In production, would use
        embeddings (sentence-transformers) for true semantic matching.
        """
        # Get text to compare
        org_text = (organization.capabilities_narrative or "") + " " + \
                   (organization.past_performance_summary or "")
        opp_text = (opportunity.title or "") + " " + \
                   (opportunity.description or "")
        
        if not org_text.strip() or not opp_text.strip():
            return 0.5  # Neutral when no text
        
        # Tokenize and get keywords
        org_keywords = self._extract_keywords(org_text)
        opp_keywords = self._extract_keywords(opp_text)
        
        if not org_keywords or not opp_keywords:
            return 0.5
        
        # Calculate Jaccard similarity
        intersection = len(org_keywords & opp_keywords)
        union = len(org_keywords | opp_keywords)
        
        jaccard = intersection / union if union > 0 else 0
        
        # Scale to reasonable range (pure Jaccard is often low)
        # Typical good match might have 0.1-0.3 Jaccard
        scaled_score = min(1.0, jaccard * 5)
        
        return scaled_score
    
    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text."""
        # Lowercase and tokenize
        text = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
            'had', 'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been',
            'will', 'with', 'this', 'that', 'from', 'they', 'which', 'their',
            'would', 'there', 'could', 'other', 'into', 'more', 'some', 'such',
            'than', 'them', 'then', 'these', 'only', 'over', 'also', 'after',
            'services', 'service', 'shall', 'must', 'may', 'contractor'
        }
        
        keywords = {w for w in words if w not in stop_words}
        return keywords
    
    def _calculate_geographic_score(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> float:
        """
        Calculate geographic alignment score.
        
        Scoring:
        - Same state: 1.0
        - Adjacent state: 0.8
        - Same region: 0.5
        - National capability implied: 0.7
        - No location data: 0.5 (neutral)
        """
        org_state = organization.state
        opp_state = opportunity.place_of_performance_state
        
        if not org_state or not opp_state:
            return 0.6  # Slight positive for flexibility
        
        org_state = org_state.upper()
        opp_state = opp_state.upper()
        
        # Exact match
        if org_state == opp_state:
            return 1.0
        
        # Adjacent states
        adjacent = self.STATE_ADJACENCY.get(org_state, [])
        if opp_state in adjacent:
            return 0.8
        
        # Check reverse adjacency
        opp_adjacent = self.STATE_ADJACENCY.get(opp_state, [])
        if org_state in opp_adjacent:
            return 0.8
        
        # DC area gets special treatment (federal hub)
        dc_area = {"DC", "VA", "MD"}
        if org_state in dc_area or opp_state in dc_area:
            return 0.7
        
        # Default - different region
        return 0.4
    
    def _calculate_size_score(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> float:
        """
        Calculate size/capacity alignment score.
        
        Considers:
        - Set-aside eligibility
        - Employee count relative to contract size
        - Revenue relative to estimated value
        """
        score = 1.0
        factors = []
        
        # Check set-aside eligibility
        if opportunity.set_aside_type and organization.set_aside_types:
            opp_setaside = opportunity.set_aside_type.upper()
            org_setasides = [s.upper() for s in organization.set_aside_types]
            
            # Check if organization qualifies for this set-aside
            eligible_types = self.SET_ASIDE_ELIGIBLE.get(opp_setaside, [])
            
            if eligible_types:
                if any(t in org_setasides for t in eligible_types):
                    score = 1.0  # Eligible
                else:
                    score = 0.2  # Not eligible for set-aside
                    factors.append("set_aside_ineligible")
        
        # Check capacity based on contract value
        if opportunity.estimated_value_max and organization.annual_revenue:
            ratio = float(opportunity.estimated_value_max) / float(organization.annual_revenue)
            
            # Ideal: contract is 10-50% of annual revenue
            if ratio < 0.1:
                capacity_score = 0.95  # Very manageable
            elif ratio < 0.5:
                capacity_score = 1.0  # Ideal range
            elif ratio < 1.0:
                capacity_score = 0.8  # Stretch but doable
            elif ratio < 2.0:
                capacity_score = 0.5  # Significant stretch
            else:
                capacity_score = 0.2  # Likely too large
            
            score = min(score, capacity_score)
        
        return score
    
    def _calculate_past_performance_score(
        self,
        organization: Organization,
        opportunity: Opportunity,
    ) -> float:
        """
        Calculate past performance relevance score.
        
        In production, would query actual past performance records.
        For now, uses narrative analysis as proxy.
        """
        if not organization.past_performance_summary:
            return 0.5  # Neutral - no data
        
        pp_summary = organization.past_performance_summary.lower()
        
        # Check for relevant keywords from opportunity
        relevance_indicators = 0
        total_checks = 0
        
        # Check NAICS area
        if opportunity.naics_code:
            total_checks += 1
            naics_desc = (opportunity.naics_description or "").lower()
            if any(word in pp_summary for word in naics_desc.split()[:3]):
                relevance_indicators += 1
        
        # Check agency experience
        if opportunity.contracting_office_name:
            total_checks += 1
            office = opportunity.contracting_office_name.lower()
            if any(word in pp_summary for word in office.split()[:2]):
                relevance_indicators += 1
        
        # Check contract type experience
        contract_keywords = {
            "firm-fixed": ["fixed", "ffp"],
            "time-and-materials": ["time", "materials", "t&m"],
            "cost-plus": ["cost", "plus", "cpff", "cpaf"],
            "idiq": ["idiq", "indefinite", "delivery"],
        }
        
        if opportunity.contract_type:
            total_checks += 1
            ct = opportunity.contract_type.lower()
            for contract_type, keywords in contract_keywords.items():
                if ct in contract_type:
                    if any(kw in pp_summary for kw in keywords):
                        relevance_indicators += 1
                    break
        
        if total_checks == 0:
            return 0.6  # Slight positive for having PP
        
        return 0.4 + (0.6 * relevance_indicators / total_checks)
    
    def _generate_explanation(
        self,
        organization: Organization,
        opportunity: Opportunity,
        naics_score: float,
        semantic_score: float,
        geographic_score: float,
        size_score: float,
        past_performance_score: float,
        overall_score: float,
    ) -> str:
        """Generate human-readable explanation of the relevance score."""
        parts = []
        
        # Overall assessment
        if overall_score >= 0.8:
            parts.append("Strong alignment detected.")
        elif overall_score >= 0.6:
            parts.append("Moderate alignment with some gaps.")
        elif overall_score >= 0.4:
            parts.append("Limited alignment - review carefully.")
        else:
            parts.append("Weak alignment - likely not a good fit.")
        
        # Component analysis
        strengths = []
        weaknesses = []
        
        if naics_score >= 0.75:
            strengths.append(f"NAICS match ({naics_score:.0%})")
        elif naics_score < 0.5:
            weaknesses.append(f"NAICS mismatch ({naics_score:.0%})")
        
        if semantic_score >= 0.7:
            strengths.append(f"capabilities align well ({semantic_score:.0%})")
        elif semantic_score < 0.4:
            weaknesses.append(f"capabilities gap ({semantic_score:.0%})")
        
        if geographic_score >= 0.8:
            strengths.append("good geographic fit")
        elif geographic_score < 0.5:
            weaknesses.append("geographic distance")
        
        if size_score >= 0.9:
            strengths.append("appropriate size/eligibility")
        elif size_score < 0.5:
            weaknesses.append("size/eligibility concerns")
        
        if strengths:
            parts.append(f"Strengths: {', '.join(strengths)}.")
        
        if weaknesses:
            parts.append(f"Concerns: {', '.join(weaknesses)}.")
        
        return " ".join(parts)

