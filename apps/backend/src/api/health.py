"""Health check endpoints."""
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database.connection import get_db

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns the health status of the API and its dependencies.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = {
            "status": "healthy",
            "type": "postgresql"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check external API connectivity
    health_status["services"]["sam_gov"] = {
        "status": "configured" if settings.sam_gov_api_key else "not_configured"
    }
    
    health_status["services"]["openai"] = {
        "status": "configured" if settings.openai_api_key else "not_configured"
    }
    
    return health_status


@router.get("/health/live")
async def liveness_probe() -> Dict[str, str]:
    """Kubernetes liveness probe - is the service running?"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}

