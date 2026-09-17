import React, { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Marker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { 
  MapPin, 
  Flame, 
  Building2, 
  ShieldCheck, 
  Info, 
  Layers, 
  HeartPulse,
  Droplet
} from 'lucide-react';
import { WardListItem } from '../../types';

interface JaipurHeatMapProps {
  wards: WardListItem[];
  onSelectWard: (wardId: number) => void;
}

// Demo Jaipur Cooling Shelters & Hospitals
const COOLING_CENTERS = [
  { id: 1, name: 'Sanganer Municipal Community Hall (Cool Shelter)', lat: 26.8120, lng: 75.8010, cap: '250 persons', type: 'COOLING_CENTER' },
  { id: 2, name: 'Johari Bazaar Air-Conditioned Night Transit Shelter', lat: 26.9210, lng: 75.8290, cap: '180 persons', type: 'COOLING_CENTER' },
  { id: 3, name: 'Mansarovar Metro Hydration & Rest Station', lat: 26.8590, lng: 75.7620, cap: '100 persons', type: 'COOLING_CENTER' },
];

const HOSPITALS = [
  { id: 1, name: 'SMS Hospital & Medical College (Heatstroke Ward)', lat: 26.8988, lng: 75.8155, beds: '30 Heatstroke ICU Beds', type: 'HOSPITAL' },
  { id: 2, name: 'Jaiawati Govt Hospital, Sanganer', lat: 26.8150, lng: 75.7920, beds: '12 Emergency Beds', type: 'HOSPITAL' },
  { id: 3, name: 'Amer District Satellite Hospital', lat: 26.9810, lng: 75.8490, beds: '8 Emergency Beds', type: 'HOSPITAL' },
];

export const JaipurHeatMap: React.FC<JaipurHeatMapProps> = ({
  wards,
  onSelectWard,
}) => {
  const [filter, setFilter] = useState<'ALL' | 'EXTREME' | 'HIGH'>('ALL');
  const [showCoolingCenters, setShowCoolingCenters] = useState<boolean>(true);
  const [showHospitals, setShowHospitals] = useState<boolean>(true);

  const getWardColor = (level: string) => {
    switch (level) {
      case 'EXTREME': return '#EF4444';
      case 'HIGH': return '#F97316';
      case 'MODERATE': return '#EAB308';
      default: return '#10B981';
    }
  };

  const filteredWards = wards.filter((w) => {
    if (filter === 'EXTREME') return w.risk_level === 'EXTREME';
    if (filter === 'HIGH') return w.risk_level === 'EXTREME' || w.risk_level === 'HIGH';
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Map Controls Header */}
      <div className="glass-panel p-4 rounded-2xl border border-white/10 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-display font-bold text-white flex items-center gap-2">
            <Flame className="w-5 h-5 text-rose-500" />
            Jaipur Ward-Level Human Thermal Stress Index (GIS Heat Map)
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time geospatial distribution of thermal stress and emergency resilience infrastructure.
          </p>
        </div>

        {/* Filter and Layer Toggles */}
        <div className="flex flex-wrap items-center gap-3">
          
          {/* Severity filter buttons */}
          <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-white/10 text-xs">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                filter === 'ALL' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All Wards
            </button>
            <button
              onClick={() => setFilter('EXTREME')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                filter === 'EXTREME' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Extreme Only
            </button>
            <button
              onClick={() => setFilter('HIGH')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                filter === 'HIGH' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              High & Extreme
            </button>
          </div>

          {/* Layer toggles */}
          <div className="flex items-center space-x-2 text-xs">
            <label className="flex items-center space-x-1.5 cursor-pointer bg-slate-900/60 px-2.5 py-1.5 rounded-lg border border-white/5 hover:border-white/10">
              <input
                type="checkbox"
                checked={showCoolingCenters}
                onChange={(e) => setShowCoolingCenters(e.target.checked)}
                className="rounded text-cyan-500 bg-slate-800 border-slate-700 focus:ring-0"
              />
              <span className="text-cyan-400 font-medium">Cool Shelters</span>
            </label>

            <label className="flex items-center space-x-1.5 cursor-pointer bg-slate-900/60 px-2.5 py-1.5 rounded-lg border border-white/5 hover:border-white/10">
              <input
                type="checkbox"
                checked={showHospitals}
                onChange={(e) => setShowHospitals(e.target.checked)}
                className="rounded text-rose-500 bg-slate-800 border-slate-700 focus:ring-0"
              />
              <span className="text-rose-400 font-medium">Hospitals</span>
            </label>
          </div>

        </div>
      </div>

      {/* Map Container View */}
      <div className="relative glass-panel rounded-2xl border border-white/10 overflow-hidden shadow-2xl h-[560px] w-full">
        <MapContainer
          center={[26.9124, 75.7873]}
          zoom={12}
          scrollWheelZoom={true}
          className="w-full h-full"
        >
          {/* CartoDB Dark Matter Tile Layer */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* Wards as Interactive Heat Stress Circles */}
          {filteredWards.map((ward) => {
            const color = getWardColor(ward.risk_level);
            return (
              <CircleMarker
                key={ward.id}
                center={[ward.latitude, ward.longitude]}
                radius={28}
                pathOptions={{
                  fillColor: color,
                  fillOpacity: 0.45,
                  color: color,
                  weight: 2,
                  opacity: 0.9,
                }}
              >
                <Popup>
                  <div className="p-1 min-w-[200px] text-slate-100">
                    <div className="flex items-center justify-between pb-1 border-b border-white/10">
                      <span className="font-bold text-xs text-white">
                        {ward.ward_name}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded uppercase font-bold" style={{ backgroundColor: `${color}30`, color: color }}>
                        {ward.risk_level}
                      </span>
                    </div>

                    <div className="mt-2 space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-400">HTSI Score:</span>
                        <span className="font-mono font-bold" style={{ color: color }}>
                          {ward.htsi?.toFixed(1) || '85.0'} / 100
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Mortality Risk:</span>
                        <span className="font-mono font-bold text-slate-200">
                          {ward.mortality_risk_score || '75'}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Vulnerability:</span>
                        <span className="font-mono font-bold text-slate-200">
                          {ward.vulnerability_score?.toFixed(0) || '80'}%
                        </span>
                      </div>
                    </div>

                    <button
                      onClick={() => onSelectWard(ward.id)}
                      className="mt-3 w-full py-1.5 text-center text-[11px] font-bold rounded-lg bg-rose-500 hover:bg-rose-600 text-white transition-colors"
                    >
                      Inspect Ward Analytics →
                    </button>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}

          {/* Cooling Shelter Markers */}
          {showCoolingCenters && COOLING_CENTERS.map((center) => (
            <CircleMarker
              key={`cooling-${center.id}`}
              center={[center.lat, center.lng]}
              radius={8}
              pathOptions={{
                fillColor: '#06B6D4',
                fillOpacity: 0.9,
                color: '#FFFFFF',
                weight: 1.5,
              }}
            >
              <Popup>
                <div className="p-1 text-xs text-slate-100">
                  <div className="font-bold text-cyan-400 flex items-center gap-1">
                    <Droplet className="w-3.5 h-3.5" />
                    Cooling Shelter
                  </div>
                  <div className="font-medium text-white mt-1">{center.name}</div>
                  <div className="text-slate-400 text-[11px] mt-0.5">Capacity: {center.cap}</div>
                </div>
              </Popup>
            </CircleMarker>
          ))}

          {/* Hospital Heatstroke Beds Markers */}
          {showHospitals && HOSPITALS.map((hosp) => (
            <CircleMarker
              key={`hosp-${hosp.id}`}
              center={[hosp.lat, hosp.lng]}
              radius={8}
              pathOptions={{
                fillColor: '#EC4899',
                fillOpacity: 0.9,
                color: '#FFFFFF',
                weight: 1.5,
              }}
            >
              <Popup>
                <div className="p-1 text-xs text-slate-100">
                  <div className="font-bold text-pink-400 flex items-center gap-1">
                    <HeartPulse className="w-3.5 h-3.5" />
                    Designated Heatstroke Hospital
                  </div>
                  <div className="font-medium text-white mt-1">{hosp.name}</div>
                  <div className="text-slate-400 text-[11px] mt-0.5">Status: {hosp.beds}</div>
                </div>
              </Popup>
            </CircleMarker>
          ))}

        </MapContainer>

        {/* Map Legend Overlay */}
        <div className="absolute bottom-5 left-5 z-[1000] glass-panel p-3 rounded-xl border border-white/10 space-y-2 text-xs shadow-lg pointer-events-auto">
          <div className="font-bold text-[11px] text-white uppercase tracking-wider">
            HTSI Heat Stress Index
          </div>
          <div className="space-y-1 text-[11px]">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-rose-500 shadow-glow-red" />
              <span className="text-slate-300">Extreme Hazard (&gt; 80)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-orange-500" />
              <span className="text-slate-300">High Stress (66 - 80)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-yellow-500" />
              <span className="text-slate-300">Moderate Danger (51 - 65)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-slate-300">Low / Safe (&le; 50)</span>
            </div>
          </div>
          <div className="pt-2 border-t border-white/10 flex items-center gap-3 text-[10px] text-slate-400">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-cyan-400 inline-block"/> Cooling Center</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-pink-400 inline-block"/> Hospital ICU</span>
          </div>
        </div>
      </div>
    </div>
  );
};
