import React from 'react';
import { 
  Thermometer, 
  Droplets, 
  Sun, 
  Wind, 
  AlertOctagon, 
  Activity, 
  HeartPulse, 
  ShieldAlert,
  TrendingUp,
  Info
} from 'lucide-react';
import { DashboardSummary } from '../../types';

interface HeroMetricsProps {
  summary: DashboardSummary;
}

export const HeroMetrics: React.FC<HeroMetricsProps> = ({ summary }) => {
  const getHtsiBadge = (score: number) => {
    if (score >= 81) return { bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400', label: 'EXTREME HEAT EMERGENCY', color: '#EF4444' };
    if (score >= 66) return { bg: 'bg-orange-500/10 border-orange-500/30 text-orange-400', label: 'HIGH THERMAL STRESS', color: '#F97316' };
    if (score >= 51) return { bg: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400', label: 'MODERATE HEAT DANGER', color: '#EAB308' };
    return { bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400', label: 'SAFE / NORMAL', color: '#10B981' };
  };

  const htsiMeta = getHtsiBadge(summary.htsi);

  return (
    <div className="space-y-4">
      {/* Top Banner: Real-time Heat Status */}
      <div className={`p-4 rounded-2xl glass-panel border ${htsiMeta.bg} flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3`}>
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2 flex-wrap gap-y-1">
              <span className="font-display font-bold text-sm sm:text-base text-white">
                {htsiMeta.label}
              </span>
              <span
                className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase"
                style={{ backgroundColor: htsiMeta.color + '22', color: htsiMeta.color, border: `1px solid ${htsiMeta.color}44` }}
              >
                HTSI {summary.htsi.toFixed(1)}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Peak thermal stress in <strong className="text-white">{summary.highest_risk_ward || 'Jaipur Central'}</strong>. {summary.active_alerts} active ward alerts detected.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4 self-end sm:self-auto">
          <div className="text-right">
            <div className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">Active Alerts</div>
            <div className="text-xl font-display font-extrabold text-rose-400">{summary.active_alerts} Wards</div>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <div className="text-right">
            <div className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">Affected</div>
            <div className="text-xl font-display font-extrabold text-amber-400">
              {summary.extreme_wards + summary.high_wards} / {summary.total_wards}
            </div>
          </div>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Card 1: HTSI (Flagship Index) */}
        <div className="relative overflow-hidden glass-panel glass-panel-hover p-5 rounded-2xl border border-rose-500/30 bg-gradient-to-b from-rose-950/20 to-slate-900/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-rose-400 tracking-wider uppercase flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5" />
              HTSI Composite Index
            </span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">
              0-100
            </span>
          </div>

          <div className="mt-3 flex items-baseline justify-between">
            <div>
              <span className="text-4xl font-display font-black text-white tracking-tight">
                {summary.htsi.toFixed(1)}
              </span>
              <span className="text-sm font-semibold text-rose-400 ml-1.5 font-mono">/ 100</span>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold text-rose-400 uppercase tracking-wide block">
                {summary.htsi_level}
              </span>
              <span className="text-[10px] text-slate-400">Multi-Factor Stress</span>
            </div>
          </div>

          {/* Progress gauge bar */}
          <div className="mt-3 w-full bg-slate-800 rounded-full h-2 overflow-hidden border border-white/5">
            <div 
              className="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-600 transition-all duration-700 rounded-full"
              style={{ width: `${Math.min(100, summary.htsi)}%` }}
            />
          </div>

          <p className="mt-2 text-[11px] text-slate-400 flex items-center gap-1">
            <Info className="w-3 h-3 text-slate-500 flex-shrink-0" />
            Temperature, solar, WBGT & exposure duration.
          </p>
        </div>

        {/* Card 2: Ambient Temp & Heat Index */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl border border-white/10 bg-slate-900/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-amber-400 tracking-wider uppercase flex items-center gap-1.5">
              <Thermometer className="w-3.5 h-3.5" />
              Air Temp & Feels Like
            </span>
            <span className="text-[11px] font-mono text-slate-400">Jaipur AWS</span>
          </div>

          <div className="mt-3 flex items-baseline justify-between">
            <div>
              <span className="text-4xl font-display font-black text-white tracking-tight">
                {summary.temperature.toFixed(1)}°
              </span>
              <span className="text-sm font-semibold text-slate-400 ml-1 font-mono">C</span>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold text-amber-300 font-mono">
                HI {summary.heat_index.toFixed(1)}°C
              </span>
              <span className="text-[10px] text-slate-400 block">NOAA Heat Index</span>
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs pt-2 border-t border-white/5">
            <span className="text-slate-400">Relative Humidity:</span>
            <span className="font-mono font-bold text-slate-200">{summary.humidity}%</span>
          </div>

          <div className="mt-1 flex items-center justify-between text-xs">
            <span className="text-slate-400">Solar Radiation:</span>
            <span className="font-mono font-bold text-slate-200">{summary.solar_radiation} W/m²</span>
          </div>
        </div>

        {/* Card 3: WBGT (Wet Bulb Globe Temp) */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl border border-white/10 bg-slate-900/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-orange-400 tracking-wider uppercase flex items-center gap-1.5">
              <Sun className="w-3.5 h-3.5" />
              WBGT Index
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 font-bold">
              OSHA THRESHOLD
            </span>
          </div>

          <div className="mt-3 flex items-baseline justify-between">
            <div>
              <span className="text-4xl font-display font-black text-white tracking-tight">
                {summary.wbgt.toFixed(1)}°
              </span>
              <span className="text-sm font-semibold text-slate-400 ml-1 font-mono">C</span>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold text-rose-400 font-mono">
                &gt;32.2°C HAZARD
              </span>
              <span className="text-[10px] text-slate-400 block">Outdoor Work Limit</span>
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs pt-2 border-t border-white/5">
            <span className="text-slate-400">Wind Velocity:</span>
            <span className="font-mono font-bold text-slate-200">{summary.wind_speed} m/s</span>
          </div>

          <div className="mt-1 flex items-center justify-between text-xs">
            <span className="text-slate-400">Labor Recommendation:</span>
            <span className="font-bold text-rose-400 text-[11px]">STOP / 45m Rest/hr</span>
          </div>
        </div>

        {/* Card 4: Health Impact & Hospital Load */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl border border-white/10 bg-slate-900/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-rose-400 tracking-wider uppercase flex items-center gap-1.5">
              <HeartPulse className="w-3.5 h-3.5" />
              Healthcare Risk Load
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold">
              AI PREDICTED
            </span>
          </div>

          <div className="mt-3 flex items-baseline justify-between">
            <div>
              <span className="text-4xl font-display font-black text-white tracking-tight">
                {summary.hospitalization_risk_score.toFixed(0)}
              </span>
              <span className="text-sm font-semibold text-rose-400 ml-1 font-mono">/ 100</span>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold text-rose-400 font-mono">HIGH SURGE</span>
              <span className="text-[10px] text-slate-400 block">ER Influx Forecast</span>
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs pt-2 border-t border-white/5">
            <span className="text-slate-400">Mortality Vulnerability:</span>
            <span className="font-mono font-bold text-rose-300">{summary.mortality_risk_score} / 100</span>
          </div>

          <div className="mt-1 flex items-center justify-between text-xs">
            <span className="text-slate-400">High Risk Demographics:</span>
            <span className="font-bold text-amber-300 text-[11px]">Elderly & Slum Clusters</span>
          </div>
        </div>

      </div>
    </div>
  );
};
