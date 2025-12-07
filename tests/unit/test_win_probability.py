"""Unit tests for Win Probability Model."""
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend'))

import pytest
from unittest.mock import MagicMock
from decimal import Decimal

from src.services.win_probability import WinProbabilityModel


class TestWinProbabilityFactors:
    """Tests for individual win probability factors."""
    
    @pytest.fixture
    def model(self):
        return WinProbabilityModel()
    
    @pytest.fixture
    def mock_organization(self):
        org = MagicMock()
        org.id = "test-org-id"
        org.name = "Test Company"
        org.naics_codes = ["541512", "541519"]
        org.psc_codes = ["D302", "D306"]
        org.set_aside_types = ["SB", "SDVOSB"]
        org.state = "VA"
        org.annual_revenue = Decimal("5000000")
        org.capabilities_narrative = "Cloud computing, software development, cybersecurity"
        org.past_performance_summary = "Successfully delivered DoD software contracts"
        return org
    
    @pytest.fixture
    def mock_opportunity(self):
        opp = MagicMock()
        opp.id = "test-opp-id"
        opp.title = "Cloud Migration Services"
        opp.description = "Cloud infrastructure migration and modernization"
        opp.naics_code = "541512"
        opp.naics_description = "Computer Systems Design Services"
        opp.psc_code = "D302"
        opp.set_aside_type = "Small Business"
        opp.place_of_performance_state = "VA"
        opp.contracting_office_name = "Department of Defense"
        opp.estimated_value_max = Decimal("1000000")
        opp.notice_type = "Solicitation"
        opp.contract_type = "FFP"
        return opp
    
    def test_exact_naics_match_high_score(self, model, mock_organization, mock_opportunity):
        """Test that exact NAICS match gives high capability score."""
        score, analysis = model._score_capability_match(mock_organization, mock_opportunity)
        assert score >= 0.8
        assert "NAICS" in analysis or "match" in analysis.lower()
    
    def test_no_naics_match_low_score(self, model, mock_organization, mock_opportunity):
        """Test that no NAICS match gives low capability score."""
        mock_organization.naics_codes = ["336411"]  # Different sector
        score, _ = model._score_capability_match(mock_organization, mock_opportunity)
        assert score <= 0.5
    
    def test_eligible_setaside_full_score(self, model, mock_organization, mock_opportunity):
        """Test that eligible set-aside gives full score."""
        # Set the set-aside type to match org's certifications
        mock_opportunity.set_aside_type = "SDVOSB"  # Org has SDVOSB
        score, analysis = model._score_setaside_eligibility(mock_organization, mock_opportunity)
        assert score >= 0.9  # Should be fully eligible
    
    def test_ineligible_setaside_low_score(self, model, mock_organization, mock_opportunity):
        """Test that ineligible set-aside gives low score."""
        mock_opportunity.set_aside_type = "8(a)"
        mock_organization.set_aside_types = ["SB"]  # SB not eligible for 8(a)
        score, _ = model._score_setaside_eligibility(mock_organization, mock_opportunity)
        assert score <= 0.3
    
    def test_full_open_competition_neutral_score(self, model, mock_organization, mock_opportunity):
        """Test that full and open competition gives neutral score."""
        mock_opportunity.set_aside_type = None
        score, analysis = model._score_setaside_eligibility(mock_organization, mock_opportunity)
        assert 0.5 <= score <= 0.7
        assert "open" in analysis.lower() or "no set-aside" in analysis.lower()
    
    def test_same_state_high_geographic_score(self, model, mock_organization, mock_opportunity):
        """Test that same state gives high geographic score."""
        score, analysis = model._score_geographic_fit(mock_organization, mock_opportunity)
        assert score == 1.0
        assert "VA" in analysis
    
    def test_dc_metro_high_geographic_score(self, model, mock_organization, mock_opportunity):
        """Test that DC metro area gets high score."""
        mock_organization.state = "MD"
        mock_opportunity.place_of_performance_state = "DC"
        score, analysis = model._score_geographic_fit(mock_organization, mock_opportunity)
        assert score >= 0.8
        assert "metro" in analysis.lower()
    
    def test_different_state_lower_score(self, model, mock_organization, mock_opportunity):
        """Test that different state gives lower score."""
        mock_organization.state = "TX"
        mock_opportunity.place_of_performance_state = "WA"
        score, _ = model._score_geographic_fit(mock_organization, mock_opportunity)
        assert score <= 0.5
    
    def test_ideal_contract_size_high_pricing_score(self, model, mock_organization, mock_opportunity):
        """Test that ideal contract size gives high pricing score."""
        # Contract is 20% of revenue - ideal range
        score, analysis = model._score_pricing_position(mock_organization, mock_opportunity)
        assert score >= 0.8
    
    def test_oversized_contract_low_pricing_score(self, model, mock_organization, mock_opportunity):
        """Test that oversized contract gives low pricing score."""
        mock_opportunity.estimated_value_max = Decimal("15000000")  # 3x revenue
        score, analysis = model._score_pricing_position(mock_organization, mock_opportunity)
        assert score <= 0.4
        assert "capacity" in analysis.lower()


class TestWinRecommendations:
    """Tests for win probability recommendations."""
    
    @pytest.fixture
    def model(self):
        return WinProbabilityModel()
    
    def test_strong_pursue_high_probability(self, model):
        """Test that high probability generates strong pursue recommendation."""
        recommendation = model._generate_recommendation(0.75, {})
        assert "STRONG PURSUE" in recommendation
    
    def test_pursue_moderate_probability(self, model):
        """Test that moderate probability generates pursue recommendation."""
        recommendation = model._generate_recommendation(0.55, {})
        assert "PURSUE" in recommendation
    
    def test_evaluate_lower_probability(self, model):
        """Test that lower probability generates evaluate recommendation."""
        recommendation = model._generate_recommendation(0.42, {})
        assert "EVALUATE" in recommendation or "SELECTIVE" in recommendation
    
    def test_monitor_low_probability(self, model):
        """Test that low probability generates monitor recommendation."""
        recommendation = model._generate_recommendation(0.20, {})
        assert "MONITOR" in recommendation
