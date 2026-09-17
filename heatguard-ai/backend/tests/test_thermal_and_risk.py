"""
HeatGuard AI — Test Suite
Tests for thermal calculations, HTSI, risk classification, and alert rules.
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.thermal.thermal_engine import (
    calculate_heat_index,
    classify_heat_index,
    calculate_wbgt,
    classify_wbgt,
    calculate_htsi,
    classify_htsi,
    calculate_all_thermal_metrics,
    WeatherInput,
)
from app.risk.vulnerability import VulnerabilityInput, calculate_vulnerability
from app.risk.risk_engine import RiskInput, calculate_health_risk
from app.alerts.alert_engine import evaluate_alert_rules


# ─── Heat Index Tests ────────────────────────────────────────────────────────

class TestHeatIndex:
    def test_heat_index_below_threshold(self):
        """Below 27°C, Heat Index equals ambient temperature."""
        hi = calculate_heat_index(25.0, 60.0)
        assert hi == 25.0

    def test_heat_index_hot_humid(self):
        """43°C + 62% humidity should produce extreme apparent temperature."""
        hi = calculate_heat_index(43.0, 62.0)
        assert hi > 43.0, "Heat Index should exceed air temp under high humidity"
        assert hi > 50.0, "Under extreme Jaipur conditions, HI should be very high"

    def test_heat_index_hot_dry(self):
        """43°C + 20% humidity: HI still above ambient but less extreme."""
        hi = calculate_heat_index(43.0, 20.0)
        assert hi >= 43.0

    def test_heat_index_classification_extreme(self):
        hi = calculate_heat_index(47.0, 70.0)
        level = classify_heat_index(hi)
        assert level in ["HIGH", "EXTREME"]

    def test_heat_index_classification_safe(self):
        level = classify_heat_index(25.0)
        assert level == "SAFE"

    def test_heat_index_classification_moderate(self):
        level = classify_heat_index(35.0)
        assert level == "MODERATE"


# ─── WBGT Tests ─────────────────────────────────────────────────────────────

class TestWBGT:
    def test_wbgt_increases_with_solar_radiation(self):
        """Higher solar radiation should increase WBGT."""
        wbgt_low = calculate_wbgt(40.0, 50.0, 0.0, 10.0)
        wbgt_high = calculate_wbgt(40.0, 50.0, 900.0, 10.0)
        assert wbgt_high > wbgt_low

    def test_wbgt_decreases_with_wind(self):
        """Higher wind speed should reduce WBGT (convective cooling)."""
        wbgt_calm = calculate_wbgt(40.0, 50.0, 700.0, 0.0)
        wbgt_windy = calculate_wbgt(40.0, 50.0, 700.0, 30.0)
        assert wbgt_calm >= wbgt_windy

    def test_wbgt_extreme_conditions(self):
        """Extreme Jaipur heatwave conditions should produce HIGH+ WBGT."""
        wbgt = calculate_wbgt(43.0, 62.0, 860.0, 5.5)
        level = classify_wbgt(wbgt)
        assert level in ["HIGH", "EXTREME"]

    def test_wbgt_classification_boundaries(self):
        assert classify_wbgt(20.0) == "SAFE"
        assert classify_wbgt(26.0) == "LOW"
        assert classify_wbgt(30.0) == "MODERATE"
        assert classify_wbgt(34.0) == "HIGH"
        assert classify_wbgt(38.0) == "EXTREME"


# ─── HTSI Tests ─────────────────────────────────────────────────────────────

class TestHTSI:
    def test_htsi_range(self):
        """HTSI must always be between 0 and 100."""
        for temp in [20, 30, 40, 50]:
            for hum in [10, 50, 90]:
                for wind in [0, 10, 30]:
                    htsi, _ = calculate_htsi(temp, hum, wind, 700, 30)
                    assert 0 <= htsi <= 100, f"HTSI out of range: {htsi}"

    def test_htsi_extreme_conditions(self):
        """Ward 18 demo scenario should produce EXTREME HTSI."""
        wbgt = calculate_wbgt(43.0, 62.0, 860.0, 5.5)
        htsi, components = calculate_htsi(43.0, 62.0, 5.5, 860.0, wbgt, heatwave_duration=7)
        assert htsi >= 75, f"Expected high HTSI, got {htsi}"
        level = classify_htsi(htsi)
        assert level in ["HIGH", "EXTREME"]

    def test_htsi_components_sum(self):
        """Component contributions should roughly sum to HTSI."""
        wbgt = calculate_wbgt(43.0, 62.0, 860.0, 5.5)
        htsi, components = calculate_htsi(43.0, 62.0, 5.5, 860.0, wbgt, 7)
        total = sum(components.values())
        assert abs(total - htsi) < 1.0, f"Components don't sum to HTSI: {total} vs {htsi}"

    def test_htsi_classification_boundaries(self):
        assert classify_htsi(10) == "SAFE"
        assert classify_htsi(30) == "LOW"
        assert classify_htsi(50) == "MODERATE"
        assert classify_htsi(70) == "HIGH"
        assert classify_htsi(90) == "EXTREME"

    def test_htsi_cool_safe_conditions(self):
        """Cool, breezy, low solar should produce SAFE/LOW HTSI."""
        wbgt = calculate_wbgt(25.0, 30.0, 100.0, 20.0)
        htsi, _ = calculate_htsi(25.0, 30.0, 20.0, 100.0, wbgt, 0)
        assert htsi <= 40, f"Expected low HTSI for mild conditions, got {htsi}"


# ─── Full Thermal Calculation ────────────────────────────────────────────────

class TestThermalCalculation:
    def test_full_calculation(self):
        """Full thermal calculation should return all metrics."""
        weather = WeatherInput(
            temperature=43.0, humidity=62.0, wind_speed=5.5,
            solar_radiation=860.0, heatwave_duration=7
        )
        result = calculate_all_thermal_metrics(weather)
        assert result.heat_index > 0
        assert result.wbgt > 0
        assert 0 <= result.htsi <= 100
        assert result.htsi_level in ["SAFE", "LOW", "MODERATE", "HIGH", "EXTREME"]
        assert result.heat_index_level in ["SAFE", "LOW", "MODERATE", "HIGH", "EXTREME"]

    def test_methodology_notes_present(self):
        """Methodology notes must be present for transparency."""
        weather = WeatherInput(temperature=40.0, humidity=50.0, wind_speed=10.0, solar_radiation=700.0)
        result = calculate_all_thermal_metrics(weather)
        assert result.methodology_notes
        assert "NOAA" in result.methodology_notes or "Rothfusz" in result.methodology_notes


# ─── Vulnerability Tests ─────────────────────────────────────────────────────

class TestVulnerability:
    def test_high_elderly_density_increases_vulnerability(self):
        """Wards with more elderly population should have higher vulnerability."""
        low_elderly = VulnerabilityInput(
            ward_id=1, total_population=50000, area_sq_km=5,
            elderly_population=2000, children_population=10000,
            outdoor_worker_population=5000, hospital_count_within_2km=2
        )
        high_elderly = VulnerabilityInput(
            ward_id=2, total_population=50000, area_sq_km=5,
            elderly_population=12000, children_population=10000,
            outdoor_worker_population=5000, hospital_count_within_2km=2
        )
        r1 = calculate_vulnerability(low_elderly)
        r2 = calculate_vulnerability(high_elderly)
        assert r2.vulnerability_score > r1.vulnerability_score

    def test_no_hospitals_increases_vulnerability(self):
        base = dict(ward_id=1, total_population=50000, area_sq_km=5,
                    elderly_population=5000, children_population=10000,
                    outdoor_worker_population=5000)
        with_hospitals = VulnerabilityInput(**base, hospital_count_within_2km=3)
        no_hospitals = VulnerabilityInput(**base, hospital_count_within_2km=0)
        r1 = calculate_vulnerability(with_hospitals)
        r2 = calculate_vulnerability(no_hospitals)
        assert r2.vulnerability_score > r1.vulnerability_score

    def test_vulnerability_range(self):
        """Vulnerability score must be 0–100."""
        inp = VulnerabilityInput(
            ward_id=18, total_population=78000, area_sq_km=4.7,
            elderly_population=9360, children_population=19500,
            outdoor_worker_population=18720, hospital_count_within_2km=0
        )
        result = calculate_vulnerability(inp)
        assert 0 <= result.vulnerability_score <= 100
        assert result.vulnerability_level in ["SAFE", "LOW", "MODERATE", "HIGH", "EXTREME"]


# ─── Risk Engine Tests ───────────────────────────────────────────────────────

class TestRiskEngine:
    def test_extreme_conditions_produce_high_risk(self):
        """Ward 18 extreme scenario should produce HIGH or EXTREME risk."""
        wbgt = calculate_wbgt(43.0, 62.0, 860.0, 5.5)
        htsi, _ = calculate_htsi(43.0, 62.0, 5.5, 860.0, wbgt, 7)
        hi = calculate_heat_index(43.0, 62.0)

        inp = RiskInput(
            ward_id=18, htsi=htsi, heat_index=hi, wbgt=wbgt,
            temperature=43.0, temperature_anomaly=15.0,
            heatwave_duration=7, vulnerability_score=80.0
        )
        result = calculate_health_risk(inp)
        assert result.overall_risk_level in ["HIGH", "EXTREME"]
        assert result.mortality_risk_score >= 60

    def test_safe_conditions_produce_low_risk(self):
        """Cool conditions should produce SAFE or LOW risk."""
        wbgt = calculate_wbgt(28.0, 40.0, 200.0, 15.0)
        htsi, _ = calculate_htsi(28.0, 40.0, 15.0, 200.0, wbgt, 0)
        hi = calculate_heat_index(28.0, 40.0)

        inp = RiskInput(
            ward_id=1, htsi=htsi, heat_index=hi, wbgt=wbgt,
            temperature=28.0, temperature_anomaly=0.0,
            heatwave_duration=0, vulnerability_score=20.0
        )
        result = calculate_health_risk(inp)
        assert result.overall_risk_level in ["SAFE", "LOW", "MODERATE"]

    def test_risk_scores_in_range(self):
        """All risk scores must be 0–100."""
        wbgt = calculate_wbgt(40.0, 55.0, 700.0, 8.0)
        htsi, _ = calculate_htsi(40.0, 55.0, 8.0, 700.0, wbgt, 3)
        hi = calculate_heat_index(40.0, 55.0)
        inp = RiskInput(ward_id=1, htsi=htsi, heat_index=hi, wbgt=wbgt,
                        temperature=40.0, temperature_anomaly=12.0,
                        heatwave_duration=3, vulnerability_score=60.0)
        result = calculate_health_risk(inp)
        assert 0 <= result.mortality_risk_score <= 100
        assert 0 <= result.hospitalization_risk_score <= 100


# ─── Alert Engine Tests ──────────────────────────────────────────────────────

class TestAlertEngine:
    def test_extreme_htsi_triggers_alert(self):
        """HTSI >= 81 must trigger EXTREME alert."""
        alert = evaluate_alert_rules(
            ward_id=18, ward_name="Shastri Nagar",
            htsi=88.0, vulnerability_score=75.0,
            wbgt=35.0, heat_index=56.0,
            mortality_risk_score=82.0, hospitalization_risk_score=78.0
        )
        assert alert is not None
        assert alert["severity"] == "EXTREME"

    def test_high_htsi_with_vulnerability_triggers_alert(self):
        """HTSI >= 61 + vulnerability >= 60 should trigger HIGH alert."""
        alert = evaluate_alert_rules(
            ward_id=17, ward_name="Sanganer",
            htsi=70.0, vulnerability_score=65.0,
            wbgt=31.0, heat_index=48.0,
            mortality_risk_score=65.0, hospitalization_risk_score=60.0
        )
        assert alert is not None
        assert alert["severity"] in ["HIGH", "EXTREME"]

    def test_low_htsi_no_alert(self):
        """Low HTSI should not trigger any alert."""
        alert = evaluate_alert_rules(
            ward_id=1, ward_name="Amer",
            htsi=25.0, vulnerability_score=30.0,
            wbgt=22.0, heat_index=28.0,
            mortality_risk_score=20.0, hospitalization_risk_score=18.0
        )
        assert alert is None

    def test_extreme_alert_has_recommendations(self):
        """Extreme alert must include recommendations."""
        alert = evaluate_alert_rules(
            ward_id=18, ward_name="Shastri Nagar",
            htsi=90.0, vulnerability_score=85.0,
            wbgt=37.0, heat_index=58.0,
            mortality_risk_score=88.0, hospitalization_risk_score=85.0
        )
        assert alert is not None
        assert len(alert["recommendations"]) >= 3
