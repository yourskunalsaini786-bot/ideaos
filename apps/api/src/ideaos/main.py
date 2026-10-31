"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from ideaos.core.config import get_settings
from ideaos.core.database import init_db, close_db, get_db
from ideaos.core.security import decode_token, TokenData
from ideaos.api.routes import captures, ideas, fusion, content, brand, calendar, feedback, search, workspace, health, repurpose

settings = get_settings()

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("starting_up", app=settings.APP_NAME, version=settings.APP_VERSION)
    await init_db()
    yield
    logger.info("shutting_down")
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="IdeaOS API - Content Repurposing Studio with Brand Memory",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for workspace context (RLS)
@app.middleware("http")
async def workspace_context_middleware(request: Request, call_next):
    """Extract workspace context from JWT and set for RLS."""
    # Skip for health checks and docs
    if request.url.path in ["/health", "/healthz", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            token_data = decode_token(token)
            # Store workspace_id in request state for RLS
            request.state.workspace_id = token_data.workspace_id
            request.state.user_id = token_data.sub
            request.state.user_role = token_data.role
        except ValueError:
            pass  # Invalid token, let route handle auth

    response = await call_next(request)
    return response


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found", "type": "not_found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error("internal_error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"},
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(workspace.router, prefix="/api/v1/workspace", tags=["Workspace"])
app.include_router(captures.router, prefix="/api/v1/captures", tags=["Captures"])
app.include_router(ideas.router, prefix="/api/v1/ideas", tags=["Ideas"])
app.include_router(fusion.router, prefix="/api/v1/fusion", tags=["Fusion"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(brand.router, prefix="/api/v1/brand", tags=["Brand"])
app.include_router(calendar.router, prefix="/api/v1/calendar", tags=["Calendar"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Feedback"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(repurpose.router, prefix="/api/v1/repurpose", tags=["Repurpose"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ideaos.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )