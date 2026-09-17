"""
HeatGuard AI — Health Risk Engine
==================================

Calculates Mortality Risk Score and Hospitalization Risk Score.

IMPORTANT DISCLAIMER:
─────────────────────
These scores are PROTOTYPE ESTIMATES for decision support.
They are NOT validated clinical predictions.
Real operational deployment requires:
  - Validated historical mortality/hospitalization datasets
  - Peer-reviewed model validation
  - Public health authority review
  - Ongoing monitoring and calibration

The system uses the terminology "Predicted Mortality Risk Score" (0–100)
rather than "predicted number of deaths" to reflect the prototype nature
of this model.

METHODOLOGY:
The scores are derived from a combination of:
  1. Thermal metrics (HTSI, WBGT, Heat Index)
  2. Temperature anomaly (deviation from seasonal normal)
  3. Heatwave duration (cumulative stress)
  4. Population vulnerability score
  5. Historical health indicator (per-ward baseline, if available)
  6. ML model prediction (when model is loaded)

In absence of a trained ML model, the rule-based fallback is used.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class RiskInput:
    ward_id: int
    htsi: float                           # 0–100
    heat_index: float                     # °C
    wbgt: float                           # °C
    temperature: float                    # °C
    temperature_anomaly: float            # Deviation from seasonal normal (°C)
    heatwave_duration: int                # Consecutive days
    vulnerability_score: float            # 0–100
    historical_health_indicator: float = 50.0  # Baseline 0–100 (50 = average)
    ml_prediction_score: Optional[float] = None  # From ML model if available


@dataclass
class RiskResult:
    ward_id: int
    overall_risk_level: str               # SAFE / LOW / MODERATE / HIGH / EXTREME
    htsi: float
    mortality_risk_score: float           # 0–100
    hospitalization_risk_score: float     # 0–100
    mortality_risk_level: str
    hospitalization_risk_level: str
    risk_factors: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    model_used: str = "rule_based"        # rule_based | ml_random_forest | ml_xgboost


# ─── Scoring weights ────────────────────────────────────────────────────────

MORTALITY_WEIGHTS = {
    "htsi": 0.30,
    "wbgt": 0.20,
    "vulnerability": 0.25,
    "temperature_anomaly": 0.10,
    "heatwave_duration": 0.10,
    "historical_indicator": 0.05,
}

HOSPITALIZATION_WEIGHTS = {
    "htsi": 0.25,
    "heat_index": 0.20,
    "vulnerability": 0.25,
    "wbgt": 0.15,
    "heatwave_duration": 0.10,
    "historical_indicator": 0.05,
}

# Reference ranges
RISK_REFS = {
    "htsi_min": 0, "htsi_max": 100,
    "wbgt_min": 15, "wbgt_max": 42,
    "heat_index_min": 27, "heat_index_max": 60,
    "anomaly_min": -5, "anomaly_max": 15,         # °C above seasonal normal
    "duration_min": 0, "duration_max": 10,
    "vuln_min": 0, "vuln_max": 100,
    "hist_min": 0, "hist_max": 100,
}


def _norm(value: float, v_min: float, v_max: float) -> float:
    if v_max == v_min:
        return 0.0
    return max(0.0, min(1.0, (value - v_min) / (v_max - v_min))) * 100.0


def calculate_health_risk(inp: RiskInput) -> RiskResult:
    """
    Calculate Mortality and Hospitalization Risk Scores.
    
    Uses rule-based weighted scoring as the baseline.
    If an ML prediction is available, it is blended with the rule-based score.
    
    Returns:
        RiskResult with scores and explanatory factors
    """
    refs = RISK_REFS

    # ── Mortality Risk ────────────────────────────────────────────────────
    m_components = {
        "htsi": _norm(inp.htsi, refs["htsi_min"], refs["htsi_max"]),
        "wbgt": _norm(inp.wbgt, refs["wbgt_min"], refs["wbgt_max"]),
        "vulnerability": _norm(inp.vulnerability_score, refs["vuln_min"], refs["vuln_max"]),
        "temperature_anomaly": _norm(inp.temperature_anomaly, refs["anomaly_min"], refs["anomaly_max"]),
        "heatwave_duration": _norm(inp.heatwave_duration, refs["duration_min"], refs["duration_max"]),
        "historical_indicator": _norm(inp.historical_health_indicator, refs["hist_min"], refs["hist_max"]),
    }
    mortality_rule = sum(m_components[k] * MORTALITY_WEIGHTS[k] for k in MORTALITY_WEIGHTS)

    # ── Hospitalization Risk ──────────────────────────────────────────────
    h_components = {
        "htsi": _norm(inp.htsi, refs["htsi_min"], refs["htsi_max"]),
        "heat_index": _norm(inp.heat_index, refs["heat_index_min"], refs["heat_index_max"]),
        "vulnerability": _norm(inp.vulnerability_score, refs["vuln_min"], refs["vuln_max"]),
        "wbgt": _norm(inp.wbgt, refs["wbgt_min"], refs["wbgt_max"]),
        "heatwave_duration": _norm(inp.heatwave_duration, refs["duration_min"], refs["duration_max"]),
        "historical_indicator": _norm(inp.historical_health_indicator, refs["hist_min"], refs["hist_max"]),
    }
    hospital_rule = sum(h_components[k] * HOSPITALIZATION_WEIGHTS[k] for k in HOSPITALIZATION_WEIGHTS)

    # ── Blend with ML prediction if available ────────────────────────────
    model_used = "rule_based"
    if inp.ml_prediction_score is not None:
        # Blend: 60% ML + 40% rule-based (ML gets more weight when available)
        mortality_score = round(0.6 * inp.ml_prediction_score + 0.4 * mortality_rule, 2)
        hospital_score = round(0.6 * (inp.ml_prediction_score * 1.05) + 0.4 * hospital_rule, 2)
        model_used = "ml_blended"
    else:
        mortality_score = round(min(100.0, max(0.0, mortality_rule)), 2)
        hospital_score = round(min(100.0, max(0.0, hospital_rule)), 2)

    mortality_level = _score_to_level(mortality_score)
    hospital_level = _score_to_level(hospital_score)
    overall_level = _score_to_level(max(inp.htsi * 0.6 + mortality_score * 0.4, mortality_score))

    # Explainability: top contributing factors
    risk_factors = {
        "HTSI": round(inp.htsi, 1),
        "WBGT": round(inp.wbgt, 1),
        "Heat Index": round(inp.heat_index, 1),
        "Vulnerability Score": round(inp.vulnerability_score, 1),
        "Temperature Anomaly (°C)": round(inp.temperature_anomaly, 1),
        "Heatwave Duration (days)": float(inp.heatwave_duration),
    }

    explanation = (
        f"Mortality risk driven by: HTSI={inp.htsi:.1f}, "
        f"WBGT={inp.wbgt:.1f}°C, Vulnerability={inp.vulnerability_score:.1f}, "
        f"Heatwave day {inp.heatwave_duration}. "
        f"Model: {model_used}. "
        "PROTOTYPE — requires validation against real health datasets."
    )

    return RiskResult(
        ward_id=inp.ward_id,
        overall_risk_level=overall_level,
        htsi=inp.htsi,
        mortality_risk_score=mortality_score,
        hospitalization_risk_score=hospital_score,
        mortality_risk_level=mortality_level,
        hospitalization_risk_level=hospital_level,
        risk_factors=risk_factors,
        explanation=explanation,
        model_used=model_used,
    )


def _score_to_level(score: float) -> str:
    if score <= 20:
        return "SAFE"
    elif score <= 40:
        return "LOW"
    elif score <= 60:
        return "MODERATE"
    elif score <= 80:
        return "HIGH"
    else:
        return "EXTREME"
