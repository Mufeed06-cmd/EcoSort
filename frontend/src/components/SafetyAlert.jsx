import React from 'react';
import { AlertOctagon, ShieldAlert, AlertTriangle } from 'lucide-react';

export default function SafetyAlert({ warnings = [] }) {
  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="rounded-xl border border-rose-300 bg-rose-50/90 p-4 shadow-sm transition-all animate-fade-in">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-rose-600 text-white shrink-0 mt-0.5">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-bold text-rose-900 tracking-tight flex items-center gap-1.5">
            Critical Safety & Environmental Precautions
          </h4>
          <p className="text-xs text-rose-700 mt-0.5 mb-2.5">
            Adhere strictly to these protective measures to prevent fires, toxic exposure, or recycling stream contamination.
          </p>
          <ul className="space-y-1.5">
            {warnings.map((warn, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-xs font-medium text-rose-800 bg-white/70 border border-rose-200/60 rounded-lg p-2"
              >
                <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <span>{warn}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
