"""
HeatGuard AI — Thermal Stress Engine
=====================================

Implements recognized thermal-comfort and heat-stress metrics.

SCIENTIFIC TRANSPARENCY:
────────────────────────
1. Heat Index      — NOAA/NWS Rothfusz regression (1990)
2. WBGT            — Bernard & Pourmoghani (1999) approximation
                     (for outdoor conditions without direct globe/psychrometric measurements)
3. UTCI            — Simplified linear approximation (not full 6-node model)
4. HTSI            — Project-specific composite prototype index (0–100)
                     NOT an internationally standardized medical index.

All thresholds and weights are configurable prototype values.
Deployment in public-health decision-making requires validation
against domain-expert review and high-quality health datasets.
"""
import math
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data class for thermal computation inputs
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class WeatherInput:
    temperature: float          # °C
    humidity: float             # % (0–100)
    wind_speed: float           # km/h
    solar_radiation: float      # W/m²
    pressure: float = 1013.25   # hPa
    cloud_cover: float = 0.0    # % (0–100)
    heatwave_duration: int = 0  # consecutive heatwave days


@dataclass
class ThermalResult:
    # Input
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: float

    # Standard thermal indices
    heat_index: float = 0.0
    wbgt: float = 0.0
    utci: float = 0.0

    # Risk classifications for standard indices
    heat_index_level: str = "SAFE"
    wbgt_level: str = "SAFE"

    # Project-specific composite index
    htsi: float = 0.0
    htsi_level: str = "SAFE"

    # HTSI component breakdown (for explainability)
    htsi_components: Dict[str, float] = field(default_factory=dict)

    # Metadata
    methodology_notes: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# 1. HEAT INDEX — NOAA/NWS Rothfusz Regression
# ─────────────────────────────────────────────────────────────────────────────

def calculate_heat_index(temp_c: float, rh: float) -> float:
    """
    Calculate Heat Index using the NOAA/NWS Rothfusz regression equation.
    
    Source: Rothfusz, L.P. (1990). The Heat Index Equation.
            NWS Technical Attachment SR/SSD 90-23.
    
    Args:
        temp_c: Air temperature in Celsius
        rh: Relative humidity in percent (0–100)
    
    Returns:
        Heat Index in Celsius
    
    Notes:
        - Valid range: temp ≥ 27°C, RH ≥ 40%
        - Below these thresholds, returns ambient temperature
        - Represents apparent temperature (perceived heat under given humidity)
    """
    if temp_c < 27.0:
        return temp_c  # Heat Index not meaningful at cooler temperatures

    # Convert to Fahrenheit for Rothfusz regression
    T = temp_c * 9 / 5 + 32
    RH = rh

    # Rothfusz regression coefficients
    HI = (
        -42.379
        + 2.04901523 * T
        + 10.14333127 * RH
        - 0.22475541 * T * RH
        - 0.00683783 * T * T
        - 0.05481717 * RH * RH
        + 0.00122874 * T * T * RH
        + 0.00085282 * T * RH * RH
        - 0.00000199 * T * T * RH * RH
    )

    # Adjustment for low humidity (RH < 13%, T between 80–112°F)
    if RH < 13 and 80 <= T <= 112:
        adjustment = ((13 - RH) / 4) * math.sqrt((17 - abs(T - 95)) / 17)
        HI -= adjustment
    # Adjustment for high humidity (RH > 85%, T between 80–87°F)
    elif RH > 85 and 80 <= T <= 87:
        adjustment = ((RH - 85) / 10) * ((87 - T) / 5)
        HI += adjustment

    # Convert back to Celsius
    hi_celsius = (HI - 32) * 5 / 9

    # Heat Index should not be less than air temperature
    return max(hi_celsius, temp_c)


def classify_heat_index(hi_c: float) -> str:
    """
    Classify Heat Index level based on NWS categories.
    
    NWS Heat Index thresholds (adapted to Celsius):
    < 27°C      — Normal (no heat stress level assigned)
    27–32°C     — Caution (LOW)
    32–39°C     — Extreme Caution (MODERATE)
    39–51°C     — Danger (HIGH)
    > 51°C      — Extreme Danger (EXTREME)
    """
    if hi_c < 27:
        return "SAFE"
    elif hi_c < 32:
        return "LOW"
    elif hi_c < 39:
        return "MODERATE"
    elif hi_c < 51:
        return "HIGH"
    else:
        return "EXTREME"


