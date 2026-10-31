"""Health check routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ideaos.core.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "ideaos-api"}


@router.get("/healthz")
async def kubernetes_health_check():
    """Kubernetes liveness/readiness probe."""
    return {"status": "ok"}


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Database connectivity check."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}