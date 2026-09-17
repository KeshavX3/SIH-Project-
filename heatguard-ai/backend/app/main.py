"""
HeatGuard AI — FastAPI Application Entry Point
================================================

SIH26083: Extreme Heatwave Early Warning & Human Thermal Stress Index
Demo city: Jaipur, Rajasthan, India

All endpoints: http://localhost:8000/api/...
Swagger docs: http://localhost:8000/docs
"""
import logging
import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.database import engine, Base
from app.ml.prediction.predict import load_model

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("heatguard")


# ─── Lifespan: startup / shutdown ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialize DB and seed demo data. Shutdown: cleanup."""
    logger.info("=" * 60)
    logger.info("  HeatGuard AI — Extreme Heat Early Warning Platform")
    logger.info("  SIH26083 | City: Jaipur, Rajasthan, India")
    logger.info("=" * 60)

    try:
        # Create tables and seed demo data
        from app.models import models  # noqa: F401 — register all models
        Base.metadata.create_all(bind=engine)
        from app.database.database import SessionLocal
        from app.seeds.seed_demo import seed_demo_data
        db = SessionLocal()
        try:
            seed_demo_data(db)
        finally:
            db.close()
        logger.info("✓ Database ready")
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)

    try:
        # Load ML model
        load_model(settings.ML_MODEL_PATH)
        logger.info("✓ ML model ready")
    except Exception as e:
        logger.warning(f"ML model not ready (will train on first request): {e}")

    logger.info(f"✓ Demo mode: {settings.DEMO_MODE}")
    logger.info(f"✓ API ready at http://0.0.0.0:{8000}/docs")
    logger.info("=" * 60)

    yield

    logger.info("HeatGuard AI shutting down")


# ─── Application ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="HeatGuard AI",
    description=(
        "**HeatGuard AI** — Extreme Heatwave Early Warning & Human Thermal Stress Intelligence Platform\n\n"
        "**SIH26083** | Demo city: Jaipur, Rajasthan, India\n\n"
        "⚠️ **DATA NOTE**: All data in demo mode is SYNTHETIC DEMONSTRATION DATA. "
        "Not official government or meteorological data.\n\n"
        "Thermal indices documented in `/docs/methodology.md`."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
from app.api.auth import router as auth_router            # noqa: E402
from app.api.thermal import router as thermal_router      # noqa: E402
from app.api.wards import router as wards_router          # noqa: E402
from app.api.weather import router as weather_router      # noqa: E402
from app.api.alerts import router as alerts_router        # noqa: E402
from app.api.dashboard import router as dashboard_router  # noqa: E402
from app.api.risk import router as risk_router            # noqa: E402
from app.api.ml import router as ml_router                # noqa: E402

app.include_router(auth_router)
app.include_router(thermal_router)
app.include_router(wards_router)
app.include_router(weather_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(risk_router)
app.include_router(ml_router)


# ─── Health check ────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    from app.ml.prediction.predict import is_model_loaded

    # Check DB
    db_status = "CONNECTED"
    try:
        from app.database.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "ERROR"

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "demo_mode": settings.DEMO_MODE,
        "services": {
            "backend": "HEALTHY",
            "database": db_status,
            "ml_engine": "READY" if is_model_loaded() else "NOT_LOADED",
            "gis": "LOADED",
            "weather": "DEMO_MODE" if settings.DEMO_MODE else "LIVE",
            "notifications": "SIMULATION_MODE" if settings.NOTIFICATION_MODE == "mock" else "LIVE",
        },
        "app_name": "HeatGuard AI",
        "sih_problem_id": "SIH26083",
        "demo_city": "Jaipur, Rajasthan, India",
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "app": "HeatGuard AI",
        "description": "Extreme Heatwave Early Warning & Human Thermal Stress Intelligence Platform",
        "sih_problem_id": "SIH26083",
        "docs": "/docs",
        "health": "/api/health",
        "version": "1.0.0",
    }


# ─── Error handlers ──────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Check server logs.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
