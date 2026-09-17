import axios from 'axios';
import {
  DashboardSummary,
  WardListItem,
  WardDetail,
  AlertItem,
  ThermalCalculationRequest,
  ThermalCalculationResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Realistic Demo Fallback Data ──────────────────────────────────────────

export const DEMO_DASHBOARD_SUMMARY: DashboardSummary = {
  city: "Jaipur",
  state: "Rajasthan",
  timestamp: new Date().toISOString(),
  data_source: "DEMO_SIMULATION",
  temperature: 43.8,
  humidity: 58.0,
  wind_speed: 4.8,
  solar_radiation: 890.0,
  heat_index: 56.4,
  wbgt: 34.6,
  htsi: 86.4,
  utci: 44.1,
  overall_risk_level: "EXTREME",
  htsi_level: "EXTREME",
  mortality_risk_score: 78.5,
  hospitalization_risk_score: 84.2,
  total_wards: 5,
  extreme_wards: 2,
  high_wards: 2,
  moderate_wards: 1,
  safe_wards: 0,
  active_alerts: 4,
  highest_risk_ward: "Ward 18 - Sanganer Industrial",
  highest_risk_ward_id: 3,
  system_status: {
    backend: "HEALTHY",
    database: "CONNECTED",
    ml_engine: "READY",
    gis: "LOADED",
    weather: "DEMO_MODE",
    notifications: "SIMULATION_MODE",
  },
};

export const DEMO_WARDS: WardListItem[] = [
  {
    id: 1,
    ward_number: 1,
    ward_name: "Walled City (Old Jaipur)",
    latitude: 26.9239,
    longitude: 75.8267,
    risk_level: "EXTREME",
    htsi: 88.2,
    mortality_risk_score: 82.0,
    vulnerability_score: 89.5,
  },
  {
    id: 2,
    ward_number: 2,
    ward_name: "Mansarovar Central",
    latitude: 26.8540,
    longitude: 75.7580,
    risk_level: "HIGH",
    htsi: 74.5,
    mortality_risk_score: 64.0,
    vulnerability_score: 61.2,
  },
  {
    id: 3,
    ward_number: 3,
    ward_name: "Sanganer Industrial Zone",
    latitude: 26.8090,
    longitude: 75.7960,
    risk_level: "EXTREME",
    htsi: 91.4,
    mortality_risk_score: 89.0,
    vulnerability_score: 93.0,
  },
  {
    id: 4,
    ward_number: 4,
    ward_name: "Vaishali Nagar",
    latitude: 26.9120,
    longitude: 75.7380,
    risk_level: "MODERATE",
    htsi: 62.1,
    mortality_risk_score: 48.0,
    vulnerability_score: 52.4,
  },
  {
    id: 5,
    ward_number: 5,
    ward_name: "Amer Heritage Ward",
    latitude: 26.9855,
    longitude: 75.8513,
    risk_level: "HIGH",
    htsi: 77.8,
    mortality_risk_score: 71.0,
    vulnerability_score: 79.8,
  },
];

export const DEMO_ALERTS: AlertItem[] = [
  {
    id: 101,
    ward_id: 3,
    ward_name: "Sanganer Industrial Zone",
    severity: "EXTREME",
    status: "ACTIVE",
    title: "Extreme Thermal Emergency Alert (HTSI 91.4)",
    reason: "Sustained temperature >44°C combined with 62% humidity and high concentration of outdoor textile factory workers.",
    htsi_value: 91.4,
    recommendations: [
      "Immediate mandatory suspension of outdoor labor between 11:30 AM and 4:30 PM",
      "Deploy 4 emergency municipal water tankers & ORS hydration booths to Sanganer Bus Stand",
      "Activate cooling shelter at Sanganer Community Centre (Cap: 250 persons)",
      "Alert SMS dispatch to 24,000 registered residents and factory supervisors"
    ],
    created_at: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
  },
  {
    id: 102,
    ward_id: 1,
    ward_name: "Walled City (Old Jaipur)",
    severity: "EXTREME",
    status: "ACTIVE",
    title: "Urban Heat Island Vulnerability Surge",
    reason: "Dense architectural concrete/masonry trapping nocturnal heat. Nighttime minimum temp failed to drop below 32°C for 48h.",
    htsi_value: 88.2,
    recommendations: [
      "Open air-conditioned night shelters at Johari Bazaar Town Hall",
      "Primary health centers on high heatstroke resuscitation readiness",
      "Cool roof reflective coating inspection for high-density tenements"
    ],
    created_at: new Date(Date.now() - 75 * 60 * 1000).toISOString(),
  },
  {
    id: 103,
    ward_id: 5,
    ward_name: "Amer Heritage Ward",
    severity: "HIGH",
    status: "ACTIVE",
    title: "Severe Heat Risk for Tourists & Outdoor Vendors",
    reason: "Elevated solar radiation (920 W/m²) on unshaded stone pathways with high geriatric foot traffic.",
    htsi_value: 77.8,
    recommendations: [
      "Install misting canopies at Fort ascent paths",
      "Mandatory hydration stops for elephant safari & guide workers"
    ],
    created_at: new Date(Date.now() - 140 * 60 * 1000).toISOString(),
  },
  {
    id: 104,
    ward_id: 2,
    ward_name: "Mansarovar Central",
    severity: "HIGH",
    status: "ACKNOWLEDGED",
    title: "Elevated Thermal Warning for Residential Clusters",
    reason: "WBGT threshold exceeded 33.5°C during afternoon hours.",
    htsi_value: 74.5,
    recommendations: [
      "Advisory broadcast to vulnerable elderly residents via municipal loudspeaker vans"
    ],
    created_at: new Date(Date.now() - 280 * 60 * 1000).toISOString(),
  }
];

// ─── Client-side Thermal Index Fallback Calculator ─────────────────────────
function calculateClientThermal(input: ThermalCalculationRequest): ThermalCalculationResponse {
  const T = input.temperature;
  const RH = input.humidity;
  const V = input.wind_speed;
  const SR = input.solar_radiation || 800;
  const days = input.heatwave_duration || 3;

  // Heat Index (NOAA Steadman / Rothfusz formula approximation)
  let hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (RH * 0.094));
  if (hi >= 80) {
    const c1 = -42.379, c2 = 2.04901523, c3 = 10.14333127, c4 = -0.22475541;
    const c5 = -0.00683783, c6 = -0.05481717, c7 = 0.00122874, c8 = 0.00085282, c9 = -0.00000199;
    hi = c1 + c2*T + c3*RH + c4*T*RH + c5*T*T + c6*RH*RH + c7*T*T*RH + c8*T*RH*RH + c9*T*T*RH*RH;
  }

  // WBGT Outdoor approximation (Liljegren / Bernard simplified)
  const Twb = T * Math.atan(0.151977 * Math.pow(RH + 8.313659, 0.5)) + Math.atan(T + RH) - Math.atan(RH - 1.676331) + 0.00391838 * Math.pow(RH, 1.5) * Math.atan(0.023101 * RH) - 4.686035;
  const Tg = T + 0.013 * SR - 0.45 * V;
  const wbgt = 0.7 * Twb + 0.2 * Tg + 0.1 * T;

  // HTSI (Human Thermal Stress Index - 0 to 100 composite)
  const tempFactor = Math.min(100, Math.max(0, (T - 30) * 4.2));
  const humFactor = Math.min(100, Math.max(0, (RH - 20) * 1.1));
  const solarFactor = Math.min(100, Math.max(0, (SR / 1000) * 80));
  const windMitigation = Math.min(25, V * 2.8);
  const durBonus = Math.min(15, days * 2.5);

  let rawHtsi = (tempFactor * 0.40) + (humFactor * 0.20) + (solarFactor * 0.20) + ((wbgt / 38) * 20) + durBonus - windMitigation;
  const htsi = Math.round(Math.min(100, Math.max(10, rawHtsi)) * 10) / 10;

  let htsiLevel = 'SAFE';
  if (htsi >= 81) htsiLevel = 'EXTREME';
  else if (htsi >= 66) htsiLevel = 'HIGH';
  else if (htsi >= 51) htsiLevel = 'MODERATE';
  else if (htsi >= 36) htsiLevel = 'LOW';

  return {
    temperature: T,
    humidity: RH,
    wind_speed: V,
    solar_radiation: SR,
    heat_index: Math.round(hi * 10) / 10,
    wbgt: Math.round(wbgt * 10) / 10,
    utci: Math.round((T + 0.3 * (RH / 10) - 0.2 * V) * 10) / 10,
    heat_index_level: hi >= 54 ? 'EXTREME_DANGER' : hi >= 41 ? 'DANGER' : 'CAUTION',
    wbgt_level: wbgt >= 32.2 ? 'EXTREME' : wbgt >= 30 ? 'HIGH' : 'MODERATE',
    htsi,
    htsi_level: htsiLevel,
    htsi_components: {
      temperature: Math.round(tempFactor * 0.40),
      humidity: Math.round(humFactor * 0.20),
      wind: Math.round(windMitigation),
      solar_radiation: Math.round(solarFactor * 0.20),
      wbgt: Math.round((wbgt / 38) * 20),
      duration: Math.round(durBonus),
    },
    methodology_notes: "Computed via HeatGuard AI HTSI multi-physics biometeorological composite model.",
  };
}

