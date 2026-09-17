"""
HeatGuard AI — Demo Data Seeder
=================================

Seeds the database with realistic demonstration data for Jaipur city.

DATA TRANSPARENCY:
  - All data is SYNTHETIC/DEMONSTRATION.
  - Weather conditions are randomly generated within realistic ranges.
  - Population data approximates real Jaipur demographics proportionally.
  - Health indicators and risk predictions are computed by the thermal/risk engines.
  - No real patient, mortality, or hospitalization data is used.

Credentials seeded:
  Admin user:  admin@heatguard.ai  /  heatguard2024
  Analyst user: analyst@heatguard.ai / analyst2024
"""
import random
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.models import (
    User, City, Ward, PopulationData, WeatherData, ThermalMetrics,
    RiskPrediction, Alert, AlertAction, CoolingCenter, Hospital,
    RoleEnum, RiskLevelEnum, AlertStatusEnum, DataSourceEnum,
)
from app.thermal.thermal_engine import WeatherInput, calculate_all_thermal_metrics
from app.risk.vulnerability import VulnerabilityInput, calculate_vulnerability
from app.risk.risk_engine import RiskInput, calculate_health_risk

logger = logging.getLogger(__name__)

RANDOM_SEED = 42
rng = random.Random(RANDOM_SEED)


# ─── Ward definitions (Jaipur approximate data) ──────────────────────────────

WARDS = [
    {
        "ward_number": 1,
        "ward_name": "Walled City (Old Jaipur)",
        "latitude": 26.9239,
        "longitude": 75.8267,
        "area_sq_km": 6.2,
        "total_population": 180000,
        "elderly_pct": 0.12,
        "children_pct": 0.28,
        "outdoor_worker_pct": 0.18,
        "hospitals_nearby": 1,
    },
    {
        "ward_number": 2,
        "ward_name": "Mansarovar",
        "latitude": 26.8540,
        "longitude": 75.7580,
        "area_sq_km": 14.5,
        "total_population": 210000,
        "elderly_pct": 0.09,
        "children_pct": 0.22,
        "outdoor_worker_pct": 0.10,
        "hospitals_nearby": 3,
    },
    {
        "ward_number": 3,
        "ward_name": "Sanganer",
        "latitude": 26.8090,
        "longitude": 75.7960,
        "area_sq_km": 18.0,
        "total_population": 160000,
        "elderly_pct": 0.10,
        "children_pct": 0.30,
        "outdoor_worker_pct": 0.22,
        "hospitals_nearby": 1,
    },
    {
        "ward_number": 4,
        "ward_name": "Vaishali Nagar",
        "latitude": 26.9120,
        "longitude": 75.7380,
        "area_sq_km": 10.8,
        "total_population": 145000,
        "elderly_pct": 0.11,
        "children_pct": 0.20,
        "outdoor_worker_pct": 0.08,
        "hospitals_nearby": 2,
    },
    {
        "ward_number": 5,
        "ward_name": "Amer",
        "latitude": 26.9855,
        "longitude": 75.8513,
        "area_sq_km": 22.3,
        "total_population": 95000,
        "elderly_pct": 0.14,
        "children_pct": 0.32,
        "outdoor_worker_pct": 0.25,
        "hospitals_nearby": 0,
    },
]

COOLING_CENTERS = [
    ("Community Hall - Walled City", 26.9210, 75.8250, 200),
    ("Mansarovar Sports Complex", 26.8520, 75.7560, 350),
    ("Sanganer Panchayat Hall", 26.8070, 75.7980, 150),
    ("Vaishali Nagar Community Center", 26.9100, 75.7400, 250),
]

HOSPITALS = [
    ("SMS Hospital", 26.9056, 75.8089, 1800, 120, "0141-2518888"),
    ("Santokba Durlabhji Memorial Hospital", 26.9031, 75.8106, 450, 45, "0141-2566251"),
    ("Fortis Escorts Hospital", 26.8591, 75.7958, 350, 55, "0141-2547000"),
    ("Mahatma Gandhi Hospital", 26.8977, 75.8278, 500, 60, "0141-2224747"),
]


def _make_weather(
    city_id: int,
    ward_id: Optional[int],
    timestamp: datetime,
    heatwave_day: int,
    base_temp: float = 40.0,
) -> WeatherData:
    """Generate a synthetic weather observation."""
    # Temperature varies by time of day
    hour = timestamp.hour
    time_factor = (
        -3.0 if hour < 6
        else 0.0 if hour < 10
        else 2.5 if hour < 14
        else 1.0 if hour < 18
        else -1.5
    )
    temp = base_temp + time_factor + rng.uniform(-1.5, 1.5)
    humidity = rng.uniform(15, 55)
    wind = rng.uniform(5, 25)
    solar = max(0.0, 800.0 * (1 - abs(hour - 13) / 8.0) + rng.uniform(-50, 50))
    if hour < 6 or hour > 19:
        solar = 0.0

    return WeatherData(
        city_id=city_id,
        ward_id=ward_id,
        timestamp=timestamp,
        temperature=round(temp, 1),
        humidity=round(humidity, 1),
        wind_speed=round(wind, 1),
        solar_radiation=round(solar, 0),
        pressure=round(rng.uniform(1005, 1015), 1),
        cloud_cover=round(rng.uniform(0, 20), 0),
        feels_like=round(temp + 2.0, 1),
        data_source=DataSourceEnum.SYNTHETIC,
        heatwave_day_number=heatwave_day,
    )


