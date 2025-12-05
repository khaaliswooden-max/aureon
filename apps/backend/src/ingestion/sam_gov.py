"""
SAM.gov Opportunities API Ingestion

Fetches procurement opportunities from SAM.gov's public API
and stores them in the Aureon database.

API Documentation: https://open.gsa.gov/api/sam-api/
"""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import structlog

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Opportunity

logger = structlog.get_logger()


class SAMGovIngester:
    """
    Ingests opportunities from SAM.gov's public API.
    
    Supports filtering by:
    - NAICS codes
    - Posted date range
    - Notice types
    - Set-aside types
    """
    
    BASE_URL = "https://api.sam.gov/opportunities/v2/search"
    
    # SAM.gov notice types
    NOTICE_TYPES = {
        "o": "Solicitation",
        "p": "Presolicitation",
        "k": "Combined Synopsis/Solicitation",
        "r": "Sources Sought",
        "g": "Sale of Surplus Property",
        "s": "Special Notice",
        "i": "Intent to Bundle Requirements",
        "a": "Award Notice",
        "u": "Justification and Approval",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
        timeout: int = 30,
    ):
        """
        Initialize SAM.gov ingester.
        
        Args:
            api_key: SAM.gov API key (required for production use)
            db_session: Database session for storing opportunities
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.db_session = db_session
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def ingest(
        self,
        naics_codes: Optional[List[str]] = None,
        posted_from: Optional[str] = None,
        posted_to: Optional[str] = None,
        notice_types: Optional[List[str]] = None,
        set_aside_codes: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, int]:
        """
        Ingest opportunities from SAM.gov.
        
        Args:
            naics_codes: Filter by NAICS codes
            posted_from: Start date (MM/DD/YYYY format)
            posted_to: End date (MM/DD/YYYY format)
            notice_types: Filter by notice types
            set_aside_codes: Filter by set-aside types
            limit: Maximum records to fetch
            
        Returns:
            Dictionary with ingestion statistics
        """
        logger.info(
            "Starting SAM.gov ingestion",
            naics_codes=naics_codes,
            posted_from=posted_from,
            limit=limit,
        )
        
        stats = {
            "fetched": 0,
            "inserted": 0,
            "updated": 0,
            "failed": 0,
        }
        
        # Set default date range (last 30 days)
        if not posted_from:
            from_date = datetime.now(timezone.utc) - timedelta(days=30)
            posted_from = from_date.strftime("%m/%d/%Y")
        
        if not posted_to:
            posted_to = datetime.now(timezone.utc).strftime("%m/%d/%Y")
        
        # Build API parameters
        params = {
            "api_key": self.api_key,
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "limit": min(limit, 1000),  # API max is 1000
            "offset": 0,
        }
        
        if naics_codes:
            params["ncode"] = ",".join(naics_codes)
        
        if notice_types:
            params["ptype"] = ",".join(notice_types)
        
        if set_aside_codes:
            params["typeOfSetAside"] = ",".join(set_aside_codes)
        
        try:
            # Fetch opportunities
            opportunities = await self._fetch_opportunities(params)
            stats["fetched"] = len(opportunities)
            
            # Store in database
            if self.db_session and opportunities:
                for opp_data in opportunities:
                    try:
                        result = await self._store_opportunity(opp_data)
                        if result == "inserted":
                            stats["inserted"] += 1
                        elif result == "updated":
                            stats["updated"] += 1
                    except Exception as e:
                        logger.warning(
                            "Failed to store opportunity",
                            notice_id=opp_data.get("noticeId"),
                            error=str(e),
                        )
                        stats["failed"] += 1
                
                await self.db_session.commit()
            
            logger.info("SAM.gov ingestion complete", **stats)
            
        except Exception as e:
            logger.error("SAM.gov ingestion failed", error=str(e))
            raise
        
        return stats
    
    async def _fetch_opportunities(self, params: Dict[str, Any]) -> List[Dict]:
        """Fetch opportunities from SAM.gov API."""
        if not self.api_key:
            logger.warning("No SAM.gov API key configured, returning sample data")
            return self._get_sample_opportunities()
        
        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            opportunities = data.get("opportunitiesData", [])
            
            logger.debug(
                "Fetched opportunities from SAM.gov",
                count=len(opportunities),
                total=data.get("totalRecords", 0),
            )
            
            return opportunities
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "SAM.gov API error",
                status_code=e.response.status_code,
                detail=e.response.text[:500],
            )
            raise
        except Exception as e:
            logger.error("Failed to fetch from SAM.gov", error=str(e))
            raise
    
    async def _store_opportunity(self, data: Dict[str, Any]) -> str:
        """
        Store or update an opportunity in the database.
        
        Returns:
            "inserted" or "updated"
        """
        source_id = data.get("noticeId", "")
        
        # Check if exists
        stmt = select(Opportunity).where(
            Opportunity.source_id == source_id,
            Opportunity.source_system == "sam.gov",
        )
        result = await self.db_session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        # Parse opportunity data
        opp_dict = self._parse_opportunity(data)
        
        if existing:
            # Update existing
            for key, value in opp_dict.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.now(timezone.utc)
            return "updated"
        else:
            # Insert new
            opportunity = Opportunity(**opp_dict)
            self.db_session.add(opportunity)
            return "inserted"
    
    def _parse_opportunity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse SAM.gov API response into Opportunity model format."""
        # Parse dates
        def parse_date(date_str: Optional[str]) -> Optional[datetime]:
            if not date_str:
                return None
            try:
                # SAM.gov uses various date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        return datetime.strptime(date_str[:19], fmt).replace(
                            tzinfo=timezone.utc
                        )
                    except ValueError:
                        continue
                return None
            except Exception:
                return None
        
        # Extract place of performance
        pop = data.get("placeOfPerformance", {}) or {}
        pop_city = pop.get("city", {}) or {}
        pop_state = pop.get("state", {}) or {}
        
        # Extract point of contact
        poc = data.get("pointOfContact", [])
        primary_poc = poc[0] if poc else {}
        
        # Extract office info
        office = data.get("office", {}) or {}
        
        return {
            "source_id": data.get("noticeId", ""),
            "source_system": "sam.gov",
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "notice_type": self.NOTICE_TYPES.get(
                data.get("type", ""), data.get("type", "")
            ),
            "solicitation_number": data.get("solicitationNumber", ""),
            "naics_code": data.get("naicsCode", ""),
            "naics_description": data.get("naicsDescription", ""),
            "psc_code": data.get("classificationCode", ""),
            "psc_description": "",
            "set_aside_type": data.get("typeOfSetAsideDescription", ""),
            "response_deadline": parse_date(data.get("responseDeadLine")),
            "posted_date": parse_date(data.get("postedDate")),
            "archive_date": parse_date(data.get("archiveDate")),
            "contract_type": data.get("contractType", ""),
            "estimated_value_min": None,
            "estimated_value_max": None,
            "place_of_performance_city": pop_city.get("name", ""),
            "place_of_performance_state": pop_state.get("code", ""),
            "place_of_performance_zip": pop.get("zip", ""),
            "place_of_performance_country": pop.get("country", {}).get("code", "USA"),
            "contracting_office_name": office.get("name", ""),
            "contracting_office_address": "",
            "point_of_contact_name": primary_poc.get("fullName", ""),
            "point_of_contact_email": primary_poc.get("email", ""),
            "point_of_contact_phone": primary_poc.get("phone", ""),
            "status": "active",
            "raw_data": data,
            "ingested_at": datetime.now(timezone.utc),
        }
    
    def _get_sample_opportunities(self) -> List[Dict]:
        """Return sample opportunities for testing without API key."""
        return [
            {
                "noticeId": "SAMPLE-001",
                "title": "Cloud Migration Services for Federal Agency",
                "description": "Professional services for migrating legacy systems to cloud infrastructure. Includes assessment, planning, migration, and ongoing support.",
                "type": "k",
                "solicitationNumber": "SOL-2025-001",
                "naicsCode": "541512",
                "naicsDescription": "Computer Systems Design Services",
                "typeOfSetAsideDescription": "Small Business Set-Aside",
                "postedDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "responseDeadLine": (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d"),
                "placeOfPerformance": {
                    "city": {"name": "Washington"},
                    "state": {"code": "DC"},
                },
                "office": {"name": "Department of Example"},
                "pointOfContact": [
                    {
                        "fullName": "Jane Smith",
                        "email": "jane.smith@example.gov",
                        "phone": "202-555-0100",
                    }
                ],
            },
            {
                "noticeId": "SAMPLE-002",
                "title": "Cybersecurity Assessment and Monitoring",
                "description": "Comprehensive cybersecurity services including vulnerability assessments, penetration testing, and continuous monitoring.",
                "type": "o",
                "solicitationNumber": "RFP-2025-002",
                "naicsCode": "541519",
                "naicsDescription": "Other Computer Related Services",
                "typeOfSetAsideDescription": "8(a) Set-Aside",
                "postedDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "responseDeadLine": (datetime.now(timezone.utc) + timedelta(days=45)).strftime("%Y-%m-%d"),
                "placeOfPerformance": {
                    "city": {"name": "Arlington"},
                    "state": {"code": "VA"},
                },
                "office": {"name": "Defense Information Systems Agency"},
                "pointOfContact": [
                    {
                        "fullName": "John Doe",
                        "email": "john.doe@example.gov",
                        "phone": "703-555-0200",
                    }
                ],
            },
            {
                "noticeId": "SAMPLE-003",
                "title": "Environmental Remediation Services",
                "description": "Environmental consulting and remediation services for contaminated site cleanup.",
                "type": "p",
                "solicitationNumber": "PRE-2025-003",
                "naicsCode": "562910",
                "naicsDescription": "Remediation Services",
                "typeOfSetAsideDescription": "Women-Owned Small Business Set-Aside",
                "postedDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "responseDeadLine": (datetime.now(timezone.utc) + timedelta(days=60)).strftime("%Y-%m-%d"),
                "placeOfPerformance": {
                    "city": {"name": "Denver"},
                    "state": {"code": "CO"},
                },
                "office": {"name": "Environmental Protection Agency"},
                "pointOfContact": [
                    {
                        "fullName": "Mary Johnson",
                        "email": "mary.johnson@example.gov",
                        "phone": "303-555-0300",
                    }
                ],
            },
        ]

