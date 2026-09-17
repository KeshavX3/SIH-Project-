import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  CartesianGrid,
  Legend
} from 'recharts';
import { 
  ShieldAlert, 
  Users, 
  Building2, 
  ChevronRight, 
  Clock, 
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { DashboardSummary, WardListItem } from '../../types';

interface RiskDistributionProps {
  summary: DashboardSummary;
  wards: WardListItem[];
  onSelectWard: (wardId: number) => void;
}

// 72-hour simulated forecast trend for Jaipur
const FORECAST_TREND = [
  { time: '06:00', temp: 34.2, htsi: 58.0, wbgt: 28.5 },
  { time: '09:00', temp: 38.5, htsi: 72.1, wbgt: 31.2 },
  { time: '12:00', temp: 43.1, htsi: 85.4, wbgt: 33.8 },
  { time: '15:00', temp: 44.6, htsi: 89.2, wbgt: 34.9 },
  { time: '18:00', temp: 41.8, htsi: 79.5, wbgt: 32.4 },
  { time: '21:00', temp: 37.0, htsi: 67.2, wbgt: 29.8 },
  { time: '00:00', temp: 34.8, htsi: 61.0, wbgt: 28.0 },
  { time: '03:00', temp: 33.2, htsi: 56.4, wbgt: 27.2 },
];

export const RiskDistribution: React.FC<RiskDistributionProps> = ({
  summary,
  wards,
  onSelectWard,
}) => {
  const riskCategories = [
    { label: 'EXTREME', count: summary.extreme_wards, color: '#EF4444', desc: 'HTSI ≥ 81' },
    { label: 'HIGH', count: summary.high_wards, color: '#F97316', desc: 'HTSI 66-80' },
    { label: 'MODERATE', count: summary.moderate_wards, color: '#EAB308', desc: 'HTSI 51-65' },
    { label: 'SAFE/LOW', count: summary.safe_wards, color: '#10B981', desc: 'HTSI < 50' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* 2-Col Left: 72-Hour Diurnal Heatwave Forecast & Stress Trend */}
      <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-white/10 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-display font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              Diurnal Heat Stress Forecast & HTSI Curve (Next 24 Hours)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              High-resolution hourly simulation of air temperature and human thermal stress peak times.
            </p>
          </div>
          <span className="hidden sm:inline px-2.5 py-1 text-[11px] font-mono rounded bg-slate-800 text-slate-300 border border-white/5">
            Peak Window: 13:00 - 16:30
          </span>
        </div>

        <div className="h-64 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={FORECAST_TREND} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(15, 23, 42, 0.95)', 
                  borderColor: 'rgba(255,255,255,0.15)',
                  borderRadius: '8px',
                  color: '#f8fafc',
                  fontSize: '12px'
                }} 
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
              <Line 
                type="monotone" 
                dataKey="htsi" 
                name="HTSI (Thermal Stress 0-100)" 
                stroke="#EF4444" 
                strokeWidth={3} 
                dot={{ r: 4, fill: '#EF4444' }} 
              />
              <Line 
                type="monotone" 
                dataKey="temp" 
                name="Air Temp (°C)" 
                stroke="#F59E0B" 
                strokeWidth={2} 
                dot={{ r: 3, fill: '#F59E0B' }} 
              />
              <Line 
                type="monotone" 
                dataKey="wbgt" 
                name="WBGT (°C)" 
                stroke="#06B6D4" 
                strokeWidth={2} 
                strokeDasharray="4 4"
                dot={{ r: 3, fill: '#06B6D4' }} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Distribution Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-white/5">
          {riskCategories.map((cat) => (
            <div key={cat.label} className="p-2.5 rounded-xl bg-slate-900/50 border border-white/5 text-center">
              <div className="text-[10px] font-mono text-slate-400">{cat.desc}</div>
              <div className="text-xl font-display font-extrabold" style={{ color: cat.color }}>
                {cat.count} Wards
              </div>
              <div className="text-[10px] font-bold tracking-wider" style={{ color: cat.color }}>
                {cat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 1-Col Right: Priority Wards Leaderboard */}
      <div className="glass-panel p-5 rounded-2xl border border-white/10 flex flex-col justify-between space-y-4">
        <div>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-display font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-500" />
              High-Risk Wards Ranking
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Sorted by HTSI</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Wards requiring immediate emergency municipal intervention.
          </p>

          <div className="mt-4 space-y-2">
            {wards.slice(0, 5).map((ward) => {
              const isExtreme = ward.risk_level === 'EXTREME';
              return (
                <div
                  key={ward.id}
                  onClick={() => onSelectWard(ward.id)}
                  className="group flex items-center justify-between p-3 rounded-xl bg-slate-900/40 hover:bg-slate-800/80 border border-white/5 hover:border-white/15 cursor-pointer transition-all"
                >
                  <div className="flex items-center space-x-3">
                    <span className={`w-2 h-8 rounded-full ${isExtreme ? 'bg-rose-500 shadow-glow-red' : 'bg-orange-500'}`} />
                    <div>
                      <h4 className="text-xs font-semibold text-white group-hover:text-amber-400 transition-colors">
                        {ward.ward_name}
                      </h4>
                      <div className="flex items-center space-x-2 text-[11px] text-slate-400 mt-0.5">
                        <span>Ward #{ward.ward_number}</span>
                        <span>•</span>
                        <span className="text-slate-300 font-mono">Vuln: {ward.vulnerability_score?.toFixed(0) || 'N/A'}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <div className="text-right">
                      <div className={`text-xs font-mono font-bold ${isExtreme ? 'text-rose-400' : 'text-orange-400'}`}>
                        {ward.htsi?.toFixed(1) || '80.0'}
                      </div>
                      <div className="text-[9px] font-bold uppercase text-slate-400 tracking-wider">
                        HTSI
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-white transition-colors" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Emergency SOP Quick Reference */}
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs space-y-1.5">
          <div className="flex items-center space-x-1.5 text-rose-400 font-bold text-[11px] uppercase tracking-wider">
            <AlertCircle className="w-3.5 h-3.5" />
            Active Municipal Protocol
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            ORS distribution kiosks active at 12 transit junctions. Cool roof inspections ongoing in Old Jaipur Walled City.
          </p>
        </div>
      </div>

    </div>
  );
};
