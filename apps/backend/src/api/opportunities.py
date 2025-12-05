"""Opportunities API endpoints."""
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import Opportunity
from src.api.schemas import (
    OpportunityCreate, OpportunityResponse, OpportunitySearchParams,
    OpportunityListResponse
)

router = APIRouter()


@router.get("", response_model=OpportunityListResponse)
async def list_opportunities(
    query: Optional[str] = None,
    naics_code: Optional[str] = None,
    set_aside_type: Optional[str] = None,
    state: Optional[str] = None,
    notice_type: Optional[str] = None,
    posted_after: Optional[datetime] = None,
    deadline_after: Optional[datetime] = None,
    status: str = "active",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "posted_date",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
) -> OpportunityListResponse:
    """
    List and search procurement opportunities.
    
    Supports filtering by:
    - Free text search (title, description)
    - NAICS code
    - Set-aside type
    - State (place of performance)
    - Notice type
    - Posted date range
    - Response deadline
    - Status
    """
    # Build query
    stmt = select(Opportunity)
    
    # Apply filters
    conditions = []
    
    if status:
        conditions.append(Opportunity.status == status)
    
    if query:
        search_term = f"%{query}%"
        conditions.append(
            or_(
                Opportunity.title.ilike(search_term),
                Opportunity.description.ilike(search_term),
                Opportunity.solicitation_number.ilike(search_term)
            )
        )
    
    if naics_code:
        conditions.append(Opportunity.naics_code == naics_code)
    
    if set_aside_type:
        conditions.append(Opportunity.set_aside_type == set_aside_type)
    
    if state:
        conditions.append(Opportunity.place_of_performance_state == state)
    
    if notice_type:
        conditions.append(Opportunity.notice_type == notice_type)
    
    if posted_after:
        conditions.append(Opportunity.posted_date >= posted_after)
    
    if deadline_after:
        conditions.append(Opportunity.response_deadline >= deadline_after)
    
    if conditions:
        stmt = stmt.where(and_(*conditions))
    
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # Apply sorting
    sort_column = getattr(Opportunity, sort_by, Opportunity.posted_date)
    if sort_order == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(stmt)
    opportunities = result.scalars().all()
    
    return OpportunityListResponse(
        items=[OpportunityResponse.model_validate(opp) for opp in opportunities],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> OpportunityResponse:
    """Get a specific opportunity by ID."""
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    result = await db.execute(stmt)
    opportunity = result.scalar_one_or_none()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return OpportunityResponse.model_validate(opportunity)


@router.post("", response_model=OpportunityResponse, status_code=201)
async def create_opportunity(
    data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
) -> OpportunityResponse:
    """Create a new opportunity (manual entry)."""
    opportunity = Opportunity(**data.model_dump())
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return OpportunityResponse.model_validate(opportunity)


@router.get("/naics/{naics_code}", response_model=OpportunityListResponse)
async def get_opportunities_by_naics(
    naics_code: str,
    status: str = "active",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> OpportunityListResponse:
    """Get opportunities filtered by NAICS code."""
    # Handle 2-digit to 6-digit NAICS matching
    stmt = select(Opportunity).where(
        and_(
            Opportunity.naics_code.startswith(naics_code),
            Opportunity.status == status
        )
    ).order_by(Opportunity.posted_date.desc())
    
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    opportunities = result.scalars().all()
    
    return OpportunityListResponse(
        items=[OpportunityResponse.model_validate(opp) for opp in opportunities],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/stats/summary")
async def get_opportunity_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get summary statistics for opportunities."""
    # Total active opportunities
    active_count = await db.execute(
        select(func.count()).where(Opportunity.status == "active")
    )
    
    # Opportunities by notice type
    notice_type_stmt = select(
        Opportunity.notice_type,
        func.count().label("count")
    ).where(
        Opportunity.status == "active"
    ).group_by(Opportunity.notice_type)
    
    notice_types_result = await db.execute(notice_type_stmt)
    
    # Opportunities by set-aside type
    set_aside_stmt = select(
        Opportunity.set_aside_type,
        func.count().label("count")
    ).where(
        Opportunity.status == "active"
    ).group_by(Opportunity.set_aside_type)
    
    set_asides_result = await db.execute(set_aside_stmt)
    
    return {
        "total_active": active_count.scalar() or 0,
        "by_notice_type": {
            row.notice_type or "unspecified": row.count 
            for row in notice_types_result
        },
        "by_set_aside": {
            row.set_aside_type or "unrestricted": row.count 
            for row in set_asides_result
        }
    }

