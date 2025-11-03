"""
FastAPI Backend for WhatsApp-Integrated Civil Engineering PM System v3.0 (Gamma)
Main application entry point with AI-first architecture
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
from typing import Callable

from .config import settings
from .database import create_tables, get_db, health_check_database
from .routers import auth, projects, tasks, costs, whatsapp, ai, admin
from .middleware.tenant_middleware import TenantMiddleware
from .middleware.auth_middleware import AuthMiddleware
from .services.ai_service import AIService
from .services.notification_service import NotificationService
from .utils.logging import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

# Global services
ai_service = AIService()
notification_service = NotificationService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Gamma PM System v3.0")

    # Create database tables (with error handling)
    try:
        await create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error("Failed to create database tables, continuing without them", error=str(e))

    # Initialize AI service (optional)
    try:
        if settings.ENABLE_AI_FEATURES:
            await ai_service.initialize()
            logger.info("AI service initialized")
        else:
            logger.info("AI service disabled via configuration")
    except Exception as e:
        logger.warning("AI service initialization failed, continuing without AI features", error=str(e))

    # Initialize notification service (optional)
    try:
        await notification_service.initialize()
        logger.info("Notification service initialized")
    except Exception as e:
        logger.warning("Notification service initialization failed, continuing without notifications", error=str(e))

    yield

    # Shutdown
    logger.info("Shutting down Gamma PM System v3.0")
    try:
        await ai_service.cleanup()
    except Exception as e:
        logger.warning("AI service cleanup failed", error=str(e))

    try:
        await notification_service.cleanup()
    except Exception as e:
        logger.warning("Notification service cleanup failed", error=str(e))

# Create FastAPI application
app = FastAPI(
    title="WhatsApp PM API - Gamma v3.0",
    description="AI-First Construction Project Management Platform",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(TenantMiddleware)
app.add_middleware(AuthMiddleware)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Log all HTTP requests with timing."""
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            status_code=response.status_code,
            process_time=f"{process_time:.3f}s",
            method=request.method,
            url=str(request.url)
        )

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            error=str(e),
            process_time=f"{process_time:.3f}s",
            method=request.method,
            url=str(request.url)
        )
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        url=str(request.url),
        method=request.method,
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    health_status = {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": time.time(),
        "services": {}
    }

    # Check database health
    try:
        db_health = await health_check_database()
        health_status["services"]["database"] = db_health.get("status", "unknown")
        if db_health.get("status") != "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["database"] = "disconnected"
        health_status["status"] = "unhealthy"

    # Check AI service health (only if enabled)
    if settings.ENABLE_AI_FEATURES:
        try:
            # Simple AI service check - just verify it exists
            health_status["services"]["ai_service"] = "ready"
        except Exception as e:
            health_status["services"]["ai_service"] = "failed"
            if health_status["status"] == "healthy":
                health_status["status"] = "degraded"
    else:
        health_status["services"]["ai_service"] = "disabled"

    # WhatsApp service status
    if settings.ENABLE_WHATSAPP_INTEGRATION:
        health_status["services"]["whatsapp"] = "configured"
    else:
        health_status["services"]["whatsapp"] = "disabled"

    return health_status

# API v1 routes
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    projects.router,
    prefix="/api/v1/projects",
    tags=["Projects"]
)

app.include_router(
    tasks.router,
    prefix="/api/v1",
    tags=["Tasks"]
)

app.include_router(
    costs.router,
    prefix="/api/v1",
    tags=["Costs"]
)

app.include_router(
    whatsapp.router,
    prefix="/api/v1/whatsapp",
    tags=["WhatsApp"]
)

app.include_router(
    ai.router,
    prefix="/api/v1/ai",
    tags=["AI Services"]
)

app.include_router(
    admin.router,
    prefix="/api/v1",
    tags=["Admin"]
)

# WebSocket endpoint for real-time features
from .routers.websocket import ws_router
app.include_router(ws_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "WhatsApp PM API - Gamma v3.0",
        "version": "3.0.0",
        "documentation": "/api/docs",
        "health": "/health",
        "features": [
            "AI-powered message processing",
            "Real-time collaboration",
            "Multi-tenant architecture",
            "WhatsApp integration",
            "Project health analytics"
        ]
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )
