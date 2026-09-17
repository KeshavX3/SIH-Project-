"""
HeatGuard AI — Database Seeder
================================

Populates the database with demonstration data for Jaipur, Rajasthan.

DATA SOURCE: DEMONSTRATION / SYNTHETIC DATA
─────────────────────────────────────────────
All data is created for SIH prototype demonstration.
It is NOT official government, census, or meteorological data.

The seeder is idempotent — running it multiple times will not create
duplicate records.
"""
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.database.database import engine, Base, init_postgis
from app.models.models import (
    User, City, Ward, PopulationData, HealthIndicator,
    WeatherData, ForecastData, ThermalMetrics, RiskPrediction,
    Alert, CoolingCenter, Hospital, ModelVersion,
    RoleEnum, RiskLevelEnum, AlertStatusEnum, DataSourceEnum
)
from app.core.security import hash_password
from app.thermal.thermal_engine import WeatherInput, calculate_all_thermal_metrics
from app.risk.vulnerability import VulnerabilityInput, calculate_vulnerability
from app.risk.risk_engine import RiskInput, calculate_health_risk
from app.services.demo_weather_provider import get_ward_weather, get_5day_forecast

logger = logging.getLogger(__name__)

# ─── Jaipur Ward Data (25 wards for demo) ──────────────────────────────────
JAIPUR_WARDS = [
    # (ward_num, name, lat, lon, area_km2, total_pop, elderly_pop, children_pop, outdoor_workers, hospitals_2km)
    (1,  "Amer",              26.987, 75.848, 12.5, 45000, 4500, 11250, 6750, 1),
    (2,  "Bani Park",         26.921, 75.782, 3.2,  38000, 5700, 7600,  4200, 2),
    (3,  "Chandpol",          26.924, 75.812, 2.8,  52000, 5200, 13000, 9360, 1),
    (4,  "Civil Lines",       26.908, 75.802, 4.1,  41000, 4920, 8200,  3690, 2),
    (5,  "Durgapura",         26.855, 75.802, 5.8,  63000, 5670, 15750, 8190, 1),
    (6,  "Gandhi Nagar",      26.896, 75.820, 3.5,  49000, 4900, 12250, 6370, 2),
    (7,  "Hasanpura",         26.933, 75.867, 6.2,  71000, 5680, 17750, 10650, 1),
    (8,  "Jhotwara",          26.971, 75.759, 8.9,  85000, 6800, 21250, 12750, 1),
    (9,  "Kanota",            26.882, 75.939, 14.2, 28000, 2240, 7000,  5880, 0),
    (10, "Khatipura",         26.938, 75.740, 7.1,  67000, 4020, 16750, 11390, 1),
    (11, "Lal Kothi",         26.891, 75.806, 2.9,  33000, 4290, 6600,  2970, 3),
    (12, "Malviya Nagar",     26.860, 75.815, 5.4,  58000, 5220, 14500, 6960, 1),
    (13, "Mansarovar",        26.861, 75.753, 7.8,  92000, 7360, 23000, 11040, 2),
    (14, "Muralipura",        26.961, 75.802, 5.6,  54000, 4320, 13500, 7560, 1),
    (15, "Nirman Nagar",      26.879, 75.793, 4.3,  47000, 5170, 11750, 5640, 2),
    (16, "Raja Park",         26.900, 75.830, 3.0,  39000, 3510, 9750,  4290, 2),
    (17, "Sanganer",          26.791, 75.815, 18.4, 98000, 5880, 24500, 22540, 1),
    (18, "Shastri Nagar",     26.940, 75.790, 4.7,  78000, 9360, 19500, 18720, 0),  # ← HIGH VULN
    (19, "Sodala",            26.900, 75.778, 5.1,  61000, 4880, 15250, 8540, 1),
    (20, "Tonk Road",         26.856, 75.830, 6.4,  69000, 4830, 17250, 10350, 1),
    (21, "Vidhyadhar Nagar",  26.951, 75.785, 6.8,  74000, 5920, 18500, 9620, 2),
    (22, "Vidhan Sabha",      26.885, 75.845, 4.2,  46000, 4140, 11500, 7360, 1),
    (23, "Yojana Nagar",      26.855, 75.768, 5.5,  53000, 4240, 13250, 7950, 1),
    (24, "Bajri Mandi",       26.910, 75.855, 3.8,  44000, 3960, 11000, 8800, 1),
    (25, "Barkat Nagar",      26.875, 75.795, 4.0,  57000, 4560, 14250, 8550, 1),
]