# ─────────────────────────────────────────────────────────────────────────────
# 2. WET-BULB GLOBE TEMPERATURE (WBGT)
# ─────────────────────────────────────────────────────────────────────────────

def calculate_wet_bulb_temperature(temp_c: float, rh: float) -> float:
    """
    Estimate natural wet-bulb temperature using the Stull (2011) formula.
    
    Source: Stull, R. (2011). Wet-Bulb Temperature from Relative Humidity
            and Air Temperature. Journal of Applied Meteorology and Climatology, 50, 2267–2269.
    
    This is an approximation; actual wet-bulb temperature requires a
    psychrometer or direct measurement.
    
    Args:
        temp_c: Air temperature °C
        rh: Relative humidity % (0–100)
    
    Returns:
        Estimated wet-bulb temperature °C
    """
    Tw = (
        temp_c * math.atan(0.151977 * math.sqrt(rh + 8.313659))
        + math.atan(temp_c + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838 * rh ** 1.5 * math.atan(0.023101 * rh)
        - 4.686035
    )
    return Tw


def calculate_globe_temperature(temp_c: float, solar_rad: float, wind_speed_ms: float) -> float:
    """
    Estimate black-globe temperature from ambient conditions.
    
    Based on: Hunter, C.H., & Minyard, C.O. (1999).
              Estimating wet bulb globe temperature using standard meteorological measurements.
    
    This is an approximation for a standard 150mm black globe thermometer.
    A direct measurement is always preferred.
    
    Args:
        temp_c: Air temperature °C
        solar_rad: Solar irradiance W/m²
        wind_speed_ms: Wind speed m/s
    
    Returns:
        Estimated globe temperature °C
    """
    # Globe temperature is higher than air temp by an amount depending on solar load
    # and convective cooling from wind
    if solar_rad <= 0:
        return temp_c

    # Simplified estimation — globe temp rises with solar radiation and falls with wind
    delta = (solar_rad * 0.008) - (wind_speed_ms * 0.9)
    globe_temp = temp_c + max(0, delta)
    return globe_temp


def calculate_wbgt(temp_c: float, rh: float, solar_rad: float, wind_speed_kmh: float) -> float:
    """
    Calculate Wet-Bulb Globe Temperature (WBGT) for outdoor conditions.
    
    Outdoor WBGT formula:
        WBGT = 0.7 × Tw + 0.2 × Tg + 0.1 × Ta
    
    Where:
        Tw = natural wet-bulb temperature (approximated)
        Tg = globe temperature (approximated)
        Ta = air (dry-bulb) temperature
    
    Source: Yaglou, C.P., & Minard, D. (1957).
            Control of Heat Casualties at Military Training Centers.
            Archives of Industrial Health, 16, 302–316.
    
    ASSUMPTIONS:
    - Outdoor environment with full solar exposure
    - Globe temperature is estimated (not directly measured)
    - Wet-bulb temperature uses Stull (2011) approximation
    - Wind speed converted from km/h to m/s
    
    This is a standard-methodology approximation appropriate for prototype use.
    
    Args:
        temp_c: Air temperature °C
        rh: Relative humidity %
        solar_rad: Solar irradiance W/m²
        wind_speed_kmh: Wind speed km/h
    
    Returns:
        WBGT °C (approximated for outdoor conditions)
    """
    wind_ms = wind_speed_kmh / 3.6

    Tw = calculate_wet_bulb_temperature(temp_c, rh)
    Tg = calculate_globe_temperature(temp_c, solar_rad, wind_ms)
    Ta = temp_c

    wbgt = 0.7 * Tw + 0.2 * Tg + 0.1 * Ta
    return round(wbgt, 2)


def classify_wbgt(wbgt: float) -> str:
    """
    Classify WBGT into risk levels.
    
    Based on ISO 7933 / ACGIH TLV guidelines (approximate):
    < 25°C    — SAFE (no restriction for acclimatized workers)
    25–28°C   — LOW (light work, with breaks)
    28–32°C   — MODERATE (moderate work restriction)
    32–36°C   — HIGH (heavy work restricted)
    > 36°C    — EXTREME (work cessation recommended)
    
    These thresholds are adapted from occupational health guidelines.
    Actual application depends on work intensity and acclimatization status.
    """
    if wbgt < 25:
        return "SAFE"
    elif wbgt < 28:
        return "LOW"
    elif wbgt < 32:
        return "MODERATE"
    elif wbgt < 36:
        return "HIGH"
    else:
        return "EXTREME"


# ─────────────────────────────────────────────────────────────────────────────
# 3. UTCI (Simplified approximation)
# ─────────────────────────────────────────────────────────────────────────────

def calculate_utci_simplified(temp_c: float, rh: float, wind_speed_kmh: float, solar_rad: float) -> float:
    """
    Simplified UTCI approximation.
    
    IMPORTANT: The full UTCI computation requires a 6-node thermoregulation model
    with clothing insulation, mean radiant temperature from all surfaces, and
    vapour pressure calculations. The full polynomial approximation by
    Bröde et al. (2012) has 210 coefficients.
    
    This simplified version uses the linear approximation approach for
    prototype demonstration purposes. It should NOT be used for operational
    public-health decisions without implementing the full Fiala/Bröde model.
    
    Reference:
    Bröde, P. et al. (2012). Deriving the operational procedure for the
    Universal Thermal Climate Index (UTCI). International Journal of
    Biometeorology, 56(3), 481–494.
    
    Returns:
        Approximate UTCI equivalent temperature °C
    """
    wind_ms = wind_speed_kmh / 3.6

    # Estimate mean radiant temperature from solar radiation
    # (simplified — real MRT requires surrounding surface temperatures)
    mrt = temp_c + (solar_rad * 0.005) - (wind_ms * 0.5)

    # Vapour pressure (hPa) from T and RH
    vp = (rh / 100.0) * 6.105 * math.exp(17.27 * temp_c / (temp_c + 237.3))

    # Simplified UTCI approximation
    utci = temp_c + 0.33 * vp - 0.70 * wind_ms + 0.15 * (mrt - temp_c) - 4.0

    return round(utci, 2)


# ─────────────────────────────────────────────────────────────────────────────
# 4. HUMAN THERMAL STRESS INDEX (HTSI)
# ─────────────────────────────────────────────────────────────────────────────
#
# DISCLAIMER: HTSI is a project-specific composite prototype index created
# for HeatGuard AI (SIH26083). It is NOT an internationally standardized
# medical index. It should be treated as a decision-support tool pending
# validation against historical health data and domain-expert review.
#
# METHODOLOGY:
# HTSI is a weighted composite of normalized thermal and exposure factors.
# Each component is normalized to [0, 100] and combined with empirically
# chosen weights. The thresholds and weights are configurable for tuning
# against local conditions.

# HTSI component weights — must sum to 1.0
HTSI_WEIGHTS = {
    "temperature": 0.25,        # Ambient temperature (primary driver)
    "humidity": 0.20,           # Relative humidity (major modifier)
    "wbgt": 0.20,               # WBGT (integrated thermal exposure)
    "solar_radiation": 0.15,    # Solar heat load
    "wind": 0.10,               # Wind cooling (inverse effect)
    "duration": 0.10,           # Heatwave duration (cumulative stress)
}

# Reference ranges for normalization (Jaipur summer context)
HTSI_REFS = {
    "temp_min": 20.0, "temp_max": 50.0,        # °C
    "humidity_min": 10.0, "humidity_max": 100.0,
    "wbgt_min": 15.0, "wbgt_max": 40.0,
    "solar_min": 0.0, "solar_max": 1100.0,      # W/m²
    "wind_min": 0.0, "wind_max": 40.0,          # km/h (high wind = cooling)
    "duration_min": 0, "duration_max": 10,       # days
}


def normalize(value: float, v_min: float, v_max: float, inverse: bool = False) -> float:
    """Normalize value to [0, 100] range. If inverse=True, lower value → higher score."""
    if v_max == v_min:
        return 0.0
    score = (value - v_min) / (v_max - v_min)
    score = max(0.0, min(1.0, score))
    if inverse:
        score = 1.0 - score
    return score * 100.0


def calculate_htsi(
    temp_c: float,
    rh: float,
    wind_speed_kmh: float,
    solar_rad: float,
    wbgt: float,
    heatwave_duration: int = 0,
) -> tuple[float, dict]:
    """
    Calculate Human Thermal Stress Index (HTSI).
    
    This is HeatGuard AI's project-specific composite prototype index.
    It combines multiple thermal and exposure factors into a single 0–100 score.
    
    Components:
        - Temperature:     Normalized ambient temperature
        - Humidity:        Normalized relative humidity
        - WBGT:            Normalized wet-bulb globe temperature
        - Solar Radiation: Normalized solar irradiance
        - Wind:            Inverse-normalized wind speed (high wind = cooling = low score)
        - Duration:        Normalized consecutive heatwave day count
    
    Returns:
        Tuple of (htsi_score 0–100, component_breakdown dict)
    """
    refs = HTSI_REFS
    weights = HTSI_WEIGHTS

    components = {
        "temperature": normalize(temp_c, refs["temp_min"], refs["temp_max"]),
        "humidity": normalize(rh, refs["humidity_min"], refs["humidity_max"]),
        "wbgt": normalize(wbgt, refs["wbgt_min"], refs["wbgt_max"]),
        "solar_radiation": normalize(solar_rad, refs["solar_min"], refs["solar_max"]),
        "wind": normalize(wind_speed_kmh, refs["wind_min"], refs["wind_max"], inverse=True),
        "duration": normalize(heatwave_duration, refs["duration_min"], refs["duration_max"]),
    }

    # Weighted sum
    htsi = sum(components[k] * weights[k] for k in weights)
    htsi = round(min(100.0, max(0.0, htsi)), 2)

    # Component contributions (weighted score per component)
    contributions = {k: round(components[k] * weights[k], 2) for k in weights}

    return htsi, contributions


def classify_htsi(htsi: float) -> str:
    """
    Classify HTSI into prototype risk categories.
    
    Scale:
        0–20    SAFE
        21–40   LOW
        41–60   MODERATE
        61–80   HIGH
        81–100  EXTREME
    
    Note: These thresholds are configurable prototype categories.
    They are not medically authoritative without validation.
    """
    if htsi <= settings.HTSI_SAFE_MAX:
        return "SAFE"
    elif htsi <= settings.HTSI_LOW_MAX:
        return "LOW"
    elif htsi <= settings.HTSI_MODERATE_MAX:
        return "MODERATE"
    elif htsi <= settings.HTSI_HIGH_MAX:
        return "HIGH"
    else:
        return "EXTREME"


# ─────────────────────────────────────────────────────────────────────────────
# Master calculation function
# ─────────────────────────────────────────────────────────────────────────────

def calculate_all_thermal_metrics(weather: WeatherInput) -> ThermalResult:
    """
    Calculate all thermal metrics from a weather observation.
    
    This is the main entry point for the thermal calculation engine.
    Produces Heat Index, WBGT, UTCI (simplified), and HTSI.
    """
    # 1. Heat Index
    hi = calculate_heat_index(weather.temperature, weather.humidity)
    hi_level = classify_heat_index(hi)

    # 2. WBGT
    wbgt = calculate_wbgt(
        weather.temperature,
        weather.humidity,
        weather.solar_radiation,
        weather.wind_speed,
    )
    wbgt_level = classify_wbgt(wbgt)

    # 3. UTCI (simplified)
    utci = calculate_utci_simplified(
        weather.temperature,
        weather.humidity,
        weather.wind_speed,
        weather.solar_radiation,
    )

    # 4. HTSI (project-specific)
    htsi, htsi_components = calculate_htsi(
        weather.temperature,
        weather.humidity,
        weather.wind_speed,
        weather.solar_radiation,
        wbgt,
        weather.heatwave_duration,
    )
    htsi_level = classify_htsi(htsi)

    result = ThermalResult(
        temperature=weather.temperature,
        humidity=weather.humidity,
        wind_speed=weather.wind_speed,
        solar_radiation=weather.solar_radiation,
        heat_index=round(hi, 2),
        wbgt=round(wbgt, 2),
        utci=round(utci, 2),
        heat_index_level=hi_level,
        wbgt_level=wbgt_level,
        htsi=htsi,
        htsi_level=htsi_level,
        htsi_components=htsi_components,
        methodology_notes=(
            "Heat Index: NOAA/NWS Rothfusz (1990) regression. "
            "WBGT: Outdoor approximation using Stull (2011) wet-bulb + Hunter & Minyard (1999) globe temp estimation. "
            "UTCI: Simplified linear approximation (not full Bröde 2012 polynomial). "
            "HTSI: Project-specific composite prototype index — NOT an international standard."
        ),
    )

    return result
