"""
Database connection and session management for WhatsApp PM System v3.0 (Gamma)
Async SQLAlchemy with Supabase PostgreSQL integration
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
import structlog
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import redis.asyncio as redis

from .config import settings
# from models.sqlalchemy import *  # Commented out to avoid VECTOR import errors

logger = structlog.get_logger(__name__)

# Global database engine
engine = None
async_session_maker = None

# Redis connection
redis_client = None


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def init_database():
    """Initialize database connection and create tables."""
    global engine, async_session_maker

    print("🔄 Initializing database connection...")

    try:
        # Log database URL (safely)
        db_url = settings.DATABASE_URL
        if '@' in db_url:
            # Hide password in logs
            user_part, rest = db_url.split('@', 1)
            safe_url = f"{user_part.split(':')[0]}:***@{rest}"
        else:
            safe_url = db_url
        print(f"📋 Database URL: {safe_url}")

        # Create async engine
        db_config = settings.get_database_config()
        print(f"⚙️  Database config: {db_config}")

        engine = create_async_engine(**db_config)
        print("✅ Database engine created")

        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection test successful")

        # Create session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        print("✅ Database session maker created")

        logger.info("Database engine initialized", url=safe_url)

    except Exception as e:
        print(f"❌ Failed to initialize database: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        logger.error("Failed to initialize database", error=str(e))
        raise


async def close_database():
    """Close database connections."""
    global engine, redis_client

    if engine:
        await engine.dispose()
        logger.info("Database connections closed")

    if redis_client:
        await redis_client.close()
        logger.info("Redis connections closed")


async def create_tables():
    """Create all database tables if they don't exist."""
    print("🔄 Creating database tables...")

    try:
        # Ensure database is initialized
        if not engine:
            print("⚠️  Database engine not initialized, initializing now...")
            await init_database()

        if not engine:
            raise RuntimeError("Database engine could not be initialized")

        # Enable required extensions (each in its own transaction to avoid aborting others)
        print("📦 Enabling PostgreSQL extensions...")
        extensions = ["uuid-ossp", "pgvector", "postgis", "pg_cron"]

        for ext in extensions:
            try:
                # Use a separate transaction for each extension to avoid cascading failures
                async with engine.begin() as conn:
                    await conn.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}";'))
                print(f"✅ Extension {ext} enabled")
            except Exception as ext_error:
                print(f"⚠️  Failed to enable extension {ext}: {ext_error}")
                # Continue with other extensions - don't fail the whole process

        # Create tables in a separate transaction
        print("📋 Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")

        logger.info("Database tables created successfully")

    except Exception as e:
        print(f"❌ Failed to create database tables: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        logger.error("Failed to create database tables", error=str(e))
        raise


async def init_redis():
    """Initialize Redis connection."""
    global redis_client

    try:
        redis_config = settings.get_redis_config()
        redis_client = redis.Redis(**redis_config)

        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established")

    except Exception as e:
        logger.warning("Failed to connect to Redis, caching disabled", error=str(e))
        redis_client = None


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with automatic cleanup."""
    if not async_session_maker:
        await init_database()

    session = async_session_maker()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error("Database session error", error=str(e))
        raise
    finally:
        await session.close()


async def get_redis() -> Optional[redis.Redis]:
    """Get Redis client instance."""
    if not redis_client:
        await init_redis()
    return redis_client


async def health_check_database() -> dict:
    """Check database health and connectivity."""
    try:
        # Check if database is initialized
        if not async_session_maker:
            # Try to initialize database
            try:
                await init_database()
            except Exception as init_error:
                logger.warning("Database initialization failed during health check", error=str(init_error))
                return {
                    "status": "not_configured",
                    "database": "not_initialized",
                    "error": str(init_error),
                    "type": "postgresql"
                }

        async with get_db() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1 as health_check"))
            row = result.first()

            if row and row.health_check == 1:
                return {
                    "status": "healthy",
                    "database": "connected",
                    "type": "postgresql"
                }
            else:
                return {
                    "status": "unhealthy",
                    "database": "query_failed",
                    "type": "postgresql"
                }

    except Exception as e:
        logger.warning("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "type": "postgresql"
        }


async def health_check_redis() -> dict:
    """Check Redis health and connectivity."""
    try:
        redis_conn = await get_redis()
        if redis_conn:
            await redis_conn.ping()
            return {
                "status": "healthy",
                "redis": "connected",
                "type": "redis"
            }
        else:
            return {
                "status": "degraded",
                "redis": "disabled",
                "type": "redis"
            }

    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "redis": "disconnected",
            "error": str(e),
            "type": "redis"
        }


async def get_database_stats() -> dict:
    """Get database statistics and metrics."""
    try:
        async with get_db() as session:
            # Get table statistics
            tables_query = text("""
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
                LIMIT 10
            """)

            result = await session.execute(tables_query)
            tables = [dict(row) for row in result.mappings()]

            # Get connection statistics
            connections_query = text("""
                SELECT
                    count(*) as total_connections,
                    count(*) filter (where state = 'active') as active_connections,
                    count(*) filter (where state = 'idle') as idle_connections
                FROM pg_stat_activity
                WHERE datname = current_database()
            """)

            result = await session.execute(connections_query)
            connections = dict(result.first())

            return {
                "tables": tables,
                "connections": connections,
                "timestamp": "2025-11-02T22:09:00Z"  # Current time
            }

    except Exception as e:
        logger.error("Failed to get database stats", error=str(e))
        return {"error": str(e)}


# Initialize on import
async def initialize():
    """Initialize all database connections."""
    await init_database()
    await init_redis()


async def cleanup():
    """Cleanup all database connections."""
    await close_database()


# Export commonly used functions
__all__ = [
    "get_db",
    "get_redis",
    "create_tables",
    "health_check_database",
    "health_check_redis",
    "get_database_stats",
    "initialize",
    "cleanup",
    "Base"
]