def create_tables():
    """Create all tables from SQLAlchemy models."""
    try:
        init_postgis(engine)
    except Exception:
        pass
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created/verified")


def seed_users(db: Session):
    """Seed demo users if they don't exist."""
    demo_users = [
        {
            "email": "admin@heatguard.local",
            "full_name": "HeatGuard Administrator",
            "password": "Admin@123",
            "role": RoleEnum.ADMIN,
        },
        {
            "email": "authority@heatguard.local",
            "full_name": "District Authority",
            "password": "Authority@123",
            "role": RoleEnum.AUTHORITY,
        },
        {
            "email": "analyst@heatguard.local",
            "full_name": "Heat Risk Analyst",
            "password": "Analyst@123",
            "role": RoleEnum.ANALYST,
        },
        {
            "email": "public@heatguard.local",
            "full_name": "Public User",
            "password": "Public@123",
            "role": RoleEnum.PUBLIC,
        },
    ]

    for u in demo_users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
    db.commit()
    logger.info("✓ Demo users seeded")


def seed_city_and_wards(db: Session) -> tuple:
    """Seed Jaipur city and its 25 demo wards."""
    city = db.query(City).filter(City.name == "Jaipur").first()
    if not city:
        city = City(
            name="Jaipur",
            state="Rajasthan",
            country="India",
            latitude=26.9124,
            longitude=75.7873,
            population=3073350,
            area_sq_km=484.6,
            is_active=True,
        )
        db.add(city)
        db.flush()
        logger.info("✓ Jaipur city created")

    existing_ward_count = db.query(Ward).filter(Ward.city_id == city.id).count()
    if existing_ward_count < len(JAIPUR_WARDS):
        for wd in JAIPUR_WARDS:
            existing = db.query(Ward).filter(
                Ward.city_id == city.id, Ward.ward_number == wd[0]
            ).first()
            if not existing:
                ward = Ward(
                    ward_number=wd[0],
                    ward_name=wd[1],
                    city_id=city.id,
                    latitude=wd[2],
                    longitude=wd[3],
                    area_sq_km=wd[4],
                )
                db.add(ward)
        db.flush()
        logger.info(f"✓ {len(JAIPUR_WARDS)} Jaipur wards seeded")

    db.commit()
    wards = db.query(Ward).filter(Ward.city_id == city.id).all()
    return city, wards


def seed_population_data(db: Session, wards: list):
    """Seed ward-level population and vulnerability data."""
    for i, ward in enumerate(wards):
        existing = db.query(PopulationData).filter(PopulationData.ward_id == ward.id).first()
        if existing:
            continue

        wd = JAIPUR_WARDS[i % len(JAIPUR_WARDS)]
        total_pop, elderly_pop, children_pop, outdoor_pop = wd[5], wd[6], wd[7], wd[8]
        hospitals = wd[9]
        area = ward.area_sq_km or 5.0

        vuln_inp = VulnerabilityInput(
            ward_id=ward.id,
            total_population=total_pop,
            area_sq_km=area,
            elderly_population=elderly_pop,
            children_population=children_pop,
            outdoor_worker_population=outdoor_pop,
            hospital_count_within_2km=hospitals,
        )
        vuln = calculate_vulnerability(vuln_inp)

        pop_data = PopulationData(
            ward_id=ward.id,
            total_population=total_pop,
            elderly_population=elderly_pop,
            children_population=children_pop,
            outdoor_worker_population=outdoor_pop,
            population_density=round(total_pop / area, 1),
            elderly_density=round(elderly_pop / area, 1),
            outdoor_worker_density=round(outdoor_pop / area, 1),
            vulnerability_score=vuln.vulnerability_score,
            vulnerability_level=RiskLevelEnum(vuln.vulnerability_level),
            data_source=DataSourceEnum.DEMO,
        )
        db.add(pop_data)

        # Health indicator
        hi = HealthIndicator(
            ward_id=ward.id,
            year=2024,
            heat_related_deaths=round(0.5 + (vuln.vulnerability_score / 100) * 3.5, 2),
            heat_hospitalizations=round(2.0 + (vuln.vulnerability_score / 100) * 15.0, 2),
            hospital_beds=int(50 + hospitals * 200),
            data_source=DataSourceEnum.DEMO,
            notes="DEMONSTRATION DATA — Synthetic for SIH prototype",
        )
        db.add(hi)

    db.commit()
    logger.info("✓ Population and health indicator data seeded")


