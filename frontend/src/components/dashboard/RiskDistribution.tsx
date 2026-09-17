import React, { useState, useEffect } from 'react';
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
  AlertCircle,
  BookOpen,
  Radio,
  Zap
} from 'lucide-react';
import { DashboardSummary, WardListItem, HourlyForecastPoint } from '../../types';
import { fetchHourlyForecast, FALLBACK_HOURLY_FORECAST } from '../../services/api';
import { HeatActionPlanModal } from './HeatActionPlanModal';

interface RiskDistributionProps {
  summary: DashboardSummary;
  wards: WardListItem[];
  onSelectWard: (wardId: number) => void;
}

export const RiskDistribution: React.FC<RiskDistributionProps> = ({
  summary,
  wards,
  onSelectWard,
}) => {
  const [hoursRange, setHoursRange] = useState<number>(24);
  const [forecastList, setForecastList] = useState<HourlyForecastPoint[]>(FALLBACK_HOURLY_FORECAST);
  const [dataSource, setDataSource] = useState<string>('Live Weather');
  const [isHapModalOpen, setIsHapModalOpen] = useState<boolean>(false);
  const [isLoadingForecast, setIsLoadingForecast] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    async function loadForecast() {
      setIsLoadingForecast(true);
      try {
        const data = await fetchHourlyForecast(hoursRange);
        if (isMounted && data && data.length > 0) {
          setForecastList(data);
          if (data[0]?.data_source?.includes('OPEN_METEO')) {
            setDataSource('Live Weather');
          } else {
            setDataSource('Simulated Data');
          }
        }
      } catch (err) {
        console.warn('Failed to load forecast', err);
      } finally {
        if (isMounted) setIsLoadingForecast(false);
      }
    }
    loadForecast();
    return () => { isMounted = false; };
  }, [hoursRange]);

  // Transform data points for clean Recharts display
  const chartData = forecastList.map((pt) => ({
    time: hoursRange > 24 ? pt.label : pt.short_time,
    temp: pt.temperature,
    htsi: pt.htsi,
    wbgt: pt.wbgt,
    heat_index: pt.heat_index,
    risk: pt.risk_level,
  }));

  const riskCategories = [
    { label: 'EXTREME', count: summary.extreme_wards, color: '#EF4444', desc: 'HTSI ≥ 81' },
    { label: 'HIGH', count: summary.high_wards, color: '#F97316', desc: 'HTSI 66-80' },
    { label: 'MODERATE', count: summary.moderate_wards, color: '#EAB308', desc: 'HTSI 51-65' },
    { label: 'SAFE/LOW', count: summary.safe_wards, color: '#10B981', desc: 'HTSI < 50' },
  ];

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* 2-Col Left: 72-Hour Diurnal Heatwave Forecast & Stress Trend */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-white/10 space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-display font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Clock className="w-4 h-4 text-amber-400" />
                  Predictive Heat Stress Early Warning Forecast
                </h3>
                <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                  <Radio className="w-2.5 h-2.5 animate-pulse" />
                  {dataSource}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Hourly biometeorological forecast calculating thermal stress (HTSI), apparent temperature & WBGT.
              </p>
            </div>

            {/* Range Toggle & NDMA Protocol Button */}
            <div className="flex items-center space-x-2">
              <div className="bg-slate-900/90 p-1 rounded-xl border border-white/10 flex text-[11px] font-semibold">
                <button
                  onClick={() => setHoursRange(24)}
                  className={`px-2.5 py-1 rounded-lg transition-all ${
                    hoursRange === 24 ? 'bg-amber-500 text-black shadow-sm font-bold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  24h
                </button>
                <button
                  onClick={() => setHoursRange(48)}
                  className={`px-2.5 py-1 rounded-lg transition-all ${
                    hoursRange === 48 ? 'bg-amber-500 text-black shadow-sm font-bold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  48h
                </button>
                <button
                  onClick={() => setHoursRange(72)}
                  className={`px-2.5 py-1 rounded-lg transition-all ${
                    hoursRange === 72 ? 'bg-amber-500 text-black shadow-sm font-bold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  72h Warning
                </button>
              </div>

              <button
                onClick={() => setIsHapModalOpen(true)}
                className="px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center gap-1.5 transition-all"
                title="Open NDMA Heat Action Plan Guidelines"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">NDMA Action Plan</span>
                <span className="sm:hidden">HAP</span>
              </button>
            </div>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="time" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 10 }} />
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
                  dot={hoursRange <= 24 ? { r: 3, fill: '#EF4444' } : false} 
                />
                <Line 
                  type="monotone" 
                  dataKey="temp" 
                  name="Air Temp (°C)" 
                  stroke="#F59E0B" 
                  strokeWidth={2} 
                  dot={hoursRange <= 24 ? { r: 2.5, fill: '#F59E0B' } : false} 
                />
                <Line 
                  type="monotone" 
                  dataKey="wbgt" 
                  name="WBGT (°C)" 
                  stroke="#06B6D4" 
                  strokeWidth={2} 
                  strokeDasharray="4 4"
                  dot={hoursRange <= 24 ? { r: 2.5, fill: '#06B6D4' } : false} 
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

        {/* Active Protocols */}
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs space-y-1.5">
          <div className="flex items-center space-x-1.5 text-rose-400 font-bold text-[11px] uppercase tracking-wider">
            <AlertCircle className="w-3.5 h-3.5" />
            Active Protocols
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            ORS distribution at 12 transit points. Cool roof inspections ongoing in Old Jaipur Walled City.
          </p>
        </div>
      </div>

    </div>

    {/* Bilingual NDMA Heat Action Plan Modal */}
    <HeatActionPlanModal
      isOpen={isHapModalOpen}
      onClose={() => setIsHapModalOpen(false)}
      currentRiskLevel={summary.overall_risk_level}
    />
  </>
  );
};

