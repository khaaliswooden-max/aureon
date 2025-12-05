"""Organizations API endpoints."""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import Organization
from src.api.schemas import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse
)

router = APIRouter()


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    query: Optional[str] = None,
    naics_code: Optional[str] = None,
    state: Optional[str] = None,
    set_aside_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[OrganizationResponse]:
    """
    List and search organizations.
    
    Supports filtering by:
    - Free text search (name, capabilities)
    - NAICS codes
    - State
    - Set-aside types
    """
    stmt = select(Organization)
    
    if query:
        search_term = f"%{query}%"
        stmt = stmt.where(
            or_(
                Organization.name.ilike(search_term),
                Organization.legal_name.ilike(search_term),
                Organization.capabilities_narrative.ilike(search_term)
            )
        )
    
    if naics_code:
        stmt = stmt.where(Organization.naics_codes.contains([naics_code]))
    
    if state:
        stmt = stmt.where(Organization.state == state)
    
    if set_aside_type:
        stmt = stmt.where(Organization.set_aside_types.contains([set_aside_type]))
    
    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size).order_by(Organization.name)
    
    result = await db.execute(stmt)
    organizations = result.scalars().all()
    
    return [OrganizationResponse.model_validate(org) for org in organizations]


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    """Get a specific organization by ID."""
    stmt = select(Organization).where(Organization.id == organization_id)
    result = await db.execute(stmt)
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return OrganizationResponse.model_validate(organization)


@router.get("/uei/{uei}", response_model=OrganizationResponse)
async def get_organization_by_uei(
    uei: str,
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    """Get an organization by its Unique Entity Identifier (UEI)."""
    stmt = select(Organization).where(Organization.uei == uei)
    result = await db.execute(stmt)
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return OrganizationResponse.model_validate(organization)


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    """Create a new organization."""
    # Check for existing UEI
    if data.uei:
        existing = await db.execute(
            select(Organization).where(Organization.uei == data.uei)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400, 
                detail="Organization with this UEI already exists"
            )
    
    organization = Organization(**data.model_dump())
    db.add(organization)
    await db.commit()
    await db.refresh(organization)
    
    return OrganizationResponse.model_validate(organization)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: uuid.UUID,
    data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    """Update an organization."""
    stmt = select(Organization).where(Organization.id == organization_id)
    result = await db.execute(stmt)
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    await db.commit()
    await db.refresh(organization)
    
    return OrganizationResponse.model_validate(organization)


@router.delete("/{organization_id}", status_code=204)
async def delete_organization(
    organization_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an organization."""
    stmt = select(Organization).where(Organization.id == organization_id)
    result = await db.execute(stmt)
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    await db.delete(organization)
    await db.commit()


@router.get("/{organization_id}/naics-matches")
async def get_organization_naics_matches(
    organization_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get statistics about opportunities matching the organization's NAICS codes."""
    from src.database.models import Opportunity
    
    stmt = select(Organization).where(Organization.id == organization_id)
    result = await db.execute(stmt)
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if not organization.naics_codes:
        return {"matches": [], "total": 0}
    
    # Count opportunities per NAICS code
    matches = []
    for naics in organization.naics_codes:
        count_stmt = select(func.count()).where(
            Opportunity.naics_code.startswith(naics),
            Opportunity.status == "active"
        )
        count_result = await db.execute(count_stmt)
        count = count_result.scalar() or 0
        matches.append({"naics_code": naics, "opportunity_count": count})
    
    return {
        "organization_id": str(organization_id),
        "matches": matches,
        "total": sum(m["opportunity_count"] for m in matches)
    }

