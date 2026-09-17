"""
HeatGuard AI — Application Configuration
Uses pydantic-settings to load from environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "HeatGuard AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://heatguard:heatguard_secret_2024@db:5432/heatguard"

    # JWT
    JWT_SECRET: str = "heatguard-jwt-secret-change-in-production-min32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",")]

    # Demo / Live mode
    DEMO_MODE: bool = True

    # ML
    ML_MODEL_PATH: str = "app/ml/models/risk_model.pkl"
    RANDOM_SEED: int = 42

    # Weather API (optional)
    OPENWEATHER_API_KEY: str = ""
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Notifications
    NOTIFICATION_MODE: str = "mock"  # mock | live

    # HTSI Thresholds (configurable)
    HTSI_SAFE_MAX: float = 20.0
    HTSI_LOW_MAX: float = 40.0
    HTSI_MODERATE_MAX: float = 60.0
    HTSI_HIGH_MAX: float = 80.0
    # EXTREME is > 80

    # Alert thresholds
    ALERT_EXTREME_HTSI: float = 81.0
    ALERT_HIGH_HTSI: float = 61.0
    ALERT_HIGH_VULNERABILITY: float = 60.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
