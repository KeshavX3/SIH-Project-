import React from 'react';
import { 
  Flame, 
  MapPin, 
  Activity, 
  AlertTriangle, 
  Sliders, 
  BarChart3, 
  ShieldAlert, 
  RefreshCw,
  Cpu
} from 'lucide-react';
import { SystemStatus } from '../../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  activeAlertCount: number;
  systemStatus?: SystemStatus;
  lastUpdated: string;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  activeAlertCount,
  systemStatus,
  lastUpdated,
  onRefresh,
  isRefreshing,
}) => {
  const navItems = [
    { id: 'overview', label: 'Command Center', icon: Activity },
    { id: 'map', label: 'GIS Heat Stress Map', icon: MapPin },
    { id: 'simulator', label: 'Thermal Simulator', icon: Sliders },
    { id: 'wards', label: 'Ward Vulnerability', icon: BarChart3 },
    { id: 'alerts', label: 'Early Warnings & SOPs', icon: AlertTriangle, badge: activeAlertCount },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 bg-[#080C14]/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & City Info */}
          <div className="flex items-center space-x-3">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-amber-500 p-0.5 shadow-glow-red">
              <div className="w-full h-full bg-[#0B0F17] rounded-[10px] flex items-center justify-center">
                <Flame className="w-5 h-5 text-rose-500 animate-pulse" />
              </div>
            </div>

            <div>
              <div className="flex items-center space-x-2">
                <span className="font-display font-extrabold text-lg tracking-tight text-white">
                  HeatGuard <span className="text-rose-500">AI</span>
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-mono font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded">
                  SIH26083
                </span>
              </div>
              <div className="flex items-center space-x-1 text-xs text-slate-400">
                <MapPin className="w-3 h-3 text-amber-400" />
                <span className="font-medium text-slate-300">Jaipur</span>
                <span className="text-slate-500">•</span>
                <span className="text-[11px] text-slate-400">Rajasthan, India</span>
              </div>
            </div>
          </div>

          {/* Nav Tabs */}
          <nav className="hidden md:flex items-center space-x-1 bg-slate-900/60 p-1 rounded-xl border border-white/5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`relative flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-rose-500/20 to-amber-500/20 text-white border border-rose-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-rose-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="ml-1.5 px-1.5 py-0.2 text-[10px] font-bold bg-rose-500 text-white rounded-full animate-pulse-slow">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right Status & Actions */}
          <div className="flex items-center space-x-3">
            {/* System Engine Status */}
            <div className="hidden lg:flex items-center space-x-2 px-2.5 py-1.5 bg-slate-900/80 border border-white/5 rounded-lg text-xs">
              <Cpu className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-slate-400 text-[11px]">ML Engine:</span>
              <span className="font-mono text-[11px] font-semibold text-emerald-400">
                {systemStatus?.ml_engine === 'READY' ? 'ONLINE' : 'ACTIVE'}
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            </div>

            {/* Refresh Button */}
            <button
              onClick={onRefresh}
              title={`Last updated: ${new Date(lastUpdated).toLocaleTimeString()}`}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-white/10 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-slate-400 ${isRefreshing ? 'animate-spin text-rose-400' : ''}`} />
              <span className="hidden sm:inline text-[11px]">Refresh</span>
            </button>
          </div>

        </div>

        {/* Mobile Navigation bar */}
        <div className="flex md:hidden overflow-x-auto py-2 space-x-1 border-t border-white/5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap ${
                  isActive
                    ? 'bg-rose-500/20 text-white border border-rose-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="px-1.5 text-[9px] bg-rose-500 text-white rounded-full">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
