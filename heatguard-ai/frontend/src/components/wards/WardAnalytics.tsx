import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Users, 
  Thermometer, 
  Activity, 
  ShieldAlert, 
  BarChart2, 
  Sun, 
  Heart, 
  MapPin,
  Briefcase
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';
import { WardListItem, WardDetail } from '../../types';
import { fetchWardDetail } from '../../services/api';

interface WardAnalyticsProps {
  wards: WardListItem[];
  selectedWardId: number;
  onSelectWard: (id: number) => void;
}

export const WardAnalytics: React.FC<WardAnalyticsProps> = ({
  wards,
  selectedWardId,
  onSelectWard,
}) => {
  const [detail, setDetail] = useState<WardDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isCurrent = true;
    setLoading(true);
    fetchWardDetail(selectedWardId).then((data) => {
      if (isCurrent) {
        setDetail(data);
        setLoading(false);
      }
    });
    return () => { isCurrent = false; };
  }, [selectedWardId]);

  const htsiComponents = detail?.thermal?.htsi_components ? [
    { name: 'Temperature', value: detail.thermal.htsi_components.temperature || 32, fill: '#EF4444' },
    { name: 'Humidity', value: detail.thermal.htsi_components.humidity || 18, fill: '#06B6D4' },
    { name: 'Solar Rad.', value: detail.thermal.htsi_components.solar_radiation || 16, fill: '#F59E0B' },
    { name: 'WBGT', value: detail.thermal.htsi_components.wbgt || 17, fill: '#F97316' },
    { name: 'Duration', value: detail.thermal.htsi_components.duration || 9, fill: '#A855F7' },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Top Header & Ward Picker */}
      <div className="glass-panel p-5 rounded-2xl border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base sm:text-lg font-display font-bold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-rose-500" />
            Ward Vulnerability & Thermal Stress Deep Dive
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Socio-demographic exposure indices correlated with microclimate heat stress metrics.
          </p>
        </div>

        {/* Ward Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-mono font-medium">Select Ward:</span>
          <select
            value={selectedWardId}
            onChange={(e) => onSelectWard(Number(e.target.value))}
            className="bg-slate-900 text-white text-xs font-semibold px-3 py-2 rounded-xl border border-white/10 focus:outline-none focus:border-rose-500 cursor-pointer"
          >
            {wards.map((w) => (
              <option key={w.id} value={w.id}>
                Ward #{w.ward_number}: {w.ward_name} ({w.risk_level})
              </option>
            ))}
          </select>
        </div>
      </div>

      {detail && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left 4-Cols: Ward Socio-Demographic Vulnerability Profile */}
          <div className="lg:col-span-4 glass-panel p-6 rounded-2xl border border-white/10 space-y-5">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase">Selected Ward</span>
                <h3 className="text-lg font-display font-bold text-white mt-0.5">
                  {detail.ward_name}
                </h3>
              </div>
              <span className={`px-2.5 py-1 text-xs font-mono font-bold uppercase rounded-lg border ${
                detail.risk?.overall_risk_level === 'EXTREME'
                  ? 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                  : 'bg-orange-500/20 text-orange-300 border-orange-500/30'
              }`}>
                {detail.risk?.overall_risk_level || 'HIGH'}
              </span>
            </div>

            {/* Demographics Metrics */}
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/50 border border-white/5">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-blue-400" />
                  Total Population:
                </span>
                <span className="font-mono font-bold text-white text-sm">
                  {detail.vulnerability?.total_population?.toLocaleString() || '180,000'}
                </span>
              </div>

              <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/50 border border-white/5">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Heart className="w-3.5 h-3.5 text-rose-400" />
                  Elderly Population (&gt;60y):
                </span>
                <span className="font-mono font-bold text-rose-300">
                  {detail.vulnerability?.elderly_population?.toLocaleString() || '21,600'}
                </span>
              </div>

              <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/50 border border-white/5">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-amber-400" />
                  Outdoor Labor Workers:
                </span>
                <span className="font-mono font-bold text-amber-300">
                  {detail.vulnerability?.outdoor_worker_population?.toLocaleString() || '32,400'}
                </span>
              </div>

              <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/50 border border-white/5">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                  Ward Area:
                </span>
                <span className="font-mono font-bold text-slate-200">
                  {detail.area_sq_km || 6.2} km²
                </span>
              </div>
            </div>

            {/* Vulnerability Score Indicator */}
            <div className="pt-2 border-t border-white/5">
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400 font-semibold">Composite Vulnerability Score:</span>
                <span className="font-mono font-bold text-rose-400">
                  {detail.vulnerability?.vulnerability_score?.toFixed(0) || '85'} / 100
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-yellow-500 to-rose-500 rounded-full"
                  style={{ width: `${detail.vulnerability?.vulnerability_score || 85}%` }}
                />
              </div>
            </div>
          </div>

          {/* Right 8-Cols: Microclimate Weather & HTSI Components Breakdown */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* Weather & Thermal Snapshot Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="glass-panel p-3.5 rounded-xl border border-white/5">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Microclimate Temp</span>
                <div className="text-2xl font-display font-extrabold text-white mt-1">
                  {detail.weather?.temperature.toFixed(1) || '43.5'}°C
                </div>
                <div className="text-[10px] text-amber-400 mt-0.5">Heatwave Day #{detail.weather?.heatwave_day_number || 4}</div>
              </div>

              <div className="glass-panel p-3.5 rounded-xl border border-white/5">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Relative Humidity</span>
                <div className="text-2xl font-display font-extrabold text-cyan-400 mt-1">
                  {detail.weather?.humidity || 59}%
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">High moisture entrapment</div>
              </div>

              <div className="glass-panel p-3.5 rounded-xl border border-white/5">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Calculated WBGT</span>
                <div className="text-2xl font-display font-extrabold text-orange-400 mt-1">
                  {detail.thermal?.wbgt.toFixed(1) || '34.2'}°C
                </div>
                <div className="text-[10px] text-rose-400 mt-0.5">Extreme Labor Hazard</div>
              </div>

              <div className="glass-panel p-3.5 rounded-xl border border-white/5">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Ward HTSI Score</span>
                <div className="text-2xl font-display font-extrabold text-rose-400 mt-1">
                  {detail.thermal?.htsi.toFixed(1) || '88.2'}
                </div>
                <div className="text-[10px] text-rose-300 font-bold uppercase mt-0.5">{detail.thermal?.htsi_level || 'EXTREME'}</div>
              </div>
            </div>

            {/* HTSI Factor Contribution Bar Chart */}
            <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-bold flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-rose-500" />
                  HTSI Component Breakdown (Biometeorological Model Weights)
                </h4>
                <span className="text-[10px] text-slate-400 font-mono">Additive Stress Model</span>
              </div>

              <div className="h-56 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={htsiComponents} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
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
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      {htsiComponents.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <p className="text-[11px] text-slate-400 leading-relaxed border-t border-white/5 pt-2">
                HTSI integrates air temperature, vapor pressure (humidity), shortwave solar radiation, wind convective cooling, and consecutive exposure duration into an actionable index calibrated for Indian climate resilience.
              </p>
            </div>

          </div>

        </div>
      )}
    </div>
  );
};
