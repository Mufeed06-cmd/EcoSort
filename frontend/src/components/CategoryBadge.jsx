import React from 'react';
import { Recycle, Apple, AlertTriangle, Trash2, HelpCircle } from 'lucide-react';

const CATEGORY_CONFIG = {
  recyclable: {
    label: 'Recyclable Stream',
    bg: 'bg-blue-50 border-blue-200 text-blue-700',
    iconBg: 'bg-blue-500 text-white',
    icon: Recycle,
    description: 'Blue Bin / Dry Recycling',
  },
  organic: {
    label: 'Organic Compost',
    bg: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    iconBg: 'bg-emerald-500 text-white',
    icon: Apple,
    description: 'Green Bin / Food & Yard Scraps',
  },
  hazardous: {
    label: 'Hazardous Waste',
    bg: 'bg-amber-50 border-amber-300 text-amber-800',
    iconBg: 'bg-amber-500 text-white',
    icon: AlertTriangle,
    description: 'Special Drop-Off / HHW Facility Only',
  },
  general: {
    label: 'General Landfill Waste',
    bg: 'bg-slate-100 border-slate-300 text-slate-700',
    iconBg: 'bg-slate-600 text-white',
    icon: Trash2,
    description: 'Black/Gray Bin / Non-Recyclable',
  },
};

export default function CategoryBadge({ category, isUncertain, size = 'normal' }) {
  const normCategory = (category || 'general').toLowerCase();
  const config = CATEGORY_CONFIG[normCategory] || CATEGORY_CONFIG.general;
  const Icon = config.icon;

  if (size === 'large') {
    return (
      <div className={`flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-xl border ${config.bg}`}>
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-lg shadow-sm ${config.iconBg}`}>
            <Icon className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight">{config.label}</span>
              {isUncertain && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded-full bg-rose-100 text-rose-700 border border-rose-300">
                  <HelpCircle className="w-3 h-3" />
                  Uncertainty Guard
                </span>
              )}
            </div>
            <p className="text-xs opacity-80 mt-0.5">{config.description}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${config.bg}`}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{config.label}</span>
      {isUncertain && (
        <span className="ml-1 px-1.5 py-0.2 rounded-full bg-rose-100 text-rose-700 text-[10px]">
          Cautious
        </span>
      )}
    </span>
  );
}
