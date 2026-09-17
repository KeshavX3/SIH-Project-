export type RiskLevel = 'EXTREME' | 'HIGH' | 'MODERATE' | 'LOW' | 'SAFE';

export interface SystemStatus {
  backend: string;
  database: string;
  ml_engine: string;
  gis: string;
  weather: string;
  notifications: string;
}

export interface DashboardSummary {
  city: string;
  state: string;
  timestamp: string;
  data_source: string;
  temperature: number;
  humidity: number;
  wind_speed: number;
  solar_radiation: number;
  heat_index: number;
  wbgt: number;
  htsi: number;
  utci?: number | null;
  overall_risk_level: RiskLevel;
  htsi_level: string;
  mortality_risk_score: number;
  hospitalization_risk_score: number;
  total_wards: number;
  extreme_wards: number;
  high_wards: number;
  moderate_wards: number;
  safe_wards: number;
  active_alerts: number;
  highest_risk_ward?: string | null;
  highest_risk_ward_id?: number | null;
  system_status: SystemStatus;
}

export interface WardListItem {
  id: number;
  ward_number: number;
  ward_name: string;
  latitude: number;
  longitude: number;
  risk_level: RiskLevel;
  htsi?: number | null;
  mortality_risk_score?: number | null;
  vulnerability_score?: number | null;
}

export interface AlertItem {
  id: number;
  ward_id: number;
  ward_name: string;
  severity: RiskLevel;
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED' | 'EXPIRED';
  title: string;
  reason: string;
  htsi_value?: number | null;
  recommendations: string[];
  created_at: string;
  updated_at?: string;
}

export interface ThermalCalculationRequest {
  temperature: number;
  humidity: number;
  wind_speed: number;
  solar_radiation?: number;
  pressure?: number;
  cloud_cover?: number;
  heatwave_duration?: number;
}

export interface ThermalCalculationResponse {
  temperature: number;
  humidity: number;
  wind_speed: number;
  solar_radiation?: number;
  heat_index: number;
  wbgt: number;
  utci?: number | null;
  heat_index_level: string;
  wbgt_level: string;
  htsi: number;
  htsi_level: string;
  htsi_components: {
    temperature: number;
    humidity: number;
    wind: number;
    solar_radiation: number;
    wbgt: number;
    duration: number;
  };
  methodology_notes?: string;
}

export interface WardDetail {
  id: number;
  ward_number: number;
  ward_name: string;
  city_id: number;
  latitude: number;
  longitude: number;
  area_sq_km: number;
  weather?: {
    temperature: number;
    humidity: number;
    wind_speed: number;
    solar_radiation: number;
    heatwave_day_number: number;
  };
  thermal?: {
    heat_index: number;
    wbgt: number;
    htsi: number;
    htsi_level: string;
    htsi_components: Record<string, number>;
  };
  vulnerability?: {
    vulnerability_score: number;
    vulnerability_level: string;
    total_population: number;
    elderly_population: number;
    children_population: number;
    outdoor_worker_population: number;
  };
  risk?: {
    overall_risk_level: RiskLevel;
    htsi: number;
    mortality_risk_score: number;
    hospitalization_risk_score: number;
  };
}

export interface HourlyForecastPoint {
  time: string;
  label: string;
  short_time: string;
  date: string;
  temperature: number;
  humidity: number;
  wind_speed: number;
  solar_radiation: number;
  heat_index: number;
  wbgt: number;
  utci?: number | null;
  htsi: number;
  risk_level: RiskLevel | string;
  data_source: string;
}

export interface HourlyForecastResponse {
  city: string;
  total_hours: number;
  data_source: string;
  peak_risk_window?: string;
  max_temperature: number;
  max_htsi: number;
  hourly: HourlyForecastPoint[];
}

export interface HeatActionPlanProtocol {
  tier: 'NORMAL' | 'YELLOW' | 'ORANGE' | 'RED';
  color: string;
  threshold_hi: string;
  threshold_temp: string;
  title_en: string;
  title_hi: string;
  municipal_actions_en: string[];
  municipal_actions_hi: string[];
  citizen_advisories_en: string[];
  citizen_advisories_hi: string[];
  vulnerable_groups_en: string[];
  vulnerable_groups_hi: string[];
}

