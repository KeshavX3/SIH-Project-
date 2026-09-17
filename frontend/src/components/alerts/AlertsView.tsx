import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, Clock, MapPin, ShieldCheck, PhoneCall, Check, Filter } from 'lucide-react';
import { AlertItem } from '../../types';
import { acknowledgeAlert } from '../../services/api';

interface AlertsViewProps {
  alerts: AlertItem[];
  onAlertAcknowledged: (updated: AlertItem) => void;
}

const SEV_STYLES: Record<string, { bg: string; border: string; color: string; dot: string }> = {
  EXTREME: { bg: 'rgba(239,68,68,0.12)',  border: 'rgba(239,68,68,0.3)',  color: '#f87171', dot: '#ef4444' },
  HIGH:    { bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.3)', color: '#fb923c', dot: '#f97316' },
  MODERATE:{ bg: 'rgba(251,191,36,0.12)', border: 'rgba(251,191,36,0.3)', color: '#fbbf24', dot: '#fbbf24' },
  LOW:     { bg: 'rgba(56,189,248,0.10)', border: 'rgba(56,189,248,0.2)', color: '#38bdf8', dot: '#38bdf8' },
};

export const AlertsView: React.FC<AlertsViewProps> = ({ alerts, onAlertAcknowledged }) => {
  const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'ACKNOWLEDGED'>('ALL');
  const [ackId, setAckId] = useState<number | null>(null);

  const filtered = alerts.filter((a) => {
    if (filter === 'ACTIVE') return a.status === 'ACTIVE';
    if (filter === 'ACKNOWLEDGED') return a.status === 'ACKNOWLEDGED';
    return true;
  });

  const handleAck = async (id: number) => {
    setAckId(id);
    try {
      const updated = await acknowledgeAlert(id);
      onAlertAcknowledged(updated);
    } catch (e) {
      console.error(e);
    } finally {
      setAckId(null);
    }
  };

  return (
    <div className="space-y-5 animate-fade-up">

      {/* ── Top bar ─────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, Inter, sans-serif' }}>
            Heat Alerts
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">{alerts.filter(a => a.status === 'ACTIVE').length} active · {alerts.length} total</p>
        </div>

        {/* Emergency line */}
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-2xl" style={{
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.22)',
        }}>
          <PhoneCall className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <div>
            <div className="text-[10px] text-rose-300/70 font-semibold uppercase tracking-wider">Emergency</div>
            <div className="text-sm font-black text-white">1077 <span className="text-xs text-slate-400 font-normal">/ 108</span></div>
          </div>
        </div>
      </div>

      {/* ── Filter pills ─────────────────────────── */}
      <div className="flex items-center gap-2">
        <Filter className="w-3.5 h-3.5 text-slate-500" />
        {(['ALL', 'ACTIVE', 'ACKNOWLEDGED'] as const).map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className="px-3 py-1.5 text-xs font-semibold rounded-xl transition-all"
            style={{
              background: filter === s ? 'linear-gradient(135deg,rgba(249,115,22,0.25),rgba(239,68,68,0.25))' : 'rgba(255,255,255,0.05)',
              border: `1px solid ${filter === s ? 'rgba(249,115,22,0.4)' : 'rgba(255,255,255,0.08)'}`,
              color: filter === s ? 'white' : '#94a3b8',
            }}
          >
            {s} ({alerts.filter(a => s === 'ALL' || a.status === s).length})
          </button>
        ))}
      </div>

      {/* ── Alerts list ─────────────────────────── */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="card p-10 rounded-2xl text-center">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
            <div className="font-bold text-white">No alerts</div>
            <p className="text-xs text-slate-400 mt-1">All conditions within normal thresholds.</p>
          </div>
        ) : (
          filtered.map((alert) => {
            const isActive = alert.status === 'ACTIVE';
            const sty = SEV_STYLES[alert.severity] ?? SEV_STYLES.LOW;
            return (
              <div key={alert.id} className="rounded-2xl overflow-hidden transition-all" style={{
                background: isActive ? sty.bg : 'rgba(255,255,255,0.03)',
                border: `1px solid ${isActive ? sty.border : 'rgba(255,255,255,0.07)'}`,
                opacity: isActive ? 1 : 0.65,
              }}>
                <div className="p-4">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      {/* Severity dot */}
                      <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0 animate-pulse-soft" style={{ background: sty.dot }} />

                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-lg" style={{ background: sty.bg, color: sty.color, border: `1px solid ${sty.border}` }}>
                            {alert.severity}
                          </span>
                          {alert.htsi_value && (
                            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-lg" style={{ background: 'rgba(239,68,68,0.1)', color: '#f87171', border: '1px solid rgba(239,68,68,0.2)' }}>
                              HTSI {alert.htsi_value.toFixed(1)}
                            </span>
                          )}
                        </div>

                        <h3 className="text-sm font-bold text-white mt-2">{alert.title}</h3>

                        <div className="flex flex-wrap items-center gap-3 mt-1.5 text-xs text-slate-400">
                          <span className="flex items-center gap-1"><MapPin className="w-3 h-3 text-amber-400" />{alert.ward_name}</span>
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          <span className="font-semibold" style={{ color: isActive ? sty.color : '#34d399' }}>
                            {isActive ? '● Active' : '✓ Acknowledged'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Action button */}
                    <div className="flex-shrink-0 sm:self-start">
                      {isActive ? (
                        <button
                          onClick={() => handleAck(alert.id)}
                          disabled={ackId === alert.id}
                          className="btn-fire flex items-center gap-2 px-4 py-2 text-xs disabled:opacity-50"
                        >
                          <ShieldCheck className="w-3.5 h-3.5" />
                          {ackId === alert.id ? 'Dispatching...' : 'Acknowledge'}
                        </button>
                      ) : (
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold" style={{ background: 'rgba(52,211,153,0.1)', border: '1px solid rgba(52,211,153,0.2)', color: '#34d399' }}>
                          <Check className="w-3.5 h-3.5" />
                          Done
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Reason */}
                  <div className="mt-3 px-3 py-2.5 rounded-xl text-xs text-slate-300 leading-relaxed" style={{ background: 'rgba(0,0,0,0.2)' }}>
                    {alert.reason}
                  </div>

                  {/* Recommendations */}
                  {alert.recommendations && alert.recommendations.length > 0 && (
                    <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {alert.recommendations.map((rec, i) => (
                        <div key={i} className="flex items-start gap-2 p-2.5 rounded-xl text-[11px] text-slate-300 leading-relaxed" style={{ background: 'rgba(255,255,255,0.04)' }}>
                          <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" style={{ color: isActive ? sty.color : '#34d399' }} />
                          {rec}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
