"""
HeatGuard AI — ML Model Training
==================================

IMPORTANT DISCLAIMER:
This model is trained on DEMONSTRATION/SYNTHETIC data generated from
the thermal calculation engine. It is a PROTOTYPE intended to demonstrate
the system architecture and feature pipeline.

Real-world deployment requires:
  - Validated historical health datasets (mortality/hospitalization records)
  - Domain expert validation
  - Proper train/test splits on real data
  - Model monitoring and retraining pipelines

DO NOT use accuracy metrics from this prototype as evidence of
real-world predictive performance.

Model: Random Forest Classifier (primary) + XGBoost (comparison)
Target: Risk category (SAFE / LOW / MODERATE / HIGH / EXTREME)
"""
import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

logger = logging.getLogger(__name__)

# Feature columns used for training
FEATURE_COLUMNS = [
    "temperature",
    "humidity",
    "wind_speed",
    "solar_radiation",
    "heat_index",
    "wbgt",
    "htsi",
    "temperature_anomaly",
    "heatwave_duration",
    "population_density",
    "elderly_density",
    "outdoor_worker_density",
    "historical_health_indicator",
    "vulnerability_score",
]

TARGET_COLUMN = "risk_level"
RISK_CLASSES = ["SAFE", "LOW", "MODERATE", "HIGH", "EXTREME"]
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))


def generate_synthetic_training_data(n_samples: int = 5000) -> pd.DataFrame:
    """
    Generate synthetic training data using domain knowledge and thermal engine.
    
    Data is generated deterministically with RANDOM_SEED so results are reproducible.
    Labels are assigned using the rule-based risk engine to ensure consistency
    between the ML model and the rule-based fallback.
    
    SOURCE: SYNTHETIC/DEMONSTRATION DATA
    Do NOT interpret as real-world statistics.
    """
    from app.thermal.thermal_engine import (
        WeatherInput, calculate_all_thermal_metrics
    )
    from app.risk.vulnerability import VulnerabilityInput, calculate_vulnerability
    from app.risk.risk_engine import RiskInput, calculate_health_risk

    rng = np.random.default_rng(RANDOM_SEED)
    records = []

    # Generate diverse scenarios representative of Jaipur summer conditions
    for i in range(n_samples):
        # Temperature range: 25–48°C (Jaipur summer range)
        temp = float(rng.uniform(25, 48))
        # Humidity range: 15–90%
        humidity = float(rng.uniform(15, 90))
        # Wind: 0–35 km/h
        wind = float(rng.uniform(0, 35))
        # Solar radiation: 0–1050 W/m²
        solar = float(rng.uniform(0, 1050))
        # Heatwave duration: 0–10 days
        hw_dur = int(rng.integers(0, 11))
        # Temperature anomaly: -3 to +12°C
        anomaly = float(rng.uniform(-3, 12))

        # Demographics
        pop_density = float(rng.uniform(500, 14000))
        elderly_density = float(rng.uniform(20, 450))
        outdoor_worker_density = float(rng.uniform(10, 750))
        historical_health = float(rng.uniform(20, 90))

        # Calculate thermal metrics
        weather = WeatherInput(
            temperature=temp, humidity=humidity, wind_speed=wind,
            solar_radiation=solar, heatwave_duration=hw_dur
        )
        thermal = calculate_all_thermal_metrics(weather)

        # Calculate vulnerability
        area = float(rng.uniform(1, 15))
        total_pop = int(pop_density * area)
        vuln_inp = VulnerabilityInput(
            ward_id=1,
            total_population=total_pop,
            area_sq_km=area,
            elderly_population=int(elderly_density * area),
            children_population=int(total_pop * 0.25),
            outdoor_worker_population=int(outdoor_worker_density * area),
            hospital_count_within_2km=int(rng.integers(0, 5)),
        )
        vuln = calculate_vulnerability(vuln_inp)

        # Calculate risk (ground truth label)
        risk_inp = RiskInput(
            ward_id=1,
            htsi=thermal.htsi,
            heat_index=thermal.heat_index,
            wbgt=thermal.wbgt,
            temperature=temp,
            temperature_anomaly=anomaly,
            heatwave_duration=hw_dur,
            vulnerability_score=vuln.vulnerability_score,
            historical_health_indicator=historical_health,
        )
        risk = calculate_health_risk(risk_inp)

        records.append({
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind,
            "solar_radiation": solar,
            "heat_index": thermal.heat_index,
            "wbgt": thermal.wbgt,
            "htsi": thermal.htsi,
            "temperature_anomaly": anomaly,
            "heatwave_duration": float(hw_dur),
            "population_density": pop_density,
            "elderly_density": elderly_density,
            "outdoor_worker_density": outdoor_worker_density,
            "historical_health_indicator": historical_health,
            "vulnerability_score": vuln.vulnerability_score,
            "risk_level": risk.overall_risk_level,
        })

    df = pd.DataFrame(records)
    logger.info(f"Generated {len(df)} synthetic training samples")
    logger.info(f"Risk distribution:\n{df['risk_level'].value_counts()}")
    return df


