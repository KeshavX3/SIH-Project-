import React from 'react';
import { Thermometer, Droplets, Wind, Sun, Activity, HeartPulse, AlertTriangle, TrendingUp } from 'lucide-react';
import { DashboardSummary } from '../../types';

interface HeroMetricsProps {
  summary: DashboardSummary;
}

const riskMeta = (score: number) => {
  if (score >= 81) return { label: 'Extreme Heat', color: '#ef4444', bg: 'card-red', emoji: '🔴' };
  if (score >= 66) return { label: 'High Heat Risk', color: '#f97316', bg: 'card-orange', emoji: '🟠' };
  if (score >= 51) return { label: 'Moderate Risk', color: '#fbbf24', bg: 'card-amber', emoji: '🟡' };
  return { label: 'Normal / Safe', color: '#34d399', bg: 'card-emerald', emoji: '🟢' };
};

export const HeroMetrics: React.FC<HeroMetricsProps> = ({ summary }) => {
  const meta = riskMeta(summary.htsi);

  return (
    <div className="space-y-5 animate-fade-up">

      {/* ── Hero status banner ──────────────────────────────── */}
      <div className={`${meta.bg} rounded-2xl p-5 sm:p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4`}>
        <div className="flex items-center gap-4">
          <div className="text-5xl leading-none select-none">{meta.emoji}</div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: meta.color, opacity: 0.85 }}>
              Current Status · Jaipur
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white leading-none" style={{ fontFamily: 'Space Grotesk, Inter, sans-serif' }}>
              {meta.label}
            </h2>
            <p className="text-sm text-white/60 mt-1.5">
              Highest risk in <span className="text-white font-semibold">{summary.highest_risk_ward || 'Jaipur Central'}</span>
              &nbsp;· {summary.active_alerts} active alert{summary.active_alerts !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {/* Big HTSI display */}
        <div className="flex-shrink-0 text-right">
          <div className="text-[10px] uppercase tracking-widest font-bold mb-1" style={{ color: meta.color, opacity: 0.75 }}>Heat Stress Index</div>
          <div className="text-5xl font-black text-white leading-none" style={{ fontFamily: 'Space Grotesk, Inter, sans-serif' }}>
            {summary.htsi.toFixed(0)}
            <span className="text-lg text-white/40 font-semibold ml-1">/100</span>
          </div>
          {/* Progress bar */}
          <div className="mt-2 w-32 h-2 rounded-full bg-white/10 overflow-hidden ml-auto">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${Math.min(100, summary.htsi)}%`,
                background: `linear-gradient(90deg, #34d399, #fbbf24, #f97316, #ef4444)`,
              }}
            />
          </div>
        </div>
      </div>

      {/* ── 4-stat weather cards ──────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">

        {/* Temperature */}
        <div className="card card-hover p-5 rounded-2xl flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl" style={{ background: 'rgba(249,115,22,0.15)' }}>
              <Thermometer className="w-4 h-4 text-orange-400" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Temp</span>
          </div>
          <div>
            <div className="text-3xl font-black text-white" style={{ fontFamily: 'Space Grotesk, Inter, sans-serif' }}>
              {summary.temperature.toFixed(1)}°<span className="text-lg text-slate-400">C</span>
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Feels like <span className="text-orange-300 font-semibold">{summary.heat_index.toFixed(1)}°C</span>
            </div>
          </div>
        </div>

        {/* Humidity */}
        <div className="card card-hover p-5 rounded-2xl flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl" style={{ background: 'rgba(56,189,248,0.15)' }}>
              <Droplets className="w-4 h-4 text-sky-400" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Humidity</span>
          </div>
          <div>
            <div className="text-3xl font-black text-white" style={{ fontFamily: 'Space Grotesk, Inter, sans-serif' }}>
              {summary.humidity}<span className="text-lg text-slate-400">%</span>
            </div>
            <div className="text-xs text-slate-400 mt-1">
              WBGT <span className="text-sky-300 font-semibold">{summary.wbgt.toFixed(1)}°C</span>
            </div>
          </div>
        </div>

        {/* Wind */}
        <div className="card card-hover p-5 rounded-2xl flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl" style={{ background: 'rgba(168,85,247,0.15)' }}>
              <Wind className="w-4 h-4 text-purple-400" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Wind</span>
          </div>
          <div>
            <div className="text-3xl font-black text-white" style={{ fontFamily: 'Space Grotesk, Inter, sans-serif' }}>
              {summary.wind_speed}<span className="text-lg text-slate-400"> m/s</span>
            </div>
            <div className="text-xs text-slate-400 mt-1">Surface wind speed</div>
          </div>
        </div>

        {/* Solar */}
        <div className="card card-hover p-5 rounded-2xl flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl" style={{ background: 'rgba(251,191,36,0.15)' }}>
              <Sun className="w-4 h-4 text-amber-400" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Solar</span>
          </div>
          <div>
            <div className="text-3xl font-black text-white" style={{ fontFamily: 'Space Grotesk, Inter, sans-serif' }}>
              {summary.solar_radiation}<span className="text-base text-slate-400"> W/m²</span>
            </div>
            <div className="text-xs text-slate-400 mt-1">Global solar radiation</div>
          </div>
        </div>

      </div>

      {/* ── Ward risk summary ──────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Extreme', count: summary.extreme_wards, color: '#ef4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.25)' },
          { label: 'High',     count: summary.high_wards,    color: '#f97316', bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.25)' },
          { label: 'Moderate', count: summary.moderate_wards, color: '#fbbf24', bg: 'rgba(251,191,36,0.12)', border: 'rgba(251,191,36,0.25)' },
          { label: 'Safe',     count: summary.safe_wards,    color: '#34d399', bg: 'rgba(52,211,153,0.12)', border: 'rgba(52,211,153,0.25)' },
        ].map(({ label, count, color, bg, border }) => (
          <div key={label} className="rounded-2xl p-4 text-center" style={{ background: bg, border: `1px solid ${border}` }}>
            <div className="text-2xl font-black" style={{ color, fontFamily: 'Space Grotesk, Inter, sans-serif' }}>{count}</div>
            <div className="text-xs font-semibold mt-1" style={{ color }}>
              {label}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">wards</div>
          </div>
        ))}
      </div>

      {/* ── Health risk row ──────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="card p-5 rounded-2xl flex items-center gap-4">
          <div className="p-3 rounded-2xl flex-shrink-0" style={{ background: 'rgba(239,68,68,0.12)' }}>
            <HeartPulse className="w-6 h-6 text-rose-400" />
          </div>
          <div className="flex-1">
            <div className="text-xs text-slate-400 font-medium mb-1">Hospital Load Risk</div>
            <div className="flex items-end gap-2">
              <span className="text-2xl font-black text-white">{summary.hospitalization_risk_score.toFixed(0)}</span>
              <span className="text-sm text-slate-500 mb-0.5">/ 100</span>
            </div>
            <div className="mt-2 h-1.5 rounded-full bg-white/10 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-rose-500 to-red-600" style={{ width: `${summary.hospitalization_risk_score}%` }} />
            </div>
          </div>
        </div>

        <div className="card p-5 rounded-2xl flex items-center gap-4">
          <div className="p-3 rounded-2xl flex-shrink-0" style={{ background: 'rgba(168,85,247,0.12)' }}>
            <Activity className="w-6 h-6 text-purple-400" />
          </div>
          <div className="flex-1">
            <div className="text-xs text-slate-400 font-medium mb-1">Mortality Risk Score</div>
            <div className="flex items-end gap-2">
              <span className="text-2xl font-black text-white">{summary.mortality_risk_score}</span>
              <span className="text-sm text-slate-500 mb-0.5">/ 100</span>
            </div>
            <div className="mt-2 h-1.5 rounded-full bg-white/10 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-purple-500 to-violet-600" style={{ width: `${summary.mortality_risk_score}%` }} />
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};
