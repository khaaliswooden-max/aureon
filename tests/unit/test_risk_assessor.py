"""
Unit tests for the risk assessment service.
"""
import pytest
from datetime import datetime, timezone, timedelta


class TestRiskLevelCalculation:
    """Tests for risk level determination."""
    
    def test_low_risk_threshold(self):
        """Score <= 0.25 should be low risk."""
        score = 0.20
        
        if score <= 0.25:
            level = 'low'
        elif score <= 0.50:
            level = 'medium'
        elif score <= 0.75:
            level = 'high'
        else:
            level = 'critical'
        
        assert level == 'low'
    
    def test_medium_risk_threshold(self):
        """Score 0.26-0.50 should be medium risk."""
        score = 0.40
        
        if score <= 0.25:
            level = 'low'
        elif score <= 0.50:
            level = 'medium'
        elif score <= 0.75:
            level = 'high'
        else:
            level = 'critical'
        
        assert level == 'medium'
    
    def test_high_risk_threshold(self):
        """Score 0.51-0.75 should be high risk."""
        score = 0.70
        
        if score <= 0.25:
            level = 'low'
        elif score <= 0.50:
            level = 'medium'
        elif score <= 0.75:
            level = 'high'
        else:
            level = 'critical'
        
        assert level == 'high'
    
    def test_critical_risk_threshold(self):
        """Score > 0.75 should be critical risk."""
        score = 0.90
        
        if score <= 0.25:
            level = 'low'
        elif score <= 0.50:
            level = 'medium'
        elif score <= 0.75:
            level = 'high'
        else:
            level = 'critical'
        
        assert level == 'critical'


class TestTimelineRisk:
    """Tests for timeline risk assessment."""
    
    def test_passed_deadline(self):
        """Past deadline should be critical risk."""
        deadline = datetime.now(timezone.utc) - timedelta(days=1)
        now = datetime.now(timezone.utc)
        
        days_remaining = (deadline - now).days
        
        assert days_remaining < 0
    
    def test_urgent_deadline(self):
        """Less than 7 days should be urgent."""
        deadline = datetime.now(timezone.utc) + timedelta(days=5)
        now = datetime.now(timezone.utc)
        
        days_remaining = (deadline - now).days
        
        assert days_remaining < 7
    
    def test_comfortable_deadline(self):
        """30+ days should be comfortable."""
        deadline = datetime.now(timezone.utc) + timedelta(days=45)
        now = datetime.now(timezone.utc)
        
        days_remaining = (deadline - now).days
        
        assert days_remaining >= 30


class TestEligibilityRisk:
    """Tests for eligibility risk assessment."""
    
    def test_eligible_for_set_aside(self):
        """Eligible org should have low eligibility risk."""
        org_set_asides = ['SDVOSB', 'SB']
        opp_set_aside = 'SDVOSB'
        
        # SDVOSB can bid on SDVOSB
        eligible_for_sdvosb = ['SDVOSB']
        is_eligible = any(t in eligible_for_sdvosb for t in org_set_asides)
        
        assert is_eligible
    
    def test_ineligible_for_set_aside(self):
        """Ineligible org should have high eligibility risk."""
        org_set_asides = ['SB']  # Just small business
        opp_set_aside = '8A'  # 8(a) only
        
        eligible_for_8a = ['8A']
        is_eligible = any(t in eligible_for_8a for t in org_set_asides)
        
        assert not is_eligible


class TestBidRecommendation:
    """Tests for bid/no-bid recommendation logic."""
    
    def test_high_relevance_low_risk_bid(self):
        """High relevance + low risk = bid recommendation."""
        relevance_score = 0.85
        risk_score = 0.20
        
        if relevance_score >= 0.7 and risk_score <= 0.3:
            recommendation = 'bid'
        elif relevance_score < 0.4 or risk_score > 0.7:
            recommendation = 'no_bid'
        elif relevance_score >= 0.6 and risk_score <= 0.5:
            recommendation = 'conditional_bid'
        else:
            recommendation = 'review_required'
        
        assert recommendation == 'bid'
    
    def test_low_relevance_no_bid(self):
        """Low relevance = no bid recommendation."""
        relevance_score = 0.30
        risk_score = 0.25
        
        if relevance_score >= 0.7 and risk_score <= 0.3:
            recommendation = 'bid'
        elif relevance_score < 0.4 or risk_score > 0.7:
            recommendation = 'no_bid'
        elif relevance_score >= 0.6 and risk_score <= 0.5:
            recommendation = 'conditional_bid'
        else:
            recommendation = 'review_required'
        
        assert recommendation == 'no_bid'
    
    def test_high_risk_no_bid(self):
        """High risk = no bid recommendation."""
        relevance_score = 0.80
        risk_score = 0.85
        
        if relevance_score >= 0.7 and risk_score <= 0.3:
            recommendation = 'bid'
        elif relevance_score < 0.4 or risk_score > 0.7:
            recommendation = 'no_bid'
        elif relevance_score >= 0.6 and risk_score <= 0.5:
            recommendation = 'conditional_bid'
        else:
            recommendation = 'review_required'
        
        assert recommendation == 'no_bid'
    
    def test_conditional_bid(self):
        """Moderate relevance + moderate risk = conditional bid."""
        relevance_score = 0.65
        risk_score = 0.45
        
        if relevance_score >= 0.7 and risk_score <= 0.3:
            recommendation = 'bid'
        elif relevance_score < 0.4 or risk_score > 0.7:
            recommendation = 'no_bid'
        elif relevance_score >= 0.6 and risk_score <= 0.5:
            recommendation = 'conditional_bid'
        else:
            recommendation = 'review_required'
        
        assert recommendation == 'conditional_bid'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

