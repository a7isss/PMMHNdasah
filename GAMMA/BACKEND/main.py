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

from config import settings
from database import create_tables, get_db
from routers import auth, projects, tasks, costs, whatsapp, ai
from middleware.tenant_middleware import TenantMiddleware
from middleware.auth_middleware import AuthMiddleware
from services.ai_service import AIService
from services.notification_service import NotificationService
from utils.logging import setup_logging

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

    # Create database tables
    await create_tables()
    logger.info("Database tables created/verified")

    # Initialize AI service
    await ai_service.initialize()
    logger.info("AI service initialized")

    # Initialize notification service
    await notification_service.initialize()
    logger.info("Notification service initialized")

    yield

    # Shutdown
    logger.info("Shutting down Gamma PM System v3.0")
    await ai_service.cleanup()
    await notification_service.cleanup()

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
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": time.time(),
        "services": {
            "database": "connected",  # TODO: Add actual health checks
            "ai_service": "ready",
            "whatsapp": "configured"
        }
    }

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

# WebSocket endpoint for real-time features
from routers.websocket import ws_router
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
