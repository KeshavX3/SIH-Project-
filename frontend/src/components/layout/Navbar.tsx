import React, { useState } from 'react';
import { Flame, MapPin, LayoutDashboard, Map, Zap, BarChart2, Bell, RefreshCw, Wifi, Menu, X } from 'lucide-react';
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
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { id: 'overview',   label: 'Overview',    icon: LayoutDashboard },
    { id: 'map',        label: 'Heat Map',     icon: Map },
    { id: 'simulator',  label: 'Simulator',    icon: Zap },
    { id: 'wards',      label: 'Wards',        icon: BarChart2 },
    { id: 'alerts',     label: 'Alerts',       icon: Bell, badge: activeAlertCount },
  ];

  const handleNav = (id: string) => {
    setActiveTab(id);
    setMobileOpen(false);
  };

  return (
    <header className="sticky top-0 z-50" style={{
      background: 'rgba(10,15,30,0.85)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255,255,255,0.07)',
    }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-[62px]">

          {/* Logo */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div style={{
              background: 'linear-gradient(135deg, #f97316, #ef4444)',
              borderRadius: '12px',
              padding: '7px',
              boxShadow: '0 4px 14px rgba(239,68,68,0.4)',
            }}>
              <Flame className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-white text-[15px] leading-none" style={{ fontFamily: 'Space Grotesk, Inter, sans-serif' }}>
                HeatGuard <span className="text-gradient-fire">AI</span>
              </div>
              <div className="flex items-center gap-1 mt-0.5">
                <MapPin className="w-2.5 h-2.5 text-amber-400" />
                <span className="text-[10px] text-slate-400">Jaipur, Rajasthan</span>
              </div>
            </div>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNav(item.id)}
                  className={`nav-pill relative ${isActive ? 'active' : ''}`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                  {item.badge !== undefined && item.badge > 0 && (
                    <span style={{
                      background: 'linear-gradient(135deg, #f97316, #ef4444)',
                      borderRadius: '99px',
                      fontSize: '10px',
                      fontWeight: 700,
                      padding: '1px 6px',
                      color: 'white',
                      lineHeight: 1.4,
                    }}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right actions */}
          <div className="flex items-center gap-2">
            {/* Live badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full" style={{
              background: 'rgba(16,185,129,0.12)',
              border: '1px solid rgba(16,185,129,0.25)',
            }}>
              <Wifi className="w-3 h-3 text-emerald-400" />
              <span className="text-[11px] font-semibold text-emerald-400">LIVE</span>
            </div>

            {/* Refresh */}
            <button
              onClick={onRefresh}
              title={`Updated: ${new Date(lastUpdated).toLocaleTimeString()}`}
              className="btn-ghost flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-orange-400' : 'text-slate-400'}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>

            {/* Mobile menu toggle */}
            <button
              className="md:hidden btn-ghost p-2"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileOpen && (
        <div className="md:hidden border-t border-white/5 px-4 py-3 space-y-1" style={{ background: 'rgba(10,15,30,0.95)' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNav(item.id)}
                className={`nav-pill w-full text-left ${isActive ? 'active' : ''}`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
                {item.badge !== undefined && item.badge > 0 && (
                  <span style={{
                    background: 'linear-gradient(135deg,#f97316,#ef4444)',
                    borderRadius: '99px', fontSize: '10px', fontWeight: 700,
                    padding: '1px 6px', color: 'white',
                  }}>{item.badge}</span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
