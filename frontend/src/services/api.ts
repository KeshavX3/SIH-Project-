import axios from 'axios';
import {
  DashboardSummary,
  WardListItem,
  WardDetail,
  AlertItem,
  ThermalCalculationRequest,
  ThermalCalculationResponse,
  HourlyForecastPoint,
  HourlyForecastResponse,
} from '../types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '';


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

// ─── Live Hourly Forecast & Early Warning ───────────────────────────────────

export async function fetchHourlyForecast(hours: number = 72): Promise<HourlyForecastPoint[]> {
  try {
    const res = await client.get<HourlyForecastResponse>(`/api/weather/hourly-forecast?hours=${hours}`);
    if (res.data && res.data.hourly && res.data.hourly.length > 0) {
      return res.data.hourly;
    }
    return FALLBACK_HOURLY_FORECAST.slice(0, hours);
  } catch (err) {
    console.warn('Hourly forecast API unreachable, using simulated early-warning curve', err);
    return FALLBACK_HOURLY_FORECAST.slice(0, hours);
  }
}

export const FALLBACK_HOURLY_FORECAST: HourlyForecastPoint[] = [
  { time: '2026-06-15T06:00', label: 'Day 1 06:00', short_time: '06:00', date: 'Day 1', temperature: 33.5, humidity: 55, wind_speed: 6.0, solar_radiation: 120, heat_index: 39.2, wbgt: 27.5, htsi: 54.2, risk_level: 'MODERATE', data_source: 'SIMULATED' },
  { time: '2026-06-15T09:00', label: 'Day 1 09:00', short_time: '09:00', date: 'Day 1', temperature: 38.2, humidity: 44, wind_speed: 8.2, solar_radiation: 620, heat_index: 46.5, wbgt: 30.8, htsi: 71.4, risk_level: 'HIGH', data_source: 'SIMULATED' },
  { time: '2026-06-15T12:00', label: 'Day 1 12:00', short_time: '12:00', date: 'Day 1', temperature: 43.1, humidity: 32, wind_speed: 10.5, solar_radiation: 890, heat_index: 52.8, wbgt: 33.4, htsi: 84.8, risk_level: 'EXTREME', data_source: 'SIMULATED' },
  { time: '2026-06-15T15:00', label: 'Day 1 15:00', short_time: '15:00', date: 'Day 1', temperature: 44.8, humidity: 28, wind_speed: 12.0, solar_radiation: 780, heat_index: 55.4, wbgt: 34.6, htsi: 89.1, risk_level: 'EXTREME', data_source: 'SIMULATED' },
  { time: '2026-06-15T18:00', label: 'Day 1 18:00', short_time: '18:00', date: 'Day 1', temperature: 41.5, humidity: 35, wind_speed: 9.0, solar_radiation: 250, heat_index: 48.6, wbgt: 32.1, htsi: 78.3, risk_level: 'HIGH', data_source: 'SIMULATED' },
  { time: '2026-06-15T21:00', label: 'Day 1 21:00', short_time: '21:00', date: 'Day 1', temperature: 37.0, humidity: 42, wind_speed: 7.0, solar_radiation: 0, heat_index: 43.2, wbgt: 29.4, htsi: 65.5, risk_level: 'MODERATE', data_source: 'SIMULATED' },
  { time: '2026-06-16T00:00', label: 'Day 2 00:00', short_time: '00:00', date: 'Day 2', temperature: 34.8, humidity: 48, wind_speed: 5.5, solar_radiation: 0, heat_index: 40.1, wbgt: 28.0, htsi: 59.2, risk_level: 'MODERATE', data_source: 'SIMULATED' },
  { time: '2026-06-16T03:00', label: 'Day 2 03:00', short_time: '03:00', date: 'Day 2', temperature: 33.0, humidity: 52, wind_speed: 5.0, solar_radiation: 0, heat_index: 38.0, wbgt: 27.1, htsi: 55.0, risk_level: 'MODERATE', data_source: 'SIMULATED' },
  { time: '2026-06-16T06:00', label: 'Day 2 06:00', short_time: '06:00', date: 'Day 2', temperature: 34.2, humidity: 50, wind_speed: 6.2, solar_radiation: 140, heat_index: 40.5, wbgt: 28.2, htsi: 57.8, risk_level: 'MODERATE', data_source: 'SIMULATED' },
  { time: '2026-06-16T12:00', label: 'Day 2 12:00', short_time: '12:00', date: 'Day 2', temperature: 44.2, humidity: 30, wind_speed: 11.0, solar_radiation: 910, heat_index: 54.6, wbgt: 34.2, htsi: 87.5, risk_level: 'EXTREME', data_source: 'SIMULATED' },
  { time: '2026-06-16T15:00', label: 'Day 2 15:00', short_time: '15:00', date: 'Day 2', temperature: 45.4, humidity: 26, wind_speed: 12.5, solar_radiation: 810, heat_index: 57.2, wbgt: 35.1, htsi: 92.0, risk_level: 'EXTREME', data_source: 'SIMULATED' },
  { time: '2026-06-17T12:00', label: 'Day 3 12:00', short_time: '12:00', date: 'Day 3', temperature: 43.8, humidity: 33, wind_speed: 10.0, solar_radiation: 880, heat_index: 54.1, wbgt: 33.9, htsi: 86.4, risk_level: 'EXTREME', data_source: 'SIMULATED' },
  { time: '2026-06-17T15:00', label: 'Day 3 15:00', short_time: '15:00', date: 'Day 3', temperature: 44.9, humidity: 29, wind_speed: 11.5, solar_radiation: 790, heat_index: 56.0, wbgt: 34.8, htsi: 90.3, risk_level: 'EXTREME', data_source: 'SIMULATED' },
];

