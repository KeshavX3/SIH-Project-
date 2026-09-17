import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/layout/Navbar';
import { HeroMetrics } from './components/dashboard/HeroMetrics';
import { RiskDistribution } from './components/dashboard/RiskDistribution';
import { JaipurHeatMap } from './components/map/JaipurHeatMap';
import { ThermalSimulator } from './components/calculator/ThermalSimulator';
import { AlertsView } from './components/alerts/AlertsView';
import { WardAnalytics } from './components/wards/WardAnalytics';
import {
  fetchDashboardSummary,
  fetchWards,
  fetchAlerts,
  DEMO_DASHBOARD_SUMMARY,
  DEMO_WARDS,
  DEMO_ALERTS,
} from './services/api';
import { DashboardSummary, WardListItem, AlertItem } from './types';
import { Heart, Flame } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [summary, setSummary] = useState<DashboardSummary>(DEMO_DASHBOARD_SUMMARY);
  const [wards, setWards] = useState<WardListItem[]>(DEMO_WARDS);
  const [alerts, setAlerts] = useState<AlertItem[]>(DEMO_ALERTS);
  const [selectedWardId, setSelectedWardId] = useState<number>(1);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<string>(new Date().toISOString());

  const loadData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [sumData, wardsData, alertsData] = await Promise.all([
        fetchDashboardSummary(),
        fetchWards(),
        fetchAlerts(),
      ]);
      setSummary(sumData);
      setWards(wardsData);
      setAlerts(alertsData);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      console.warn('Using cached data', err);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleSelectWard = (wardId: number) => {
    setSelectedWardId(wardId);
    setActiveTab('wards');
  };

  const handleAlertAcknowledged = (updatedAlert: AlertItem) => {
    setAlerts((prev) => prev.map((a) => (a.id === updatedAlert.id ? updatedAlert : a)));
  };

  const activeAlertCount = alerts.filter((a) => a.status === 'ACTIVE').length;

  return (
    <div className="app-bg min-h-screen flex flex-col" style={{ color: '#f1f5f9' }}>

      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeAlertCount={activeAlertCount}
        systemStatus={summary.system_status}
        lastUpdated={lastUpdated}
        onRefresh={loadData}
        isRefreshing={isRefreshing}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 space-y-6">

        {activeTab === 'overview' && (
          <div className="space-y-6">
            <HeroMetrics summary={summary} />
            <RiskDistribution summary={summary} wards={wards} onSelectWard={handleSelectWard} />
          </div>
        )}

        {activeTab === 'map' && (
          <JaipurHeatMap wards={wards} onSelectWard={handleSelectWard} />
        )}

        {activeTab === 'simulator' && (
          <ThermalSimulator />
        )}

        {activeTab === 'wards' && (
          <WardAnalytics wards={wards} selectedWardId={selectedWardId} onSelectWard={setSelectedWardId} />
        )}

        {activeTab === 'alerts' && (
          <AlertsView alerts={alerts} onAlertAcknowledged={handleAlertAcknowledged} />
        )}

      </main>

      {/* Footer */}
      <footer className="mt-auto py-5 text-xs text-slate-600" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Flame className="w-3.5 h-3.5 text-orange-500" />
            <span className="text-slate-500 font-medium">HeatGuard AI</span>
            <span className="text-slate-700">—</span>
            <span>Extreme Heat Early Warning Platform</span>
          </div>
          <div className="flex items-center gap-1">
            <Heart className="w-3 h-3 text-rose-600" />
            <span>Jaipur, Rajasthan · Real-time data</span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default App;
