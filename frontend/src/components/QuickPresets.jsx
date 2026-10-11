import React from 'react';
import { PRESET_ITEMS } from '../services/mockData';
import { Sparkles, Recycle, Apple, AlertTriangle, Trash2, HelpCircle, Coffee } from 'lucide-react';

const ICON_MAP = {
  Recycle,
  Apple,
  AlertTriangle,
  Trash2,
  HelpCircle,
  Coffee,
};

export default function QuickPresets({ onSelectPreset, disabled }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 p-5 md:p-6 transition-all">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
        <div>
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-eco-600" />
            Hackathon Demo Presets (1-Click Test)
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Quickly test the 4 core streams, food-soiled contamination, and uncertainty guardrails.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {PRESET_ITEMS.map((item) => {
          const Icon = ICON_MAP[item.icon] || Sparkles;
          return (
            <button
              key={item.id}
              type="button"
              disabled={disabled}
              onClick={() => onSelectPreset(item)}
              className="flex flex-col items-start p-3 rounded-xl border border-slate-200 hover:border-eco-400 hover:bg-eco-50/40 text-left transition-all active:scale-[0.98] group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-center justify-between w-full mb-1.5">
                <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold border ${item.badgeColor}`}>
                  {item.categoryLabel}
                </span>
                <Icon className="w-3.5 h-3.5 text-slate-400 group-hover:text-eco-600 transition-colors" />
              </div>
              <span className="text-xs font-bold text-slate-800 group-hover:text-eco-800 truncate w-full">
                {item.title}
              </span>
              <span className="text-[10px] text-slate-400 truncate w-full mt-0.5">
                {item.description}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