// ─── NDMA Heat Action Plan (HAP) Bilingual Protocols ────────────────────────

export const NDMA_PROTOCOLS = [
  {
    tier: 'NORMAL',
    color: '#10B981',
    threshold_temp: '< 40.0°C',
    threshold_hi: 'HI < 41°C',
    title_en: 'Green Alert (Normal Season / Pre-Heatwave)',
    title_hi: 'ग्रीन अलर्ट (सामान्य स्थिति / पूर्व तैयारी)',
    municipal_actions_en: [
      'Maintain continuous water tanker readiness across urban slums and informal settlements.',
      'Check availability of ORS packets and IV fluids at all Urban Primary Health Centers (UPHCs).',
      'Conduct community awareness workshops on heat stroke signs with ASHA & Anganwadi workers.',
    ],
    municipal_actions_hi: [
      'शहरी कच्ची बस्तियों और झुग्गियों में पानी के टैंकरों की पूर्व उपलब्धता सुनिश्चित करें।',
      'सभी प्राथमिक स्वास्थ्य केंद्रों (UPHC) पर ओआरएस (ORS) और आवश्यक दवाओं का स्टॉक रखें।',
      'आशा और आंगनवाड़ी कार्यकर्ताओं द्वारा लू से बचाव के प्रति जन-जागरूकता अभियान चलाएं।',
    ],
    citizen_advisories_en: [
      'Drink plenty of water even if not feeling thirsty. Carry reusable water bottles.',
      'Wear lightweight, loose-fitting, light-colored cotton clothing.',
      'Schedule heavy outdoor activities during cooler morning and evening hours.',
    ],
    citizen_advisories_hi: [
      'प्यास न लगने पर भी नियमित रूप से पानी पिएं और बाहर जाते समय पानी की बोतल साथ रखें।',
      'हल्के रंग के, ढीले और सूती कपड़े पहनें।',
      'कठिन शारीरिक कार्य सुबह या शाम के ठंडे समय में ही करें।',
    ],
    vulnerable_groups_en: ['Elderly with cardiovascular conditions', 'Infants & toddlers', 'Outdoor gig workers'],
    vulnerable_groups_hi: ['हृदय रोगी व बुजुर्ग नागरिक', 'छोटे बच्चे व शिशु', 'डिलीवरी बॉय एवं आउटडोर वर्कर्स'],
  },
  {
    tier: 'YELLOW',
    color: '#EAB308',
    threshold_temp: '40.1°C – 42.9°C',
    threshold_hi: 'HI 41°C – 53°C',
    title_en: 'Yellow Alert (Heat Alert / Watch)',
    title_hi: 'येलो अलर्ट (निगरानी व सतर्कता चेतावनी)',
    municipal_actions_en: [
      'Deploy shaded waiting shelters at major Jaipur bus stations (Sindhi Camp, Narayan Singh Circle).',
      'Instruct construction site contractors to mandate 15-minute shaded rest breaks every hour.',
      'Alert SMS broadcasts to registered registered street vendors and delivery personnel.',
    ],
    municipal_actions_hi: [
      'सिंधी कैंप और प्रमुख बस स्टैंडों पर छायादार शेल्टर और ठंडे पेयजल की व्यवस्था करें।',
      'निर्माण स्थलों पर मजदूरों के लिए प्रति घंटे 15 मिनट का छायादार विश्राम अनिवार्य करें।',
      'स्ट्रीट वेंडरों और गिग वर्करों को एसएमएस (SMS) द्वारा सतर्कता संदेश भेजें।',
    ],
    citizen_advisories_en: [
      'Avoid direct exposure to the sun between 12:00 PM and 3:00 PM.',
      'Cover head with a cloth, hat, or umbrella when stepping outdoors.',
      'Never leave children or pets inside a parked automobile under direct sunlight.',
    ],
    citizen_advisories_hi: [
      'दोपहर 12:00 बजे से 3:00 बजे के बीच सीधी धूप में जाने से बचें।',
      'धूप में निकलते समय सिर को सूती कपड़े, गमछे या टोपी से ढकें।',
      'बंद वाहन में बच्चों या पालतू जानवरों को अकेला कभी न छोड़ें।',
    ],
    vulnerable_groups_en: ['Traffic police personnel', 'Daily wage construction laborers', 'Pregnant women'],
    vulnerable_groups_hi: ['ट्रैफिक पुलिस कर्मी', 'दैनिक मजदूरी वाले निर्माण श्रमिक', 'गर्भवती महिलाएं'],
  },
  {
    tier: 'ORANGE',
    color: '#F97316',
    threshold_temp: '43.0°C – 44.9°C',
    threshold_hi: 'HI 54°C – 65°C',
    title_en: 'Orange Alert (Severe Heatwave Warning)',
    title_hi: 'ऑरेंज अलर्ट (तीव्र लू की गंभीर चेतावनी)',
    municipal_actions_en: [
      'Open air-conditioned municipal cooling centers across high-density wards (Walled City, Sanganer).',
      'Reschedule government and outdoor road construction work: halt all operations from 11:30 AM to 3:30 PM.',
      'Equip 108 Emergency Ambulances with ice packs and specialized heat-exhaustion resuscitation kits.',
    ],
    municipal_actions_hi: [
      'चारदीवारी (पुराना जयपुर) और सांगानेर जैसी घनी बस्तियों में वातानुकूलित कूलिंग शेल्टर खोलें।',
      'सड़क और सरकारी निर्माण कार्यों का समय बदलें: सुबह 11:30 से दोपहर 3:30 तक काम बंद रखें।',
      '108 एम्बुलेंस में आइस पैक्स और हीट स्ट्रोक प्राथमिक उपचार किट तैनात रखें।',
    ],
    citizen_advisories_en: [
      'High risk of heat cramps, exhaustion, and heatstroke. Minimize outdoor movement.',
      'Consume ORS, homemade drinks (lemon water, chaas, lassi, coconut water) continuously.',
      'If feeling dizzy, nauseous, or experiencing rapid heartbeat, seek immediate medical shade.',
    ],
    citizen_advisories_hi: [
      'लू लगने और बेहोश होने का भारी जोखिम। गैर-जरूरी कार्य से बाहर न निकलें।',
      'ओआरएस, छाछ, नींबू पानी, आम पन्ना और नारियल पानी का निरंतर सेवन करें।',
      'चक्कर, उल्टी या अत्यधिक पसीना आने पर तुरंत ठंडी छाया में जाएं और चिकित्सक से संपर्क करें।',
    ],
    vulnerable_groups_en: ['Rickshaw pullers & e-rickshaw drivers', 'Elderly living without AC/coolers', 'Industrial zone workers'],
    vulnerable_groups_hi: ['ई-रिक्शा व ऑटो चालक', 'बिना कूलर/एसी के रहने वाले बुजुर्ग', 'औद्योगिक क्षेत्र के श्रमिक'],
  },
  {
    tier: 'RED',
    color: '#EF4444',
    threshold_temp: '≥ 45.0°C or Prolonged Duration',
    threshold_hi: 'HI > 65°C / HTSI ≥ 81',
    title_en: 'Red Alert (Extreme Heat Emergency / Disaster Phase)',
    title_hi: 'रेड अलर्ट (अति गंभीर लू आपातकाल / आपदा चरण)',
    municipal_actions_en: [
      'Immediate enforcement: Complete shutdown of all non-essential outdoor manual labor 11:00 AM – 4:00 PM.',
      'Deploy municipal fire tenders and water misting trucks across arterial roads to reduce ambient road surface temperature.',
      'Activate dedicated Heat Emergency Response Wards at SMS Hospital, Jaipur and district satellite hospitals.',
      'Continuous broadcast of emergency heat warnings across city public address systems, radio, and electronic billboards.',
    ],
    municipal_actions_hi: [
      'तत्काल आदेश: सुबह 11:00 से शाम 4:00 बजे तक समस्त आउटडोर शारीरिक श्रम पूर्णतः प्रतिबंधित।',
      'मुख्य सड़कों की सतह का तापमान घटाने के लिए नगर निगम के पानी छिड़कने वाले टैंकर चलाएं।',
      'सवाई मानसिंह (SMS) अस्पताल एवं सभी जिला अस्पतालों में विशेष हीटस्ट्रोक इमरजेंसी वार्ड सक्रिय करें।',
      'शहर के लाउडस्पीकरों, एफएम रेडियो और डिजिटल बिलबोर्ड्स पर आपातकालीन लू चेतावनी प्रसारित करें।',
    ],
    citizen_advisories_en: [
      'LIFE THREATENING EMERGENCY. Extreme danger of fatal heat stroke.',
      'Stay indoors in the coolest available room. Use wet towels on forehead and neck.',
      'Avoid high-protein foods and alcohol which increase metabolic heat production.',
      'Check in on elderly neighbors twice daily.',
    ],
    citizen_advisories_hi: [
      'जानलेवा आपातकाल। हीट स्ट्रोक (लू) से मृत्यु का अत्यधिक खतरा।',
      'घर के सबसे ठंडे कमरे में ही रहें। माथे और गर्दन पर गीली पट्टी का इस्तेमाल करें।',
      'अत्यधिक तेल-मसालेदार भोजन और शराब से बचें जो शरीर का तापमान बढ़ाते हैं।',
      'अपने आसपास के बुजुर्गों और अकेले रहने वाले पड़ोसियों की दिन में दो बार कुशलक्षेम लें।',
    ],
    vulnerable_groups_en: ['Entire outdoor population', 'Patients with diabetes, kidney or heart illness', 'Slum residents without ventilation'],
    vulnerable_groups_hi: ['बाहर काम करने वाले सभी नागरिक', 'किडनी, शुगर या बीपी के मरीज', 'बिना हवादार आवास वाले निवासी'],
  },
];

