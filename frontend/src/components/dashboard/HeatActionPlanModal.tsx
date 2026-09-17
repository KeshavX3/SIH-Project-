import React, { useState } from 'react';
import { 
  X, 
  ShieldAlert, 
  Languages, 
  AlertTriangle, 
  Droplets, 
  Building2, 
  Users, 
  HeartHandshake,
  CheckCircle2
} from 'lucide-react';
import { NDMA_PROTOCOLS } from '../../services/api';

interface HeatActionPlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentRiskLevel?: string;
}

export const HeatActionPlanModal: React.FC<HeatActionPlanModalProps> = ({
  isOpen,
  onClose,
  currentRiskLevel = 'EXTREME'
}) => {
  const [lang, setLang] = useState<'en' | 'hi'>('en');
  
  // Default selected tab based on current city risk level
  const getInitialTier = () => {
    if (currentRiskLevel === 'EXTREME') return 'RED';
    if (currentRiskLevel === 'HIGH') return 'ORANGE';
    if (currentRiskLevel === 'MODERATE') return 'YELLOW';
    return 'NORMAL';
  };

  const [selectedTier, setSelectedTier] = useState<string>(getInitialTier());

  if (!isOpen) return null;

  const currentProtocol = NDMA_PROTOCOLS.find((p) => p.tier === selectedTier) || NDMA_PROTOCOLS[3];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div 
        className="relative w-full max-w-4xl max-h-[90vh] bg-[#0C121E] border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-5 border-b border-white/10 flex items-center justify-between bg-[#080D17]">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-display font-bold text-white tracking-wide">
                  {lang === 'en' ? 'NDMA Heat Action Plan (HAP) Protocols' : 'राष्ट्रीय आपदा प्रबंधन (NDMA) लू कार्य योजना'}
                </h2>
                <span className="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  {lang === 'en' ? 'Official Guidelines' : 'सरकारी दिशानिर्देश'}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {lang === 'en' 
                  ? 'Standard operating procedures for municipal authorities, medical response, and citizens.' 
                  : 'नगर निगम, स्वास्थ्य विभाग और नागरिकों के लिए मानक संचालन प्रक्रिया (एसओपी)।'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Language Switcher */}
            <div className="flex items-center bg-slate-900 p-1 rounded-xl border border-white/10 text-xs">
              <Languages className="w-3.5 h-3.5 text-slate-400 ml-2 mr-1" />
              <button
                onClick={() => setLang('en')}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  lang === 'en' ? 'bg-rose-500 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLang('hi')}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  lang === 'hi' ? 'bg-rose-500 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                हिन्दी
              </button>
            </div>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tier Tabs */}
        <div className="grid grid-cols-4 border-b border-white/10 bg-[#0A0F1B]">
          {NDMA_PROTOCOLS.map((p) => {
            const isSelected = selectedTier === p.tier;
            return (
              <button
                key={p.tier}
                onClick={() => setSelectedTier(p.tier)}
                className={`py-3.5 px-3 flex flex-col items-center justify-center transition-all border-b-2 text-center ${
                  isSelected 
                    ? 'border-rose-500 bg-white/[0.04]' 
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/[0.02]'
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <span 
                    className="w-2.5 h-2.5 rounded-full" 
                    style={{ backgroundColor: p.color }}
                  />
                  <span className={`text-xs font-bold tracking-wide ${isSelected ? 'text-white' : 'text-slate-400'}`}>
                    {p.tier}
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 mt-0.5 font-mono">
                  {p.threshold_temp}
                </span>
              </button>
            );
          })}
        </div>

        {/* Protocol Details Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 custom-scrollbar">
          
          {/* Active Tier Banner */}
          <div 
            className="p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
            style={{ 
              backgroundColor: `${currentProtocol.color}15`, 
              borderColor: `${currentProtocol.color}40` 
            }}
          >
            <div>
              <div className="flex items-center gap-2">
                <span 
                  className="w-3 h-3 rounded-full animate-pulse" 
                  style={{ backgroundColor: currentProtocol.color }} 
                />
                <h3 className="font-display font-bold text-white text-base">
                  {lang === 'en' ? currentProtocol.title_en : currentProtocol.title_hi}
                </h3>
              </div>
              <p className="text-xs text-slate-300 mt-1">
                {lang === 'en' 
                  ? `Threshold: Temperature ${currentProtocol.threshold_temp} | Heat Index: ${currentProtocol.threshold_hi}`
                  : `मानक सीमा: तापमान ${currentProtocol.threshold_temp} | हीट इंडेक्स: ${currentProtocol.threshold_hi}`}
              </p>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-black/40 border border-white/10 text-xs font-mono text-slate-300">
              {lang === 'en' ? 'Trigger Status: ACTIVE ENFORCEMENT' : 'स्थिति: प्रभावी दिशानिर्देश'}
            </div>
          </div>

          {/* 3 Action Pillars */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            
            {/* 1. Municipal & Govt Directives */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-white/5 space-y-3">
              <div className="flex items-center space-x-2 text-rose-400">
                <Building2 className="w-4 h-4" />
                <h4 className="text-xs font-display font-bold uppercase tracking-wider text-white">
                  {lang === 'en' ? 'Municipal Administration & Health Directives' : 'नगर निगम व स्वास्थ्य विभाग हेतु आदेश'}
                </h4>
              </div>
              <ul className="space-y-2.5">
                {(lang === 'en' ? currentProtocol.municipal_actions_en : currentProtocol.municipal_actions_hi).map((act, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start space-x-2.5 leading-relaxed">
                    <CheckCircle2 className="w-3.5 h-3.5 text-rose-500 shrink-0 mt-0.5" />
                    <span>{act}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* 2. Public Health & Citizen Advisory */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-white/5 space-y-3">
              <div className="flex items-center space-x-2 text-amber-400">
                <Droplets className="w-4 h-4" />
                <h4 className="text-xs font-display font-bold uppercase tracking-wider text-white">
                  {lang === 'en' ? 'Public Health & Citizen Advisories' : 'नागरिकों हेतु स्वास्थ्य परामर्श एवं सावधानियां'}
                </h4>
              </div>
              <ul className="space-y-2.5">
                {(lang === 'en' ? currentProtocol.citizen_advisories_en : currentProtocol.citizen_advisories_hi).map((adv, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start space-x-2.5 leading-relaxed">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
                    <span>{adv}</span>
                  </li>
                ))}
              </ul>
            </div>

          </div>

          {/* 3. Vulnerable Groups Focus */}
          <div className="p-4 rounded-xl bg-slate-900/40 border border-white/5">
            <div className="flex items-center space-x-2 text-cyan-400 mb-3">
              <Users className="w-4 h-4" />
              <h4 className="text-xs font-display font-bold uppercase tracking-wider text-white">
                {lang === 'en' ? 'High-Risk Vulnerable Cohorts in Jaipur' : 'जयपुर में सर्वाधिक संवेदनशील वर्ग'}
              </h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {(lang === 'en' ? currentProtocol.vulnerable_groups_en : currentProtocol.vulnerable_groups_hi).map((grp, i) => (
                <span 
                  key={i}
                  className="px-3 py-1 rounded-lg text-xs bg-slate-800/80 text-slate-200 border border-white/10 flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                  {grp}
                </span>
              ))}
            </div>
          </div>

          {/* Emergency Helpline Footer */}
          <div className="p-3.5 rounded-xl bg-slate-950 border border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <HeartHandshake className="w-4 h-4 text-emerald-400" />
              <span>
                {lang === 'en' ? 'Rajasthan State Emergency Helpline:' : 'राजस्थान राज्य आपातकालीन हेल्पलाइन:'}
                <strong className="text-white ml-1.5">108 (Ambulance) / 1070 (Disaster Relief)</strong>
              </span>
            </div>
            <span className="text-[11px] text-slate-400">
              {lang === 'en' ? 'Aligned with National Disaster Management Authority (NDMA)' : 'राष्ट्रीय आपदा प्रबंधन प्राधिकरण (NDMA) के मानकों पर आधारित'}
            </span>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-white/10 bg-[#080D17] flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold tracking-wide transition-colors"
          >
            {lang === 'en' ? 'Close Protocol View' : 'बंद करें'}
          </button>
        </div>

      </div>
    </div>
  );
};
