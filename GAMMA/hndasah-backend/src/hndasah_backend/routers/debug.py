"""
Debug and diagnostics router for system administrators.
Provides endpoints for system monitoring, database diagnostics,
API testing, and performance metrics.
"""

import os
import platform
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer

from ..database import get_db
from ..config import settings
from ..utils.logging import get_logger
from ..middleware.auth_middleware import get_current_super_admin

router = APIRouter(
    prefix="/api/v1/admin/debug",
    tags=["debug"],
    dependencies=[Depends(get_current_super_admin)]
)

logger = get_logger(__name__)
security = HTTPBearer()

@router.get("/system-info")
async def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information including environment variables,
    configuration, and runtime details.
    """
    try:
        # Environment variables (filter sensitive ones)
        sensitive_keys = {
            'password', 'secret', 'key', 'token', 'auth', 'database_url',
            'db_password', 'db_user', 'redis_url', 'smtp_password'
        }

        env_vars = {}
        for key, value in os.environ.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                env_vars[key] = "***FILTERED***"
            else:
                env_vars[key] = value

        # System information
        system_info = {
            "environment": env_vars,
            "config": {
                "app_name": settings.APP_NAME,
                "version": getattr(settings, 'VERSION', 'unknown'),
                "environment": settings.ENVIRONMENT,
                "debug_mode": settings.DEBUG,
                "database_url": "***FILTERED***" if settings.DATABASE_URL else None,
                "redis_url": "***FILTERED***" if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL else None,
            },
            "runtime": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": os.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/')._asdict(),
                "uptime": time.time() - psutil.boot_time(),
                "process_count": len(psutil.pids()),
            }
        }

        return system_info

    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system information")

@router.get("/database-status")
async def get_database_status(db=Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive database status and diagnostics.
    """
    try:
        # Basic connection test
        db_status = {"status": "unknown", "connection": {}, "tables": []}

        # Test connection
        start_time = time.time()
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        connection_time = time.time() - start_time

        db_status["connection"] = {
            "connected": True,
            "connection_time_ms": round(connection_time * 1000, 2),
            "database_type": str(db.bind.dialect.name),
        }

        # Get database version
        try:
            if db.bind.dialect.name == 'postgresql':
                version_result = db.execute(text("SELECT version()")).fetchone()
                db_status["connection"]["version"] = version_result[0] if version_result else "unknown"
            elif db.bind.dialect.name == 'sqlite':
                version_result = db.execute(text("SELECT sqlite_version()")).fetchone()
                db_status["connection"]["version"] = version_result[0] if version_result else "unknown"
        except Exception as e:
            db_status["connection"]["version"] = f"error: {str(e)}"

        # Get table statistics
        try:
            if db.bind.dialect.name == 'postgresql':
                # PostgreSQL table statistics
                table_query = text("""
                    SELECT
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_rows,
                        n_dead_tup as dead_rows,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 20
                """)
                table_results = db.execute(table_query).fetchall()

                db_status["tables"] = [
                    {
                        "schema": row[0],
                        "name": row[1],
                        "inserts": row[2],
                        "updates": row[3],
                        "deletes": row[4],
                        "live_rows": row[5],
                        "dead_rows": row[6],
                        "size": row[7]
                    }
                    for row in table_results
                ]

            elif db.bind.dialect.name == 'sqlite':
                # SQLite table statistics (simplified)
                table_query = text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                table_results = db.execute(table_query).fetchall()

                db_status["tables"] = [
                    {
                        "name": row[0],
                        "row_count": "N/A (SQLite)",
                        "size_mb": "N/A (SQLite)"
                    }
                    for row in table_results
                ]

        except Exception as e:
            logger.warning(f"Failed to get table statistics: {e}")
            db_status["tables"] = [{"error": str(e)}]

        # Determine overall status
        if connection_time < 1.0:  # Less than 1 second
            db_status["status"] = "healthy"
        elif connection_time < 5.0:  # Less than 5 seconds
            db_status["status"] = "slow"
        else:
            db_status["status"] = "unhealthy"

        return db_status

    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        return {
            "status": "unhealthy",
            "connection": {"connected": False, "error": str(e)},
            "tables": []
        }
    except Exception as e:
        logger.error(f"Failed to get database status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve database status")

@router.get("/logs")
async def get_system_logs(
    limit: int = Query(50, ge=1, le=500),
    level: Optional[str] = Query(None, description="Filter by log level (ERROR, WARNING, INFO, DEBUG)"),
    source: Optional[str] = Query(None, description="Filter by source/module")
) -> Dict[str, Any]:
    """
    Get recent system logs with optional filtering.
    Note: This is a simplified implementation. In production, you would integrate
    with a proper logging system like ELK stack, Loki, or similar.
    """
    try:
        # For now, return a placeholder response
        # In a real implementation, you would query your logging system
        logs = [
            {
                "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
                "level": "INFO",
                "message": f"System startup completed - iteration {i}",
                "source": "system"
            }
            for i in range(min(limit, 10))  # Return max 10 sample logs
        ]

        # Apply filters
        if level:
            logs = [log for log in logs if log["level"] == level.upper()]

        if source:
            logs = [log for log in logs if source.lower() in log["source"].lower()]

        return {
            "logs": logs[:limit],
            "total": len(logs),
            "filtered": level or source,
            "note": "This is a placeholder implementation. Integrate with your logging system for real logs."
        }

    except Exception as e:
        logger.error(f"Failed to get system logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system logs")

@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """
    Get system performance metrics and statistics.
    """
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used
        memory_total = memory.total

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = disk.used
        disk_total = disk.total

        # Network metrics (basic)
        network = psutil.net_io_counters()
        bytes_sent = network.bytes_sent
        bytes_recv = network.bytes_recv

        # Process metrics
        process_count = len(psutil.pids())

        # Database connection count (placeholder - would need actual monitoring)
        db_connections = 0  # Placeholder

        # API metrics (placeholder - would need actual monitoring)
        api_requests = 0  # Placeholder
        api_errors = 0    # Placeholder
        avg_response_time = 0  # Placeholder

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage": cpu_percent,
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
            },
            "memory": {
                "usage": memory_percent,
                "used_bytes": memory_used,
                "total_bytes": memory_total,
                "available_bytes": memory.available,
            },
            "disk": {
                "usage": disk_percent,
                "used_bytes": disk_used,
                "total_bytes": disk_total,
                "free_bytes": disk.free,
            },
            "network": {
                "bytes_sent": bytes_sent,
                "bytes_recv": bytes_recv,
            },
            "system": {
                "process_count": process_count,
                "uptime_seconds": time.time() - psutil.boot_time(),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            },
            "database": {
                "active_connections": db_connections,
                "connection_pool_size": 10,  # Placeholder
            },
            "api": {
                "requests_per_minute": api_requests,
                "error_rate": api_errors,
                "avg_response_time_ms": avg_response_time,
            }
        }

        return metrics

    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")

@router.get("/health")
async def debug_health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for debugging purposes.
    """
    try:
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {}
        }

        # System health
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
        }

        # Database health
        try:
            db = next(get_db())
            start_time = time.time()
            db.execute(text("SELECT 1"))
            connection_time = time.time() - start_time

            health_status["checks"]["database"] = {
                "status": "healthy" if connection_time < 1.0 else "slow",
                "connection_time_ms": round(connection_time * 1000, 2),
                "dialect": str(db.bind.dialect.name),
            }
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

        # Application health
        health_status["checks"]["application"] = {
            "status": "healthy",
            "version": getattr(settings, 'VERSION', 'unknown'),
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
        }

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy",
            "error": str(e),
            "checks": {}
        }
