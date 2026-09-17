import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';
import {
  ChevronRight, Clock, AlertCircle, BookOpen, Wifi, WifiOff, ChevronUp, Flame,
} from 'lucide-react';
import { DashboardSummary, WardListItem, HourlyForecastPoint } from '../../types';
import { fetchHourlyForecast, FALLBACK_HOURLY_FORECAST } from '../../services/api';
import { HeatActionPlanModal } from './HeatActionPlanModal';

interface RiskDistributionProps {
  summary: DashboardSummary;
  wards: WardListItem[];
  onSelectWard: (wardId: number) => void;
}

const RISK_COLOR: Record<string, string> = {
  EXTREME: '#ef4444',
  HIGH: '#f97316',
  MODERATE: '#fbbf24',
  SAFE: '#34d399',
  LOW: '#34d399',
};

export const RiskDistribution: React.FC<RiskDistributionProps> = ({ summary, wards, onSelectWard }) => {
  const [hoursRange, setHoursRange] = useState<number>(24);
  const [forecastList, setForecastList] = useState<HourlyForecastPoint[]>(FALLBACK_HOURLY_FORECAST);
  const [isLive, setIsLive] = useState(false);
  const [isHapModalOpen, setIsHapModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function loadForecast() {
      setIsLoading(true);
      try {
        const data = await fetchHourlyForecast(hoursRange);
        if (isMounted && data && data.length > 0) {
          setForecastList(data);
          setIsLive(data[0]?.data_source?.includes('OPEN_METEO') ?? false);
        }
      } catch {
        // fallback stays
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }
    loadForecast();
    return () => { isMounted = false; };
  }, [hoursRange]);

  const chartData = forecastList.map((pt) => ({
    time: hoursRange > 24 ? pt.label : pt.short_time,
    'Temp (°C)': pt.temperature,
    'HTSI': pt.htsi,
    'WBGT (°C)': pt.wbgt,
  }));

  const topWards = [...wards].sort((a, b) => (b.htsi ?? 0) - (a.htsi ?? 0)).slice(0, 6);

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 animate-fade-up">

        {/* ── Left 2-col: Forecast chart ──────────────────── */}
        <div className="lg:col-span-2 card p-5 rounded-2xl space-y-4">

          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg" style={{ background: 'rgba(251,191,36,0.15)' }}>
                  <Clock className="w-4 h-4 text-amber-400" />
                </div>
                <h3 className="text-sm font-bold text-white">Heat Forecast</h3>
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
                  style={{
                    background: isLive ? 'rgba(16,185,129,0.12)' : 'rgba(100,116,139,0.12)',
                    border: `1px solid ${isLive ? 'rgba(16,185,129,0.3)' : 'rgba(100,116,139,0.2)'}`,
                    color: isLive ? '#34d399' : '#94a3b8',
                  }}>
                  {isLive ? <Wifi className="w-2.5 h-2.5" /> : <WifiOff className="w-2.5 h-2.5" />}
                  {isLive ? 'Live' : 'Demo'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">Temperature · HTSI thermal stress · WBGT index</p>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              {/* Time range selector */}
              <div className="flex rounded-xl overflow-hidden" style={{ border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.04)' }}>
                {[24, 48, 72].map((h) => (
                  <button
                    key={h}
                    onClick={() => setHoursRange(h)}
                    className="px-3 py-1.5 text-xs font-semibold transition-all"
                    style={{
                      background: hoursRange === h ? 'linear-gradient(135deg,#f97316,#ef4444)' : 'transparent',
                      color: hoursRange === h ? 'white' : '#94a3b8',
                    }}
                  >
                    {h}h
                  </button>
                ))}
              </div>

              {/* NDMA button */}
              <button
                onClick={() => setIsHapModalOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl transition-all"
                style={{
                  background: 'rgba(239,68,68,0.12)',
                  border: '1px solid rgba(239,68,68,0.25)',
                  color: '#f87171',
                }}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Action Plan</span>
                <span className="sm:hidden">HAP</span>
              </button>
            </div>
          </div>

          {/* Chart */}
          <div className={`h-56 w-full transition-opacity ${isLoading ? 'opacity-40' : 'opacity-100'}`}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15,23,42,0.96)',
                    border: '1px solid rgba(255,255,255,0.12)',
                    borderRadius: '10px',
                    color: '#f8fafc',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Line type="monotone" dataKey="HTSI" stroke="#ef4444" strokeWidth={2.5} dot={hoursRange <= 24 ? { r: 3, fill: '#ef4444' } : false} />
                <Line type="monotone" dataKey="Temp (°C)" stroke="#f97316" strokeWidth={2} dot={hoursRange <= 24 ? { r: 2.5, fill: '#f97316' } : false} />
                <Line type="monotone" dataKey="WBGT (°C)" stroke="#38bdf8" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Risk chips */}
          <div className="grid grid-cols-4 gap-2 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
            {[
              { label: 'Extreme', count: summary.extreme_wards, color: '#ef4444' },
              { label: 'High',    count: summary.high_wards,    color: '#f97316' },
              { label: 'Moderate',count: summary.moderate_wards,color: '#fbbf24' },
              { label: 'Safe',    count: summary.safe_wards,    color: '#34d399' },
            ].map(({ label, count, color }) => (
              <div key={label} className="text-center p-2 rounded-xl" style={{ background: `${color}10` }}>
                <div className="text-lg font-black" style={{ color }}>{count}</div>
                <div className="text-[10px] font-semibold" style={{ color, opacity: 0.75 }}>{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Right 1-col: Ward leaderboard ────────────────── */}
        <div className="card p-5 rounded-2xl flex flex-col gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <div className="p-1.5 rounded-lg" style={{ background: 'rgba(239,68,68,0.15)' }}>
                <Flame className="w-4 h-4 text-rose-400" />
              </div>
              <h3 className="text-sm font-bold text-white">Top Risk Wards</h3>
            </div>
            <p className="text-xs text-slate-500">Sorted by heat stress index</p>
          </div>

          <div className="flex-1 space-y-2">
            {topWards.map((ward, idx) => {
              const color = RISK_COLOR[ward.risk_level] ?? '#94a3b8';
              const htsi = ward.htsi ?? 0;
              return (
                <div
                  key={ward.id}
                  onClick={() => onSelectWard(ward.id)}
                  className="group flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all"
                  style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.06)',
                  }}
                  onMouseEnter={e => {
                    (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.07)';
                    (e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.15)';
                  }}
                  onMouseLeave={e => {
                    (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.03)';
                    (e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.06)';
                  }}
                >
                  {/* Rank */}
                  <span className="text-xs font-black w-5 text-center" style={{ color }}>
                    #{idx + 1}
                  </span>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-white truncate">{ward.ward_name}</div>
                    <div className="mt-1 h-1 rounded-full bg-white/10 overflow-hidden">
                      <div className="h-full rounded-full transition-all" style={{ width: `${Math.min(100, htsi)}%`, background: color }} />
                    </div>
                  </div>

                  {/* HTSI */}
                  <div className="text-right flex-shrink-0">
                    <span className="text-xs font-black" style={{ color }}>{htsi.toFixed(0)}</span>
                    <ChevronRight className="w-3 h-3 text-slate-600 group-hover:text-slate-300 transition-colors ml-1 inline" />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Active protocol notice */}
          <div className="rounded-xl p-3 text-xs space-y-1" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
            <div className="flex items-center gap-1.5 text-rose-400 font-semibold text-[11px] uppercase tracking-wide">
              <AlertCircle className="w-3.5 h-3.5" />
              Active Protocols
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              ORS distribution at 12 transit points. Cool-roof inspections ongoing in Walled City.
            </p>
          </div>
        </div>
      </div>

      {/* NDMA Modal */}
      <HeatActionPlanModal
        isOpen={isHapModalOpen}
        onClose={() => setIsHapModalOpen(false)}
        currentRiskLevel={summary.overall_risk_level}
      />
    </>
  );
};
