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
  DEMO_ALERTS
} from './services/api';
import { DashboardSummary, WardListItem, AlertItem } from './types';
import { ShieldCheck, Info, Heart, Award } from 'lucide-react';

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
      console.warn('Using cached / mock state', err);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleSelectWard = (wardId: number) => {
    setSelectedWardId(wardId);
    setActiveTab('wards');
  };

  const handleAlertAcknowledged = (updatedAlert: AlertItem) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === updatedAlert.id ? updatedAlert : a))
    );
  };

  const activeAlertCount = alerts.filter((a) => a.status === 'ACTIVE').length;

  return (
    <div className="min-h-screen bg-[#070A11] text-slate-100 flex flex-col selection:bg-rose-500/30 selection:text-rose-200">
      
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeAlertCount={activeAlertCount}
        systemStatus={summary.system_status}
        lastUpdated={lastUpdated}
        onRefresh={loadData}
        isRefreshing={isRefreshing}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {activeTab === 'overview' && (
          <div className="space-y-6 animate-fade-in">
            <HeroMetrics summary={summary} />
            <RiskDistribution
              summary={summary}
              wards={wards}
              onSelectWard={handleSelectWard}
            />
          </div>
        )}

        {activeTab === 'map' && (
          <div className="animate-fade-in">
            <JaipurHeatMap
              wards={wards}
              onSelectWard={handleSelectWard}
            />
          </div>
        )}

        {activeTab === 'simulator' && (
          <div className="animate-fade-in">
            <ThermalSimulator />
          </div>
        )}

        {activeTab === 'wards' && (
          <div className="animate-fade-in">
            <WardAnalytics
              wards={wards}
              selectedWardId={selectedWardId}
              onSelectWard={setSelectedWardId}
            />
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="animate-fade-in">
            <AlertsView
              alerts={alerts}
              onAlertAcknowledged={handleAlertAcknowledged}
            />
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-white/5 bg-[#05080E] py-6 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Award className="w-4 h-4 text-rose-500" />
            <span className="font-semibold text-slate-300">HeatGuard AI</span>
            <span>—</span>
            <span>Smart India Hackathon (SIH26083)</span>
          </div>

          <div className="flex items-center space-x-4 text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <Info className="w-3.5 h-3.5 text-slate-400" />
              Demo City: Jaipur, Rajasthan, India
            </span>
            <span>•</span>
            <span className="text-slate-400">
              Synthetic Meteorological Data Mode
            </span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default App;