def seed_weather_and_thermal(db: Session, city: City, wards: list):
    """Seed current weather and thermal metrics for all wards."""
    now = datetime.now(timezone.utc)

    # Only seed if no recent weather data
    recent = db.query(WeatherData).filter(
        WeatherData.city_id == city.id,
        WeatherData.timestamp > now - timedelta(hours=1)
    ).first()
    if recent:
        return

    for ward in wards:
        demo_wx = get_ward_weather(ward.ward_number, now)

        wx = WeatherData(
            city_id=city.id,
            ward_id=ward.id,
            timestamp=now,
            temperature=demo_wx["temperature"],
            humidity=demo_wx["humidity"],
            wind_speed=demo_wx["wind_speed"],
            solar_radiation=demo_wx["solar_radiation"],
            pressure=demo_wx.get("pressure", 1008.0),
            cloud_cover=demo_wx.get("cloud_cover", 10.0),
            latitude=ward.latitude,
            longitude=ward.longitude,
            data_source=DataSourceEnum.DEMO,
            heatwave_day_number=demo_wx.get("heatwave_day_number", 1),
        )
        db.add(wx)
        db.flush()

        # Calculate thermal metrics
        weather_input = WeatherInput(
            temperature=wx.temperature,
            humidity=wx.humidity,
            wind_speed=wx.wind_speed,
            solar_radiation=wx.solar_radiation or 700,
            heatwave_duration=wx.heatwave_day_number,
        )
        thermal = calculate_all_thermal_metrics(weather_input)

        tm = ThermalMetrics(
            weather_data_id=wx.id,
            ward_id=ward.id,
            heat_index=thermal.heat_index,
            wbgt=thermal.wbgt,
            utci=thermal.utci,
            heat_index_level=RiskLevelEnum(thermal.heat_index_level),
            wbgt_level=RiskLevelEnum(thermal.wbgt_level),
            htsi=thermal.htsi,
            htsi_level=RiskLevelEnum(thermal.htsi_level),
            htsi_temp_contribution=thermal.htsi_components.get("temperature", 0),
            htsi_humidity_contribution=thermal.htsi_components.get("humidity", 0),
            htsi_wind_contribution=thermal.htsi_components.get("wind", 0),
            htsi_solar_contribution=thermal.htsi_components.get("solar_radiation", 0),
            htsi_wbgt_contribution=thermal.htsi_components.get("wbgt", 0),
            htsi_duration_contribution=thermal.htsi_components.get("duration", 0),
        )
        db.add(tm)

    db.commit()
    logger.info("✓ Weather and thermal metrics seeded for all wards")


