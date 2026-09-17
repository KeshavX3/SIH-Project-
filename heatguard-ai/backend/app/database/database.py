"""
HeatGuard AI — Database setup
SQLAlchemy async-compatible engine with PostGIS support.
"""
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def get_engine(retries: int = 3, delay: int = 1):
    """Create SQLAlchemy engine, falling back to SQLite if PostgreSQL is unreachable."""
    # If explicitly using sqlite
    if settings.DATABASE_URL.startswith("sqlite"):
        logger.info(f"Using SQLite database: {settings.DATABASE_URL}")
        return create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

    for attempt in range(retries):
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                echo=False,
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ PostgreSQL database connection established")
            return engine
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"PostgreSQL not ready (attempt {attempt + 1}/{retries}): {e}")
                time.sleep(delay)
            else:
                logger.warning(f"PostgreSQL unreachable ({e}). Falling back to local SQLite database: sqlite:///./heatguard.db")
                return create_engine("sqlite:///./heatguard.db", connect_args={"check_same_thread": False})


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_postgis(engine):
    """Enable PostGIS extension in the database."""
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))
            conn.commit()
        logger.info("✓ PostGIS extension enabled")
    except Exception as e:
        logger.warning(f"PostGIS extension note: {e}")
