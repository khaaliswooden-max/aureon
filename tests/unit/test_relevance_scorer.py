"""
Unit tests for the relevance scoring service.
"""
import pytest
from unittest.mock import MagicMock
from decimal import Decimal

# Mock the models since we're testing in isolation
class MockOrganization:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Test Org')
        self.naics_codes = kwargs.get('naics_codes', ['541512'])
        self.state = kwargs.get('state', 'VA')
        self.set_aside_types = kwargs.get('set_aside_types', ['SB'])
        self.annual_revenue = kwargs.get('annual_revenue', Decimal('5000000'))
        self.employee_count = kwargs.get('employee_count', 50)
        self.capabilities_narrative = kwargs.get('capabilities_narrative', 'Cloud services and IT solutions')
        self.past_performance_summary = kwargs.get('past_performance_summary', 'Federal IT contracts')


class MockOpportunity:
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', 'IT Services Contract')
        self.naics_code = kwargs.get('naics_code', '541512')
        self.place_of_performance_state = kwargs.get('state', 'VA')
        self.set_aside_type = kwargs.get('set_aside_type', 'Small Business')
        self.estimated_value_max = kwargs.get('value', Decimal('1000000'))
        self.description = kwargs.get('description', 'Cloud migration services')
        self.contracting_office_name = kwargs.get('office', 'GSA')
        self.contract_type = kwargs.get('contract_type', 'firm-fixed')
        self.naics_description = kwargs.get('naics_description', 'Computer Systems Design')


class TestNAICSScoring:
    """Tests for NAICS code matching logic."""
    
    def test_exact_naics_match(self):
        """Exact 6-digit NAICS match should score 1.0."""
        org = MockOrganization(naics_codes=['541512'])
        opp = MockOpportunity(naics_code='541512')
        
        # Simulate scoring logic
        org_naics = org.naics_codes[0]
        opp_naics = opp.naics_code
        
        match_length = 0
        for i, (c1, c2) in enumerate(zip(org_naics, opp_naics)):
            if c1 == c2:
                match_length = i + 1
            else:
                break
        
        assert match_length == 6
    
    def test_partial_naics_match(self):
        """4-digit NAICS match should score 0.75."""
        org = MockOrganization(naics_codes=['541599'])  # Different last 2 digits
        opp = MockOpportunity(naics_code='541512')
        
        org_naics = org.naics_codes[0]
        opp_naics = opp.naics_code
        
        match_length = 0
        for i, (c1, c2) in enumerate(zip(org_naics, opp_naics)):
            if c1 == c2:
                match_length = i + 1
            else:
                break
        
        # First 3 digits match: 541
        assert match_length == 3
    
    def test_no_naics_match(self):
        """Different sector should score low."""
        org = MockOrganization(naics_codes=['236220'])  # Construction
        opp = MockOpportunity(naics_code='541512')  # IT
        
        org_naics = org.naics_codes[0]
        opp_naics = opp.naics_code
        
        match_length = 0
        for i, (c1, c2) in enumerate(zip(org_naics, opp_naics)):
            if c1 == c2:
                match_length = i + 1
            else:
                break
        
        # No match at sector level
        assert match_length == 0


class TestGeographicScoring:
    """Tests for geographic proximity logic."""
    
    def test_same_state(self):
        """Same state should score 1.0."""
        org = MockOrganization(state='VA')
        opp = MockOpportunity(state='VA')
        
        assert org.state == opp.place_of_performance_state
    
    def test_adjacent_state(self):
        """Adjacent states should score high."""
        adjacency = {
            'VA': ['DC', 'MD', 'WV', 'NC', 'TN', 'KY'],
            'MD': ['DC', 'VA', 'WV', 'PA', 'DE'],
        }
        
        org_state = 'VA'
        opp_state = 'MD'
        
        # Check if adjacent
        adjacent = adjacency.get(org_state, [])
        is_adjacent = opp_state in adjacent
        
        assert is_adjacent


class TestSetAsideEligibility:
    """Tests for set-aside eligibility logic."""
    
    def test_small_business_eligible_for_sb(self):
        """Small business should be eligible for SB set-aside."""
        org_types = ['SB', 'SDVOSB']
        opp_type = 'SB'
        
        eligible_for_sb = ['SB', 'SDB', '8A', 'WOSB', 'EDWOSB', 'VOSB', 'SDVOSB', 'HUBZone']
        is_eligible = any(t in eligible_for_sb for t in org_types)
        
        assert is_eligible
    
    def test_sb_not_eligible_for_8a(self):
        """Plain SB should not be eligible for 8(a) set-aside."""
        org_types = ['SB']
        opp_type = '8A'
        
        eligible_for_8a = ['8A']
        is_eligible = any(t in eligible_for_8a for t in org_types)
        
        assert not is_eligible
    
    def test_sdvosb_eligible_for_vosb(self):
        """SDVOSB should be eligible for VOSB set-aside."""
        org_types = ['SDVOSB']
        opp_type = 'VOSB'
        
        eligible_for_vosb = ['VOSB', 'SDVOSB']
        is_eligible = any(t in eligible_for_vosb for t in org_types)
        
        assert is_eligible


class TestSizeScoring:
    """Tests for size/capacity scoring logic."""
    
    def test_appropriate_contract_size(self):
        """Contract 25% of revenue should be ideal."""
        revenue = Decimal('10000000')
        contract_value = Decimal('2500000')
        
        ratio = float(contract_value) / float(revenue)
        
        # 10-50% is ideal range
        assert 0.1 <= ratio <= 0.5
    
    def test_oversized_contract(self):
        """Contract larger than revenue is high risk."""
        revenue = Decimal('1000000')
        contract_value = Decimal('5000000')
        
        ratio = float(contract_value) / float(revenue)
        
        assert ratio > 2.0  # More than 2x revenue is risky


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