def seed_forecast_data(db: Session, city: City, wards: list):
    """Seed 5-day forecast for all wards."""
    now = datetime.now(timezone.utc)

    existing = db.query(ForecastData).filter(
        ForecastData.city_id == city.id,
        ForecastData.created_at > now - timedelta(hours=1)
    ).first()
    if existing:
        return

    forecast_days = get_5day_forecast(now)

    for ward in wards:
        for day_fc in forecast_days:
            wx_input = WeatherInput(
                temperature=day_fc["temperature_avg"],
                humidity=day_fc["humidity"],
                wind_speed=day_fc["wind_speed"],
                solar_radiation=day_fc.get("solar_radiation", 700),
                heatwave_duration=day_fc.get("heatwave_day_number", 1),
            )
            thermal = calculate_all_thermal_metrics(wx_input)

            fd = ForecastData(
                city_id=city.id,
                ward_id=ward.id,
                forecast_for_date=datetime.fromisoformat(day_fc["date"]).replace(tzinfo=timezone.utc),
                temperature_min=day_fc["temperature_min"],
                temperature_max=day_fc["temperature_max"],
                temperature_avg=day_fc["temperature_avg"],
                humidity=day_fc["humidity"],
                wind_speed=day_fc["wind_speed"],
                solar_radiation=day_fc.get("solar_radiation"),
                cloud_cover=day_fc.get("cloud_cover"),
                data_source=DataSourceEnum.DEMO,
                heat_index=thermal.heat_index,
                wbgt=thermal.wbgt,
                htsi=thermal.htsi,
                risk_level=RiskLevelEnum(thermal.htsi_level),
                mortality_risk_score=None,
                hospitalization_risk_score=None,
            )
            db.add(fd)

    db.commit()
    logger.info("✓ 5-day forecast data seeded")


def seed_risk_predictions(db: Session, city: City, wards: list):
    """Seed risk predictions for all wards."""
    now = datetime.now(timezone.utc)

    existing = db.query(RiskPrediction).filter(
        RiskPrediction.predicted_at > now - timedelta(hours=1)
    ).first()
    if existing:
        return

    for ward in wards:
        # Get latest weather and pop data
        wx = db.query(WeatherData).filter(
            WeatherData.ward_id == ward.id
        ).order_by(WeatherData.timestamp.desc()).first()

        if not wx:
            continue

        tm = db.query(ThermalMetrics).filter(
            ThermalMetrics.weather_data_id == wx.id
        ).first()

        pop = db.query(PopulationData).filter(
            PopulationData.ward_id == ward.id
        ).first()

        if not tm or not pop:
            continue

        risk_inp = RiskInput(
            ward_id=ward.id,
            htsi=tm.htsi or 0,
            heat_index=tm.heat_index or wx.temperature,
            wbgt=tm.wbgt or wx.temperature,
            temperature=wx.temperature,
            temperature_anomaly=wx.temperature - 28.0,
            heatwave_duration=wx.heatwave_day_number or 0,
            vulnerability_score=pop.vulnerability_score or 50,
            historical_health_indicator=50.0,
        )
        risk = calculate_health_risk(risk_inp)

        pred = RiskPrediction(
            ward_id=ward.id,
            valid_for=now,
            overall_risk_level=RiskLevelEnum(risk.overall_risk_level),
            htsi=tm.htsi,
            mortality_risk_score=risk.mortality_risk_score,
            hospitalization_risk_score=risk.hospitalization_risk_score,
            mortality_risk_level=RiskLevelEnum(risk.mortality_risk_level),
            hospitalization_risk_level=RiskLevelEnum(risk.hospitalization_risk_level),
            vulnerability_score=pop.vulnerability_score,
            temperature_anomaly=wx.temperature - 28.0,
            heatwave_duration=wx.heatwave_day_number,
            prediction_features=risk.risk_factors,
            feature_importance={
                "HTSI": 0.30, "Vulnerability": 0.25, "WBGT": 0.20,
                "Heat Index": 0.15, "Duration": 0.10
            },
        )
        db.add(pred)

    db.commit()
    logger.info("✓ Risk predictions seeded")