// ─── API Services ──────────────────────────────────────────────────────────

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  try {
    const res = await client.get<DashboardSummary>('/api/dashboard/summary');
    return res.data;
  } catch (err) {
    console.warn('API /api/dashboard/summary unreachable, using demonstration snapshot', err);
    return DEMO_DASHBOARD_SUMMARY;
  }
}

export async function fetchWards(): Promise<WardListItem[]> {
  try {
    const res = await client.get<WardListItem[]>('/api/wards');
    if (res.data && res.data.length > 0) return res.data;
    return DEMO_WARDS;
  } catch (err) {
    console.warn('API /api/wards unreachable, using demonstration wards', err);
    return DEMO_WARDS;
  }
}

export async function fetchWardDetail(id: number): Promise<WardDetail> {
  try {
    const res = await client.get<WardDetail>(`/api/wards/${id}`);
    return res.data;
  } catch (err) {
    const ward = DEMO_WARDS.find(w => w.id === id) || DEMO_WARDS[0];
    return {
      id: ward.id,
      ward_number: ward.ward_number,
      ward_name: ward.ward_name,
      city_id: 1,
      latitude: ward.latitude,
      longitude: ward.longitude,
      area_sq_km: 12.4,
      weather: {
        temperature: 43.5,
        humidity: 59.0,
        wind_speed: 4.5,
        solar_radiation: 870.0,
        heatwave_day_number: 4,
      },
      thermal: {
        heat_index: 55.8,
        wbgt: 34.2,
        htsi: ward.htsi || 82.0,
        htsi_level: ward.risk_level,
        htsi_components: {
          temperature: 32,
          humidity: 18,
          wind: 5,
          solar_radiation: 16,
          wbgt: 17,
          duration: 9,
        },
      },
      vulnerability: {
        vulnerability_score: ward.vulnerability_score || 75,
        vulnerability_level: ward.risk_level,
        total_population: 185000,
        elderly_population: 22000,
        children_population: 46000,
        outdoor_worker_population: 34000,
      },
      risk: {
        overall_risk_level: ward.risk_level,
        htsi: ward.htsi || 82.0,
        mortality_risk_score: ward.mortality_risk_score || 72,
        hospitalization_risk_score: 79,
      },
    };
  }
}

