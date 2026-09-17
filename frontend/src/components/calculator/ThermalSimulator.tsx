import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  Thermometer, 
  Droplets, 
  Wind, 
  Sun, 
  Calendar, 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldAlert,
  Zap
} from 'lucide-react';
import { calculateThermalStress } from '../../services/api';
import { ThermalCalculationResponse } from '../../types';

export const ThermalSimulator: React.FC = () => {
  const [temperature, setTemperature] = useState<number>(44.0);
  const [humidity, setHumidity] = useState<number>(60);
  const [windSpeed, setWindSpeed] = useState<number>(4.5);
  const [solarRadiation, setSolarRadiation] = useState<number>(880);
  const [heatwaveDuration, setHeatwaveDuration] = useState<number>(4);

  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ThermalCalculationResponse | null>(null);

  // Compute thermal metrics when sliders change (with brief debounce)
  useEffect(() => {
    let isCurrent = true;
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await calculateThermalStress({
          temperature,
          humidity,
          wind_speed: windSpeed,
          solar_radiation: solarRadiation,
          heatwave_duration: heatwaveDuration,
        });
        if (isCurrent) setResult(data);
      } catch (err) {
        console.error(err);
      } finally {
        if (isCurrent) setLoading(false);
      }
    }, 150);

    return () => {
      isCurrent = false;
      clearTimeout(timer);
    };
  }, [temperature, humidity, windSpeed, solarRadiation, heatwaveDuration]);

  const getHtsiTheme = (score: number) => {
    if (score >= 81) return { color: '#EF4444', text: 'text-rose-400', border: 'border-rose-500/30', bg: 'bg-rose-500/10', label: 'EXTREME HEAT EMERGENCY' };
    if (score >= 66) return { color: '#F97316', text: 'text-orange-400', border: 'border-orange-500/30', bg: 'bg-orange-500/10', label: 'HIGH THERMAL STRESS' };
    if (score >= 51) return { color: '#EAB308', text: 'text-yellow-400', border: 'border-yellow-500/30', bg: 'bg-yellow-500/10', label: 'MODERATE HEAT STRESS' };
    return { color: '#10B981', text: 'text-emerald-400', border: 'border-emerald-500/30', bg: 'bg-emerald-500/10', label: 'SAFE / COMFORT' };
  };

  const currentTheme = result ? getHtsiTheme(result.htsi) : getHtsiTheme(80);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-5 rounded-2xl border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="p-2 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <Sliders className="w-5 h-5" />
            </span>
            <h2 className="text-base sm:text-lg font-display font-bold text-white">
              What-If Biometeorological Thermal Stress Simulator
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Simulate custom weather extremes to compute the <strong>Human Thermal Stress Index (HTSI)</strong>, Wet Bulb Globe Temperature (WBGT), and OSHA outdoor labor thresholds.
          </p>
        </div>

        {/* Preset quick scenarios */}
        <div className="flex flex-wrap gap-2 text-xs">
          <button
            onClick={() => { setTemperature(47.5); setHumidity(45); setWindSpeed(3.0); setSolarRadiation(980); setHeatwaveDuration(5); }}
            className="px-2.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 font-medium transition-colors"
          >
            🔥 Extreme May Heatwave (47.5°C)
          </button>
          <button
            onClick={() => { setTemperature(41.0); setHumidity(75); setWindSpeed(2.0); setSolarRadiation(750); setHeatwaveDuration(3); }}
            className="px-2.5 py-1.5 rounded-lg bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 border border-orange-500/30 font-medium transition-colors"
          >
            💧 Humid Monsoon Heat (41°C / 75% RH)
          </button>
          <button
            onClick={() => { setTemperature(34.0); setHumidity(40); setWindSpeed(5.5); setSolarRadiation(600); setHeatwaveDuration(1); }}
            className="px-2.5 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 font-medium transition-colors"
          >
            🍃 Mild Spring Weather (34°C)
          </button>
        </div>
      </div>

      {/* Main Grid: Controls Left, Live Thermal Result Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left 6-cols: Interactive Sliders */}
        <div className="lg:col-span-6 glass-panel p-6 rounded-2xl border border-white/10 space-y-5">
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold border-b border-white/5 pb-2">
            Meteorological Input Parameters
          </h3>

          {/* Slider 1: Air Temperature */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="flex items-center gap-1.5 font-semibold text-slate-200">
                <Thermometer className="w-4 h-4 text-rose-500" />
                Air Temperature (°C)
              </span>
              <span className="font-mono font-bold text-rose-400 text-sm">{temperature.toFixed(1)}°C</span>
            </div>
            <input
              type="range"
              min="28"
              max="52"
              step="0.5"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-rose-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>28°C (Normal)</span>
              <span>42°C (Heatwave)</span>
              <span>52°C (Extreme)</span>
            </div>
          </div>

          {/* Slider 2: Relative Humidity */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="flex items-center gap-1.5 font-semibold text-slate-200">
                <Droplets className="w-4 h-4 text-cyan-400" />
                Relative Humidity (%)
              </span>
              <span className="font-mono font-bold text-cyan-400 text-sm">{humidity}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="95"
              step="1"
              value={humidity}
              onChange={(e) => setHumidity(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>10% (Dry Desert)</span>
              <span>50% (Moderate)</span>
              <span>95% (Oppressive)</span>
            </div>
          </div>

          {/* Slider 3: Wind Speed */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="flex items-center gap-1.5 font-semibold text-slate-200">
                <Wind className="w-4 h-4 text-blue-400" />
                Surface Wind Speed (m/s)
              </span>
              <span className="font-mono font-bold text-blue-400 text-sm">{windSpeed.toFixed(1)} m/s</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="15.0"
              step="0.5"
              value={windSpeed}
              onChange={(e) => setWindSpeed(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-400"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0.5 m/s (Stagnant)</span>
              <span>5.0 m/s (Breeze)</span>
              <span>15.0 m/s (Strong)</span>
            </div>
          </div>

          {/* Slider 4: Solar Radiation */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="flex items-center gap-1.5 font-semibold text-slate-200">
                <Sun className="w-4 h-4 text-amber-400" />
                Solar Global Horizontal Irradiance (W/m²)
              </span>
              <span className="font-mono font-bold text-amber-400 text-sm">{solarRadiation} W/m²</span>
            </div>
            <input
              type="range"
              min="100"
              max="1200"
              step="20"
              value={solarRadiation}
              onChange={(e) => setSolarRadiation(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>100 (Overcast)</span>
              <span>600 (Afternoon)</span>
              <span>1200 (Peak Direct Sun)</span>
            </div>
          </div>

          {/* Slider 5: Heatwave Duration */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="flex items-center gap-1.5 font-semibold text-slate-200">
                <Calendar className="w-4 h-4 text-purple-400" />
                Heatwave Exposure Duration (Consecutive Days)
              </span>
              <span className="font-mono font-bold text-purple-400 text-sm">{heatwaveDuration} Days</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={heatwaveDuration}
              onChange={(e) => setHeatwaveDuration(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-400"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>Day 1 (Onset)</span>
              <span>Day 5 (Cumulative Stress)</span>
              <span>Day 10 (Critical Exhaustion)</span>
            </div>
          </div>

        </div>

        {/* Right 6-cols: Live Gauge, Indices & Recommendations */}
        <div className="lg:col-span-6 space-y-4">
          
          {/* Main Dial Card */}
          <div className={`glass-panel p-6 rounded-2xl border ${currentTheme.border} ${currentTheme.bg} transition-all duration-300`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Calculated Human Thermal Stress Index
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold uppercase" style={{ backgroundColor: `${currentTheme.color}25`, color: currentTheme.color }}>
                {result?.htsi_level || 'EXTREME'}
              </span>
            </div>

            <div className="mt-4 flex items-center justify-between">
              <div>
                <div className="text-5xl font-display font-black text-white tracking-tight">
                  {result?.htsi.toFixed(1) || '86.4'}
                </div>
                <div className="text-xs font-semibold mt-1" style={{ color: currentTheme.color }}>
                  {currentTheme.label}
                </div>
              </div>

              {/* Quick Sub-Indices */}
              <div className="text-right space-y-1.5 border-l border-white/10 pl-6">
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-mono">WBGT Index</div>
                  <div className="text-lg font-mono font-bold text-cyan-400">
                    {result?.wbgt.toFixed(1) || '34.6'}°C
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-mono">NOAA Heat Index</div>
                  <div className="text-lg font-mono font-bold text-amber-400">
                    {result?.heat_index.toFixed(1) || '56.4'}°C
                  </div>
                </div>
              </div>
            </div>

            {/* HTSI Breakdown Contributions */}
            {result?.htsi_components && (
              <div className="mt-5 pt-4 border-t border-white/10">
                <div className="text-xs font-semibold text-slate-300 mb-2">
                  Factor Contributions to Total Stress
                </div>
                <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 text-center text-[11px]">
                  <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
                    <div className="text-slate-400 text-[10px]">Temp</div>
                    <div className="font-mono font-bold text-rose-400">+{result.htsi_components.temperature}</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
                    <div className="text-slate-400 text-[10px]">Humidity</div>
                    <div className="font-mono font-bold text-cyan-400">+{result.htsi_components.humidity}</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
                    <div className="text-slate-400 text-[10px]">Solar</div>
                    <div className="font-mono font-bold text-amber-400">+{result.htsi_components.solar_radiation}</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
                    <div className="text-slate-400 text-[10px]">Duration</div>
                    <div className="font-mono font-bold text-purple-400">+{result.htsi_components.duration}</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
                    <div className="text-slate-400 text-[10px]">WBGT</div>
                    <div className="font-mono font-bold text-orange-400">+{result.htsi_components.wbgt}</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
                    <div className="text-slate-400 text-[10px]">Wind Cooling</div>
                    <div className="font-mono font-bold text-emerald-400">-{result.htsi_components.wind}</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Actionable Health Advisories Card */}
          <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Automated Heat Resilience Recommendations
            </h4>

            <div className="space-y-2 text-xs">
              <div className="flex items-start space-x-2 p-2.5 rounded-xl bg-slate-900/50 border border-white/5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <strong className="text-white">Outdoor Labor Regulation: </strong>
                  <span className="text-slate-300">
                    {result && result.wbgt >= 32.2 
                      ? 'OSHA Red Flag: Enforce mandatory 45-minute rest breaks per hour or cease heavy outdoor labor.' 
                      : 'Maintain 15-minute rest breaks in shaded areas every hour with scheduled hydration.'}
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-2 p-2.5 rounded-xl bg-slate-900/50 border border-white/5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <strong className="text-white">Hydration & Electrolytes: </strong>
                  <span className="text-slate-300">
                    Minimum 750ml ORS / water consumption per hour of exposure. Deploy municipal tankers.
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-2 p-2.5 rounded-xl bg-slate-900/50 border border-white/5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <strong className="text-white">Healthcare Facilities: </strong>
                  <span className="text-slate-300">
                    {heatwaveDuration >= 4 
                      ? 'Cumulative thermal strain alert: High geriatric stroke risk. Hospital heat stroke beds on standby.' 
                      : 'Primary health centres stocked with ice packs, intravenous saline, and ORS sachets.'}
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};
