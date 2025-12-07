"""
Aureon API - Planetary Procurement Substrate
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.api import (
    opportunities, organizations, scoring, risk, health, ingestion,
    win_probability, proposals, supply_chain, pricing, auth
)
from src.database.connection import init_db, close_db

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Aureon API", version=settings.app_version)
    await init_db()
    logger.info("Database connection initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Aureon API")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Aureon API",
    description="""
    ## Planetary Procurement Substrate
    
    Aureon provides a foundational layer for intelligent procurement operations,
    offering unified access to opportunities, relevance scoring, and risk assessment
    across jurisdictions.
    
    ### Key Features
    
    - **Opportunity Discovery**: Aggregate and search procurement opportunities
    - **Relevance Scoring**: AI-powered matching of opportunities to organizations  
    - **Risk Assessment**: Comprehensive risk analysis for bid/no-bid decisions
    - **Multi-Jurisdiction**: Support for federal, state, and commercial procurement
    
    ### API Sections
    
    - `/opportunities` - Procurement opportunity management
    - `/organizations` - Organization profiles and capabilities
    - `/scoring` - Relevance scoring engine
    - `/risk` - Risk assessment engine
    - `/ingestion` - Data ingestion pipelines
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(scoring.router, prefix="/scoring", tags=["Relevance Scoring"])
app.include_router(risk.router, prefix="/risk", tags=["Risk Assessment"])
app.include_router(win_probability.router, prefix="/win-probability", tags=["Win Probability"])
app.include_router(proposals.router, prefix="/proposals", tags=["Proposal Generation"])
app.include_router(supply_chain.router, prefix="/supply-chain", tags=["Supply Chain Compliance"])
app.include_router(pricing.router, prefix="/pricing", tags=["Pricing Intelligence"])
app.include_router(ingestion.router, prefix="/ingestion", tags=["Data Ingestion"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirects to API documentation."""
    return {
        "name": "Aureon API",
        "version": settings.app_version,
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