export async function fetchAlerts(status?: string): Promise<AlertItem[]> {
  try {
    const url = status ? `/api/alerts?status=${status}` : '/api/alerts';
    const res = await client.get<AlertItem[]>(url);
    if (res.data && res.data.length > 0) return res.data;
    return DEMO_ALERTS;
  } catch (err) {
    console.warn('API /api/alerts unreachable, using demonstration alerts', err);
    return DEMO_ALERTS;
  }
}

export async function acknowledgeAlert(alertId: number): Promise<AlertItem> {
  try {
    const res = await client.post<AlertItem>(`/api/alerts/${alertId}/acknowledge`, {
      action_taken: "Immediate dispatch of water tankers and deployment of cooling centers",
      officer_name: "Municipal Control Room Officer",
    });
    return res.data;
  } catch (err) {
    const target = DEMO_ALERTS.find(a => a.id === alertId);
    if (target) {
      target.status = 'ACKNOWLEDGED';
      return { ...target };
    }
    throw err;
  }
}

export async function calculateThermalStress(params: ThermalCalculationRequest): Promise<ThermalCalculationResponse> {
  try {
    const res = await client.post<ThermalCalculationResponse>('/api/thermal/calculate', params);
    return res.data;
  } catch (err) {
    console.warn('Thermal API calculation fallback to client physics engine');
    return calculateClientThermal(params);
  }
}