def seed_demo_data(db: Session) -> None:
    """
    Seed all demo data. Safe to call on a populated DB — checks for
    existing data and skips seeding if already done.
    """
    # Guard: only seed if no city exists yet
    if db.query(City).count() > 0:
        logger.info("Demo data already seeded — skipping.")
        return

    logger.info("Seeding HeatGuard AI demo data (Jaipur)...")

    # ── 1. Users ──────────────────────────────────────────────────────────────
    admin = User(
        email="admin@heatguard.ai",
        full_name="HeatGuard Admin",
        hashed_password=hash_password("heatguard2024"),
        role=RoleEnum.ADMIN,
    )
    analyst = User(
        email="analyst@heatguard.ai",
        full_name="HeatGuard Analyst",
        hashed_password=hash_password("analyst2024"),
        role=RoleEnum.ANALYST,
    )
    db.add_all([admin, analyst])
    db.flush()
    logger.info("✓ Users seeded")

    # ── 2. City ───────────────────────────────────────────────────────────────
    city = City(
        name="Jaipur",
        state="Rajasthan",
        country="India",
        latitude=26.9124,
        longitude=75.7873,
        population=3046163,
        area_sq_km=467.0,
        is_active=True,
    )
    db.add(city)
    db.flush()
    logger.info("✓ City seeded: Jaipur")

    # ── 3. Wards ──────────────────────────────────────────────────────────────
    ward_objs = []
    for w in WARDS:
        ward = Ward(
            ward_number=w["ward_number"],
            ward_name=w["ward_name"],
            city_id=city.id,
            latitude=w["latitude"],
            longitude=w["longitude"],
            area_sq_km=w["area_sq_km"],
        )
        db.add(ward)
        db.flush()

        # Population data
        total_pop = w["total_population"]
        elderly = int(total_pop * w["elderly_pct"])
        children = int(total_pop * w["children_pct"])
        outdoor = int(total_pop * w["outdoor_worker_pct"])

        vuln_inp = VulnerabilityInput(
            ward_id=ward.id,
            total_population=total_pop,
            area_sq_km=w["area_sq_km"],
            elderly_population=elderly,
            children_population=children,
            outdoor_worker_population=outdoor,
            hospital_count_within_2km=w["hospitals_nearby"],
        )
        vuln = calculate_vulnerability(vuln_inp)

        pop_data = PopulationData(
            ward_id=ward.id,
            total_population=total_pop,
            elderly_population=elderly,
            children_population=children,
            outdoor_worker_population=outdoor,
            population_density=round(total_pop / w["area_sq_km"], 1),
            elderly_density=round(elderly / w["area_sq_km"], 1),
            outdoor_worker_density=round(outdoor / w["area_sq_km"], 1),
            vulnerability_score=vuln.vulnerability_score,
            vulnerability_level=RiskLevelEnum(vuln.vulnerability_level),
            data_source=DataSourceEnum.DEMO,
        )
        db.add(pop_data)
        ward_objs.append((ward, w, vuln))

    db.flush()
    logger.info("✓ Wards and population data seeded")

    # ── 4. Hospitals & Cooling Centers ────────────────────────────────────────
    for i, (ward_obj, wdata, vuln) in enumerate(ward_objs):
        if i < len(COOLING_CENTERS):
            name, lat, lon, cap = COOLING_CENTERS[i]
            cc = CoolingCenter(
                ward_id=ward_obj.id, name=name, latitude=lat, longitude=lon,
                capacity=cap, is_active=True, address=f"{name}, Jaipur",
            )
            db.add(cc)

    for name, lat, lon, beds, icu, contact in HOSPITALS:
        hosp = Hospital(
            ward_id=ward_objs[0][0].id,
            name=name, latitude=lat, longitude=lon,
            bed_count=beds, icu_beds=icu, contact=contact,
            address=f"{name}, Jaipur, Rajasthan",
        )
        db.add(hosp)

    db.flush()
    logger.info("✓ Infrastructure seeded")

    # ── 5. Weather + Thermal Metrics (72h history) ────────────────────────────
    now = datetime.now(timezone.utc)
    base_temps = {w[0].id: 38.0 + i * 1.5 for i, (w, _, _) in enumerate(ward_objs)}

    for ward_obj, wdata, vuln in ward_objs:
        ward_id = ward_obj.id
        base_temp = base_temps[ward_id]

        for hours_ago in range(72, 0, -2):  # Every 2 hours, 72h history
            ts = now - timedelta(hours=hours_ago)
            heatwave_day = max(0, (72 - hours_ago) // 24)

            weather = _make_weather(city.id, ward_id, ts, heatwave_day, base_temp)
            db.add(weather)
            db.flush()

            # Thermal metrics
            w_inp = WeatherInput(
                temperature=weather.temperature,
                humidity=weather.humidity,
                wind_speed=weather.wind_speed,
                solar_radiation=weather.solar_radiation or 0.0,
                heatwave_duration=heatwave_day,
            )
            thermal = calculate_all_thermal_metrics(w_inp)

            components = thermal.htsi_components
            tm = ThermalMetrics(
                weather_data_id=weather.id,
                ward_id=ward_id,
                heat_index=thermal.heat_index,
                wbgt=thermal.wbgt,
                utci=thermal.utci,
                heat_index_level=RiskLevelEnum(thermal.heat_index_level),
                wbgt_level=RiskLevelEnum(thermal.wbgt_level),
                htsi=thermal.htsi,
                htsi_level=RiskLevelEnum(thermal.htsi_level),
                htsi_temp_contribution=components.get("temperature", 0.0),
                htsi_humidity_contribution=components.get("humidity", 0.0),
                htsi_wind_contribution=components.get("wind", 0.0),
                htsi_solar_contribution=components.get("solar_radiation", 0.0),
                htsi_wbgt_contribution=components.get("wbgt", 0.0),
                htsi_duration_contribution=components.get("duration", 0.0),
            )
            db.add(tm)

    db.flush()
    logger.info("✓ Weather and thermal metrics seeded (72h × 5 wards)")

    # ── 6. Risk Predictions ───────────────────────────────────────────────────
    for ward_obj, wdata, vuln in ward_objs:
        ward_id = ward_obj.id

        # Latest weather
        latest_weather = (
            db.query(WeatherData)
            .filter(WeatherData.ward_id == ward_id)
            .order_by(WeatherData.timestamp.desc())
            .first()
        )
        if not latest_weather:
            continue

        w_inp = WeatherInput(
            temperature=latest_weather.temperature,
            humidity=latest_weather.humidity,
            wind_speed=latest_weather.wind_speed,
            solar_radiation=latest_weather.solar_radiation or 0.0,
            heatwave_duration=latest_weather.heatwave_day_number,
        )
        thermal = calculate_all_thermal_metrics(w_inp)

        risk_inp = RiskInput(
            ward_id=ward_id,
            htsi=thermal.htsi,
            heat_index=thermal.heat_index,
            wbgt=thermal.wbgt,
            temperature=latest_weather.temperature,
            temperature_anomaly=latest_weather.temperature - 34.0,  # approx seasonal normal
            heatwave_duration=latest_weather.heatwave_day_number,
            vulnerability_score=vuln.vulnerability_score,
            historical_health_indicator=50.0,
        )
        risk = calculate_health_risk(risk_inp)

        pred = RiskPrediction(
            ward_id=ward_id,
            valid_for=now,
            overall_risk_level=RiskLevelEnum(risk.overall_risk_level),
            htsi=thermal.htsi,
            mortality_risk_score=risk.mortality_risk_score,
            hospitalization_risk_score=risk.hospitalization_risk_score,
            mortality_risk_level=RiskLevelEnum(risk.mortality_risk_level),
            hospitalization_risk_level=RiskLevelEnum(risk.hospitalization_risk_level),
            vulnerability_score=vuln.vulnerability_score,
            temperature_anomaly=latest_weather.temperature - 34.0,
            heatwave_duration=latest_weather.heatwave_day_number,
            prediction_features=risk.risk_factors,
        )
        db.add(pred)

    db.flush()
    logger.info("✓ Risk predictions seeded")

    # ── 7. Alerts ─────────────────────────────────────────────────────────────
    alert_data = [
        {
            "ward_idx": 0,  # Walled City — most vulnerable
            "severity": RiskLevelEnum.EXTREME,
            "status": AlertStatusEnum.ACTIVE,
            "title": "EXTREME Heat Alert — Walled City Ward",
            "reason": "HTSI > 81, WBGT > 36°C. Immediate action required for vulnerable population.",
            "htsi_value": 84.5,
            "recommendations": [
                "Open all designated cooling centers immediately",
                "Deploy water distribution teams to Walled City area",
                "Alert elderly care facilities and outdoor workers",
                "Restrict non-essential outdoor activity 11AM–5PM",
            ],
        },
        {
            "ward_idx": 2,  # Sanganer
            "severity": RiskLevelEnum.HIGH,
            "status": AlertStatusEnum.ACTIVE,
            "title": "HIGH Heat Stress — Sanganer Ward",
            "reason": "Elevated HTSI with high outdoor worker density. Heatwave day 3.",
            "htsi_value": 73.2,
            "recommendations": [
                "Enforce mandatory rest breaks for outdoor workers",
                "Provide ORS and hydration stations at construction sites",
                "Alert Sanganer municipal office",
            ],
        },
        {
            "ward_idx": 4,  # Amer
            "severity": RiskLevelEnum.HIGH,
            "status": AlertStatusEnum.ACTIVE,
            "title": "HIGH Heat Risk — Amer Ward",
            "reason": "High elderly population (14%), no hospital within 2km. Heatwave day 3.",
            "htsi_value": 71.8,
            "recommendations": [
                "Deploy mobile medical units to Amer area",
                "Community health workers to conduct door-to-door wellness checks",
            ],
        },
        {
            "ward_idx": 0,  # Walled City — resolved yesterday
            "severity": RiskLevelEnum.HIGH,
            "status": AlertStatusEnum.RESOLVED,
            "title": "HIGH Heat Alert — Walled City (Yesterday)",
            "reason": "Previous day alert now resolved.",
            "htsi_value": 76.0,
            "recommendations": [],
        },
    ]

    for a in alert_data:
        alert = Alert(
            ward_id=ward_objs[a["ward_idx"]][0].id,
            severity=a["severity"],
            status=a["status"],
            title=a["title"],
            reason=a["reason"],
            htsi_value=a["htsi_value"],
            recommendations=a["recommendations"],
            notification_simulated=True,
        )
        db.add(alert)
        db.flush()

        if a["status"] == AlertStatusEnum.RESOLVED:
            action = AlertAction(
                alert_id=alert.id,
                user_id=admin.id,
                action="RESOLVED",
                notes="Conditions improved overnight. Monitoring continues.",
            )
            db.add(action)

    db.commit()
    logger.info("✓ Alerts seeded")
    logger.info("✅ Demo data seeding complete!")
    logger.info("  Login: admin@heatguard.ai / heatguard2024")
    logger.info("  Login: analyst@heatguard.ai / analyst2024")
