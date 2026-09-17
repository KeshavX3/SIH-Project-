"""
HeatGuard AI — ML Prediction Service
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
import numpy as np
import joblib

logger = logging.getLogger(__name__)

_model_bundle = None
_model_metadata = None


def load_model(model_path: str = None) -> bool:
    """Load the trained model from disk. Returns True if successful."""
    global _model_bundle, _model_metadata

    if model_path is None:
        model_path = os.getenv("ML_MODEL_PATH", "app/ml/models/risk_model.pkl")

    try:
        _model_bundle = joblib.load(model_path)
        metadata_path = model_path.replace("risk_model.pkl", "model_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path) as f:
                _model_metadata = json.load(f)
        logger.info(f"✓ ML model loaded from {model_path}")
        return True
    except FileNotFoundError:
        logger.warning(f"ML model not found at {model_path}. Training now...")
        try:
            from app.ml.training.train import train_and_save_model
            _model_metadata = train_and_save_model(os.path.dirname(model_path))
            _model_bundle = joblib.load(model_path)
            logger.info("✓ ML model trained and loaded")
            return True
        except Exception as e:
            logger.error(f"ML model training failed: {e}")
            return False
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        return False


def is_model_loaded() -> bool:
    return _model_bundle is not None


def predict_risk(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Predict risk level from feature dictionary.
    
    Args:
        features: Dict with keys matching FEATURE_COLUMNS
    
    Returns:
        dict with predicted_class, probability, feature_importance
    """
    if _model_bundle is None:
        load_model()

    if _model_bundle is None:
        return {
            "success": False,
            "error": "ML model not available",
            "predicted_class": None,
            "risk_score": None,
        }

    model = _model_bundle["model"]
    le = _model_bundle["label_encoder"]
    feature_columns = _model_bundle["feature_columns"]

    # Build feature array in correct order
    feature_values = []
    for col in feature_columns:
        val = features.get(col, 0.0)
        feature_values.append(float(val))

    X = np.array([feature_values])

    try:
        pred_encoded = model.predict(X)[0]
        pred_proba = model.predict_proba(X)[0]
        pred_class = le.inverse_transform([pred_encoded])[0]

        # Risk score: weighted sum of class probabilities
        class_weights = {"SAFE": 0, "LOW": 25, "MODERATE": 50, "HIGH": 75, "EXTREME": 100}
        classes = le.classes_
        risk_score = sum(
            pred_proba[i] * class_weights.get(cls, 50)
            for i, cls in enumerate(classes)
        )

        # Feature importance for this model
        feature_imp = {}
        if hasattr(model, "feature_importances_"):
            for i, col in enumerate(feature_columns):
                feature_imp[col] = float(model.feature_importances_[i])

        return {
            "success": True,
            "predicted_class": pred_class,
            "risk_score": round(risk_score, 2),
            "class_probabilities": {
                cls: round(float(pred_proba[i]), 4)
                for i, cls in enumerate(classes)
            },
            "feature_importance": dict(
                sorted(feature_imp.items(), key=lambda x: x[1], reverse=True)
            ),
            "model_version": _model_metadata.get("version", "unknown") if _model_metadata else "unknown",
            "disclaimer": (
                "Prototype model trained on synthetic data. "
                "Real-world deployment requires validated historical health datasets."
            ),
        }
    except Exception as e:
        logger.error(f"ML prediction error: {e}")
        return {"success": False, "error": str(e), "predicted_class": None}


def get_model_info() -> Dict[str, Any]:
    """Return model metadata for the admin panel."""
    if _model_metadata:
        return {
            "loaded": True,
            "model_name": _model_metadata.get("model_name"),
            "version": _model_metadata.get("version"),
            "algorithm": _model_metadata.get("algorithm"),
            "training_date": _model_metadata.get("training_date"),
            "features": _model_metadata.get("features"),
            "evaluation": _model_metadata.get("evaluation"),
            "feature_importance": _model_metadata.get("feature_importance"),
            "dataset_description": _model_metadata.get("dataset_description"),
        }
    return {"loaded": False}
