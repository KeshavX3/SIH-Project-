"""
HeatGuard AI — Alert Engine
=============================

Rule-based configurable alert generation.

Rules:
  IF HTSI >= 81 → EXTREME ALERT
  IF HTSI >= 61 AND vulnerability >= 60 → HIGH PRIORITY ALERT
  IF HTSI >= 41 AND vulnerability >= 70 → MODERATE ALERT

All thresholds are configurable via settings.
Recommendations depend on risk level.
"""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ─── Recommendation lookup ─────────────────────────────────────────────────

RECOMMENDATIONS = {
    "SAFE": [
        "Continue routine monitoring",
        "Maintain weather observation schedule",
        "Update public advisories as needed",
    ],
    "LOW": [
        "Issue public hydration advisory",
        "Monitor vulnerable populations (elderly, children)",
        "Ensure public drinking water is available",
        "Alert community health workers",
    ],
    "MODERATE": [
        "Issue public heat advisory",
        "Open community cooling areas",
        "Increase drinking water distribution",
        "Advise outdoor workers to take breaks",
        "Alert hospitals and clinics to prepare",
        "Monitor elderly and outdoor workers closely",
    ],
    "HIGH": [
        "🚨 Issue formal heat warning",
        "Open cooling centers in ward",
        "Prepare healthcare facilities for heat cases",
        "Notify outdoor employers to adjust work schedules",
        "Deploy mobile water distribution teams",
        "Alert emergency services",
        "Monitor critical infrastructure power demand",
        "Broadcast public warnings via all channels",
    ],
    "EXTREME": [
        "🔴 ACTIVATE HEAT ACTION PLAN",
        "Open emergency cooling centers",
        "Issue regional extreme heat alert",
        "Increase hospital preparedness to maximum level",
        "Suspend non-essential outdoor work",
        "Deploy water stations throughout ward",
        "Mobilize community health workers for door-to-door monitoring",
        "Coordinate with power utility to prevent outages",
        "Activate elderly and vulnerable population monitoring protocol",
        "Notify district authorities and state health department",
    ],
}


def generate_alert_reason(htsi: float, risk_level: str, vulnerability_score: float,
                           ward_name: str, wbgt: float, heat_index: float) -> str:
    """Generate human-readable alert reason."""
    reasons = []

    if htsi >= 81:
        reasons.append(f"Extreme thermal stress (HTSI={htsi:.1f}/100)")
    elif htsi >= 61:
        reasons.append(f"High thermal stress (HTSI={htsi:.1f}/100)")
    elif htsi >= 41:
        reasons.append(f"Moderate thermal stress (HTSI={htsi:.1f}/100)")

    if vulnerability_score >= 70:
        reasons.append(f"high population vulnerability ({vulnerability_score:.0f}/100)")
    elif vulnerability_score >= 50:
        reasons.append(f"moderate population vulnerability ({vulnerability_score:.0f}/100)")

    if wbgt >= 32:
        reasons.append(f"dangerous WBGT ({wbgt:.1f}°C)")

    if heat_index >= 40:
        reasons.append(f"extreme apparent temperature ({heat_index:.1f}°C)")

    reason_str = " combined with ".join(reasons) if reasons else "heat risk conditions"
    return f"{ward_name}: {reason_str.capitalize()}."


def evaluate_alert_rules(
    ward_id: int,
    ward_name: str,
    htsi: float,
    vulnerability_score: float,
    wbgt: float,
    heat_index: float,
    mortality_risk_score: float,
    hospitalization_risk_score: float,
) -> Optional[Dict[str, Any]]:
    """
    Evaluate configurable alert rules.
    
    Returns an alert dict if any rule triggers, otherwise None.
    
    Rule priority (highest first):
      EXTREME: HTSI >= 81
      HIGH:    HTSI >= 61 AND vulnerability >= 60
      MODERATE: HTSI >= 41 AND vulnerability >= 70
    """
    severity = None

    if htsi >= 81.0:
        severity = "EXTREME"
    elif htsi >= 61.0 and vulnerability_score >= 60.0:
        severity = "HIGH"
    elif htsi >= 41.0 and vulnerability_score >= 70.0:
        severity = "MODERATE"

    if severity is None:
        return None

    reason = generate_alert_reason(
        htsi, severity, vulnerability_score, ward_name, wbgt, heat_index
    )

    return {
        "ward_id": ward_id,
        "ward_name": ward_name,
        "severity": severity,
        "title": f"{severity} HEAT ALERT — {ward_name}",
        "reason": reason,
        "htsi_value": round(htsi, 2),
        "recommendations": RECOMMENDATIONS.get(severity, []),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "ACTIVE",
        "metrics": {
            "htsi": round(htsi, 2),
            "wbgt": round(wbgt, 2),
            "heat_index": round(heat_index, 2),
            "vulnerability_score": round(vulnerability_score, 2),
            "mortality_risk_score": round(mortality_risk_score, 2),
            "hospitalization_risk_score": round(hospitalization_risk_score, 2),
        },
    }


def get_recommendations(risk_level: str) -> List[str]:
    """Get recommendations for a given risk level."""
    return RECOMMENDATIONS.get(risk_level, RECOMMENDATIONS["SAFE"])
