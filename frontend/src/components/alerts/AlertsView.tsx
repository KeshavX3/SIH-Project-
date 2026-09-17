import React, { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  ShieldCheck, 
  PhoneCall, 
  Send,
  Filter,
  Check
} from 'lucide-react';
import { AlertItem } from '../../types';
import { acknowledgeAlert } from '../../services/api';

interface AlertsViewProps {
  alerts: AlertItem[];
  onAlertAcknowledged: (updated: AlertItem) => void;
}

export const AlertsView: React.FC<AlertsViewProps> = ({
  alerts,
  onAlertAcknowledged,
}) => {
  const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'ACKNOWLEDGED'>('ALL');
  const [acknowledgingId, setAcknowledgingId] = useState<number | null>(null);

  const filteredAlerts = alerts.filter((a) => {
    if (filter === 'ACTIVE') return a.status === 'ACTIVE';
    if (filter === 'ACKNOWLEDGED') return a.status === 'ACKNOWLEDGED';
    return true;
  });

  const handleAcknowledge = async (id: number) => {
    setAcknowledgingId(id);
    try {
      const updated = await acknowledgeAlert(id);
      onAlertAcknowledged(updated);
    } catch (err) {
      console.error('Failed to acknowledge alert', err);
    } finally {
      setAcknowledgingId(null);
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'EXTREME':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
      case 'MODERATE':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      default:
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Emergency Contacts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-white/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <span className="p-2 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30 shadow-glow-red">
                <AlertTriangle className="w-5 h-5 animate-pulse" />
              </span>
              <h2 className="text-base sm:text-lg font-display font-bold text-white">
                Early Warnings & Municipal Heat Action SOPs
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Automated multi-agency alert dispatch for Jaipur Municipal Corporation, Disaster Management Authorities (SDMA), and public health networks.
            </p>
          </div>

          {/* Filter tabs */}
          <div className="mt-4 flex items-center space-x-2 text-xs">
            <span className="text-slate-400 flex items-center gap-1 font-mono text-[11px]">
              <Filter className="w-3.5 h-3.5" /> Filter:
            </span>
            {(['ALL', 'ACTIVE', 'ACKNOWLEDGED'] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                  filter === status
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30 shadow-sm'
                    : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-white/5'
                }`}
              >
                {status} ({alerts.filter(a => status === 'ALL' || a.status === status).length})
              </button>
            ))}
          </div>
        </div>

        {/* Emergency Rapid Response Helpline */}
        <div className="glass-panel p-5 rounded-2xl border border-white/10 flex flex-col justify-between bg-gradient-to-br from-slate-900 to-rose-950/30">
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-rose-400 font-bold flex items-center gap-1.5">
              <PhoneCall className="w-3.5 h-3.5" />
              Control Room Hotline
            </div>
            <div className="text-xl font-display font-black text-white mt-2">
              1077 <span className="text-xs font-normal text-slate-400">/ 0141-2742900</span>
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Jaipur District Emergency Operations Center (DEOC) 24/7 Heatwave Dispatch.
            </div>
          </div>

          <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between text-xs text-slate-300 font-medium">
            <span>Ambulance Heat Unit:</span>
            <span className="font-mono text-emerald-400 font-bold">108</span>
          </div>
        </div>

      </div>

      {/* Alerts Feed */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="glass-panel p-8 rounded-2xl border border-white/10 text-center">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h3 className="text-sm font-bold text-white mt-2">No alerts matching filter</h3>
            <p className="text-xs text-slate-400 mt-1">All conditions within normal thresholds.</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const isActive = alert.status === 'ACTIVE';
            return (
              <div
                key={alert.id}
                className={`glass-panel p-5 rounded-2xl border transition-all ${
                  isActive ? 'border-rose-500/30 bg-slate-900/70 shadow-lg' : 'border-white/5 bg-slate-950/40 opacity-75'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div className="flex items-start space-x-3">
                    <span className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold uppercase border ${getSeverityBadge(alert.severity)}`}>
                      {alert.severity}
                    </span>
                    <div>
                      <h3 className="text-sm font-bold text-white flex items-center gap-2">
                        {alert.title}
                        {alert.htsi_value && (
                          <span className="text-xs font-mono text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                            HTSI {alert.htsi_value.toFixed(1)}
                          </span>
                        )}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1">
                        <span className="flex items-center gap-1 text-slate-300">
                          <MapPin className="w-3 h-3 text-amber-400" />
                          {alert.ward_name}
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-500" />
                          {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <span>•</span>
                        <span className={`font-mono text-[11px] font-bold ${isActive ? 'text-rose-400 animate-pulse' : 'text-emerald-400'}`}>
                          {alert.status}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Acknowledge Button */}
                  <div>
                    {isActive ? (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={acknowledgingId === alert.id}
                        className="w-full md:w-auto flex items-center justify-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-rose-500 hover:bg-rose-600 text-white shadow-glow-red transition-colors disabled:opacity-50"
                      >
                        <ShieldCheck className="w-4 h-4" />
                        <span>{acknowledgingId === alert.id ? 'Dispatching SOP...' : 'Acknowledge & Dispatch SOP'}</span>
                      </button>
                    ) : (
                      <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
                        <Check className="w-3.5 h-3.5" />
                        <span>SOP Dispatched & Acknowledged</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Trigger Reason */}
                <div className="mt-3 p-3 rounded-xl bg-slate-900/40 border border-white/5 text-xs text-slate-300">
                  <strong className="text-slate-200">Alert Trigger Condition: </strong>
                  {alert.reason}
                </div>

                {/* SOP Recommendations Checklist */}
                {alert.recommendations && alert.recommendations.length > 0 && (
                  <div className="mt-3 space-y-1.5">
                    <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold">
                      Mandated Heat Action Checklist:
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                      {alert.recommendations.map((rec, idx) => (
                        <div key={idx} className="flex items-start space-x-2 p-2 rounded-lg bg-slate-900/30 border border-white/5">
                          <CheckCircle2 className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${isActive ? 'text-amber-400' : 'text-emerald-400'}`} />
                          <span className="text-slate-300 text-[11px]">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
