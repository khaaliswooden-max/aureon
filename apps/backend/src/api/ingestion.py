"""Data Ingestion API endpoints."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import IngestionLog
from src.api.schemas import IngestionRequest, IngestionStatusResponse

router = APIRouter()


@router.post("/trigger", response_model=IngestionStatusResponse)
async def trigger_ingestion(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> IngestionStatusResponse:
    """
    Trigger a data ingestion job.
    
    Supported sources:
    - sam_gov: SAM.gov opportunities
    - grants_gov: Grants.gov opportunities (planned)
    - state_portal: State procurement portals (planned)
    """
    # Create ingestion log
    log = IngestionLog(
        source_system=request.source,
        status="queued",
        metadata=request.params or {},
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    
    # Queue background task
    if request.source == "sam_gov":
        background_tasks.add_task(
            run_sam_gov_ingestion,
            log.id,
            request.params or {}
        )
    else:
        # Update status for unsupported sources
        log.status = "failed"
        log.error_message = f"Source '{request.source}' is not yet implemented"
        log.completed_at = datetime.now(timezone.utc)
        await db.commit()
    
    return IngestionStatusResponse(
        id=log.id,
        source_system=log.source_system,
        status=log.status,
        started_at=log.started_at,
        completed_at=log.completed_at,
        records_fetched=log.records_fetched,
        records_inserted=log.records_inserted,
        records_updated=log.records_updated,
        records_failed=log.records_failed,
        error_message=log.error_message,
    )


@router.get("/status/{ingestion_id}", response_model=IngestionStatusResponse)
async def get_ingestion_status(
    ingestion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> IngestionStatusResponse:
    """Get the status of an ingestion job."""
    stmt = select(IngestionLog).where(IngestionLog.id == ingestion_id)
    result = await db.execute(stmt)
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Ingestion job not found")
    
    return IngestionStatusResponse(
        id=log.id,
        source_system=log.source_system,
        status=log.status,
        started_at=log.started_at,
        completed_at=log.completed_at,
        records_fetched=log.records_fetched,
        records_inserted=log.records_inserted,
        records_updated=log.records_updated,
        records_failed=log.records_failed,
        error_message=log.error_message,
    )


@router.get("/history")
async def get_ingestion_history(
    source: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get recent ingestion job history."""
    stmt = select(IngestionLog).order_by(IngestionLog.started_at.desc()).limit(limit)
    
    if source:
        stmt = stmt.where(IngestionLog.source_system == source)
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return [
        IngestionStatusResponse(
            id=log.id,
            source_system=log.source_system,
            status=log.status,
            started_at=log.started_at,
            completed_at=log.completed_at,
            records_fetched=log.records_fetched,
            records_inserted=log.records_inserted,
            records_updated=log.records_updated,
            records_failed=log.records_failed,
            error_message=log.error_message,
        )
        for log in logs
    ]


async def run_sam_gov_ingestion(ingestion_id: uuid.UUID, params: dict):
    """
    Background task to run SAM.gov ingestion.
    
    This is a placeholder - actual implementation uses the 
    src.ingestion.sam_gov module.
    """
    from src.database.connection import async_session_factory
    from src.ingestion.sam_gov import SAMGovIngester
    from src.config import get_settings
    
    settings = get_settings()
    
    async with async_session_factory() as db:
        # Update status to running
        stmt = select(IngestionLog).where(IngestionLog.id == ingestion_id)
        result = await db.execute(stmt)
        log = result.scalar_one_or_none()
        
        if not log:
            return
        
        log.status = "running"
        await db.commit()
        
        try:
            # Run ingestion
            ingester = SAMGovIngester(
                api_key=settings.sam_gov_api_key,
                db_session=db,
            )
            
            stats = await ingester.ingest(
                naics_codes=params.get("naics_codes"),
                posted_from=params.get("posted_from"),
                limit=params.get("limit", 100),
            )
            
            # Update log with results
            log.status = "completed"
            log.completed_at = datetime.now(timezone.utc)
            log.records_fetched = stats.get("fetched", 0)
            log.records_inserted = stats.get("inserted", 0)
            log.records_updated = stats.get("updated", 0)
            log.records_failed = stats.get("failed", 0)
            
        except Exception as e:
            log.status = "failed"
            log.completed_at = datetime.now(timezone.utc)
            log.error_message = str(e)
        
        await db.commit()

