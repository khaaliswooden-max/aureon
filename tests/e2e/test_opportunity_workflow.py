"""
End-to-end tests for the opportunity discovery and scoring workflow.
"""
import pytest
import httpx
from typing import Optional

# Test configuration
API_BASE_URL = "http://localhost:8000"


class TestAPIHealth:
    """Test API availability."""
    
    @pytest.fixture
    def client(self):
        """HTTP client for API requests."""
        return httpx.Client(base_url=API_BASE_URL, timeout=10.0)
    
    def test_health_endpoint(self, client):
        """API health endpoint should return healthy status."""
        try:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded"]
        except httpx.ConnectError:
            pytest.skip("API not running - skipping e2e tests")
    
    def test_root_endpoint(self, client):
        """Root endpoint should return API info."""
        try:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "version" in data
        except httpx.ConnectError:
            pytest.skip("API not running - skipping e2e tests")


class TestOpportunityEndpoints:
    """Test opportunity CRUD operations."""
    
    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=API_BASE_URL, timeout=10.0)
    
    def test_list_opportunities(self, client):
        """Should list opportunities with pagination."""
        try:
            response = client.get("/opportunities", params={"page_size": 10})
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data
        except httpx.ConnectError:
            pytest.skip("API not running")
    
    def test_filter_by_naics(self, client):
        """Should filter opportunities by NAICS code."""
        try:
            response = client.get("/opportunities", params={
                "naics_code": "541512",
                "page_size": 10
            })
            assert response.status_code == 200
        except httpx.ConnectError:
            pytest.skip("API not running")
    
    def test_filter_by_set_aside(self, client):
        """Should filter opportunities by set-aside type."""
        try:
            response = client.get("/opportunities", params={
                "set_aside_type": "Small Business",
                "page_size": 10
            })
            assert response.status_code == 200
        except httpx.ConnectError:
            pytest.skip("API not running")


class TestOrganizationEndpoints:
    """Test organization CRUD operations."""
    
    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=API_BASE_URL, timeout=10.0)
    
    def test_list_organizations(self, client):
        """Should list organizations."""
        try:
            response = client.get("/organizations")
            assert response.status_code == 200
            assert isinstance(response.json(), list)
        except httpx.ConnectError:
            pytest.skip("API not running")
    
    def test_create_organization(self, client):
        """Should create a new organization."""
        try:
            org_data = {
                "name": "Test Organization",
                "naics_codes": ["541512"],
                "city": "Arlington",
                "state": "VA",
                "set_aside_types": ["SB"]
            }
            response = client.post("/organizations", json=org_data)
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Organization"
            assert "id" in data
            
            # Cleanup
            org_id = data["id"]
            client.delete(f"/organizations/{org_id}")
        except httpx.ConnectError:
            pytest.skip("API not running")


class TestScoringWorkflow:
    """Test the scoring workflow."""
    
    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=API_BASE_URL, timeout=30.0)
    
    def test_relevance_scoring(self, client):
        """Should calculate relevance score for org-opp pair."""
        try:
            # Get an organization
            orgs = client.get("/organizations").json()
            if not orgs:
                pytest.skip("No organizations in database")
            org_id = orgs[0]["id"]
            
            # Get an opportunity
            opps = client.get("/opportunities", params={"page_size": 1}).json()
            if not opps.get("items"):
                pytest.skip("No opportunities in database")
            opp_id = opps["items"][0]["id"]
            
            # Calculate score
            response = client.post("/scoring/calculate", json={
                "organization_id": org_id,
                "opportunity_id": opp_id
            })
            
            assert response.status_code == 200
            score = response.json()
            assert "overallScore" in score or "overall_score" in score
            
        except httpx.ConnectError:
            pytest.skip("API not running")


class TestRiskAssessment:
    """Test risk assessment workflow."""
    
    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=API_BASE_URL, timeout=30.0)
    
    def test_risk_assessment(self, client):
        """Should assess risk for org-opp pair."""
        try:
            # Get an organization
            orgs = client.get("/organizations").json()
            if not orgs:
                pytest.skip("No organizations in database")
            org_id = orgs[0]["id"]
            
            # Get an opportunity
            opps = client.get("/opportunities", params={"page_size": 1}).json()
            if not opps.get("items"):
                pytest.skip("No opportunities in database")
            opp_id = opps["items"][0]["id"]
            
            # Assess risk
            response = client.post("/risk/assess", json={
                "organization_id": org_id,
                "opportunity_id": opp_id
            })
            
            assert response.status_code == 200
            risk = response.json()
            assert "overallRiskLevel" in risk or "overall_risk_level" in risk
            
        except httpx.ConnectError:
            pytest.skip("API not running")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