def seed_alerts(db: Session, wards: list):
    """Seed demo alerts for high-risk wards."""
    from app.alerts.alert_engine import evaluate_alert_rules

    existing_count = db.query(Alert).count()
    if existing_count > 0:
        return

    for ward in wards:
        rp = db.query(RiskPrediction).filter(
            RiskPrediction.ward_id == ward.id
        ).order_by(RiskPrediction.predicted_at.desc()).first()

        pop = db.query(PopulationData).filter(
            PopulationData.ward_id == ward.id
        ).first()

        if not rp or not pop:
            continue

        htsi = rp.htsi or 0
        vuln_score = pop.vulnerability_score or 0

        alert_data = evaluate_alert_rules(
            ward_id=ward.id,
            ward_name=ward.ward_name,
            htsi=htsi,
            vulnerability_score=vuln_score,
            wbgt=rp.htsi * 0.35 + 20,  # approximate
            heat_index=rp.htsi * 0.5 + 25,
            mortality_risk_score=rp.mortality_risk_score or 0,
            hospitalization_risk_score=rp.hospitalization_risk_score or 0,
        )

        if alert_data:
            alert = Alert(
                ward_id=ward.id,
                severity=RiskLevelEnum(alert_data["severity"]),
                status=AlertStatusEnum.ACTIVE,
                title=alert_data["title"],
                reason=alert_data["reason"],
                htsi_value=alert_data["htsi_value"],
                recommendations=alert_data["recommendations"],
                notification_simulated=True,
            )
            db.add(alert)

    db.commit()
    logger.info("✓ Demo alerts seeded")


def seed_infrastructure(db: Session, city: City, wards: list):
    """Seed cooling centers and hospitals."""
    if db.query(CoolingCenter).count() > 0:
        return

    cooling_centers = [
        (18, "Emergency Cooling Center — Shastri Nagar Community Hall", True),
        (17, "Sanganer Panchayat Cooling Point", False),
        (8,  "Jhotwara Municipal Rest Center", False),
        (12, "Malviya Nagar Community Center", False),
        (13, "Mansarovar Park Shelter", False),
    ]

    hospitals = [
        (11, "SMS Hospital", 2100, 180),
        (4,  "JK Lon Hospital", 800, 60),
        (6,  "Mahatma Gandhi Hospital", 500, 40),
        (2,  "Rukmani Birla Hospital", 350, 50),
        (12, "NIMS Medical College & Hospital", 600, 55),
    ]

    ward_by_number = {w.ward_number: w for w in wards}

    for wnum, name, active in cooling_centers:
        ward = ward_by_number.get(wnum)
        if ward:
            db.add(CoolingCenter(
                ward_id=ward.id,
                name=name,
                capacity=200,
                is_active=active,
                contact="1800-XXX-DEMO",
            ))

    for wnum, name, beds, icu in hospitals:
        ward = ward_by_number.get(wnum)
        if ward:
            db.add(Hospital(
                ward_id=ward.id,
                name=name,
                bed_count=beds,
                icu_beds=icu,
                contact="0141-XXX-DEMO",
            ))

    db.commit()
    logger.info("✓ Cooling centers and hospitals seeded")


def seed_model_version(db: Session):
    """Register ML model version."""
    if db.query(ModelVersion).count() > 0:
        return

    mv = ModelVersion(
        model_name="HeatGuard Risk Classifier",
        version="1.0-prototype",
        algorithm="RandomForestClassifier",
        training_date=datetime.now(timezone.utc),
        features=[
            "temperature", "humidity", "wind_speed", "solar_radiation",
            "heat_index", "wbgt", "htsi", "temperature_anomaly",
            "heatwave_duration", "population_density", "elderly_density",
            "outdoor_worker_density", "historical_health_indicator", "vulnerability_score"
        ],
        target="risk_level",
        dataset_description=(
            "5,000 synthetic samples. Labels assigned by rule-based engine. "
            "NOT real-world health data. Prototype only."
        ),
        is_active=True,
        notes="Prototype model — requires real health data for operational deployment",
    )
    db.add(mv)
    db.commit()
    logger.info("✓ Model version registered")


def run_seed():
    """Run the complete seeding process."""
    from app.database.database import SessionLocal

    logger.info("Starting database seeding...")
    create_tables()

    db = SessionLocal()
    try:
        seed_users(db)
        city, wards = seed_city_and_wards(db)
        seed_population_data(db, wards)
        seed_weather_and_thermal(db, city, wards)
        seed_forecast_data(db, city, wards)
        seed_risk_predictions(db, city, wards)
        seed_alerts(db, wards)
        seed_infrastructure(db, city, wards)
        seed_model_version(db)
        logger.info("✓ Database seeding complete")
    except Exception as e:
        logger.error(f"Seeding error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