def train_and_save_model(model_dir: str = "app/ml/models") -> dict:
    """
    Train Random Forest model and save to disk.
    
    Returns:
        dict with model metadata and evaluation results
    """
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "risk_model.pkl")
    metadata_path = os.path.join(model_dir, "model_metadata.json")

    logger.info("Starting ML model training on synthetic demonstration data...")
    logger.warning(
        "PROTOTYPE MODEL: Trained on synthetic data. "
        "Real-world deployment requires validated historical health datasets."
    )

    # Generate data
    df = generate_synthetic_training_data(n_samples=5000)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # Encode labels
    le = LabelEncoder()
    le.fit(RISK_CLASSES)
    y_encoded = le.transform(y)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=RANDOM_SEED, stratify=y_encoded
    )

    # ─── Random Forest ────────────────────────────────────────────────
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=5,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        class_weight="balanced",
    )
    rf_model.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = rf_model.predict(X_test)
    test_accuracy = float(accuracy_score(y_test, y_pred))
    cv_scores = cross_val_score(rf_model, X, y_encoded, cv=5, scoring="accuracy")

    report = classification_report(
        y_test, y_pred,
        target_names=le.classes_,
        output_dict=True,
        zero_division=0,
    )

    # Feature importance
    feature_importance = dict(
        sorted(
            zip(FEATURE_COLUMNS, rf_model.feature_importances_.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )
    )

    # ─── XGBoost comparison (optional) ───────────────────────────────
    xgb_metrics = {}
    if XGBOOST_AVAILABLE:
        try:
            xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=RANDOM_SEED,
                eval_metric="mlogloss",
                use_label_encoder=False,
            )
            xgb_model.fit(X_train, y_train)
            xgb_pred = xgb_model.predict(X_test)
            xgb_accuracy = float(accuracy_score(y_test, xgb_pred))
            xgb_metrics = {"xgboost_test_accuracy": xgb_accuracy}
            logger.info(f"XGBoost test accuracy (on synthetic data): {xgb_accuracy:.3f}")
        except Exception as e:
            logger.warning(f"XGBoost training failed: {e}")

    # Save model
    model_bundle = {
        "model": rf_model,
        "label_encoder": le,
        "feature_columns": FEATURE_COLUMNS,
        "classes": RISK_CLASSES,
    }
    joblib.dump(model_bundle, model_path)
    logger.info(f"Model saved to {model_path}")

    # Save metadata
    metadata = {
        "model_name": "HeatGuard Risk Classifier",
        "version": "1.0-prototype",
        "algorithm": "RandomForestClassifier",
        "training_date": datetime.now(timezone.utc).isoformat(),
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "classes": RISK_CLASSES,
        "n_training_samples": 5000,
        "random_seed": RANDOM_SEED,
        "evaluation": {
            "WARNING": (
                "All metrics are evaluated on SYNTHETIC demonstration data. "
                "They do not reflect real-world predictive performance."
            ),
            "test_accuracy_on_synthetic_data": round(test_accuracy, 4),
            "cv_mean_accuracy_on_synthetic_data": round(float(cv_scores.mean()), 4),
            "cv_std": round(float(cv_scores.std()), 4),
            **xgb_metrics,
        },
        "feature_importance": feature_importance,
        "dataset_description": (
            "5,000 synthetic samples generated using deterministic thermal calculations. "
            "Labels assigned by rule-based risk engine. "
            "NOT real-world health data."
        ),
        "model_path": model_path,
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Test accuracy (synthetic data only): {test_accuracy:.3f}")
    logger.info(f"Feature importance: {list(feature_importance.keys())[:5]}")

    return metadata


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = train_and_save_model()
    print("Training complete:", result["evaluation"])
