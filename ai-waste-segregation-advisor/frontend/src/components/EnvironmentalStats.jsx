import React from 'react';
import { ShieldCheck, Recycle, Flame, Trees } from 'lucide-react';

export default function EnvironmentalStats({ stats }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex items-center gap-3">
        <div className="p-2.5 rounded-lg bg-blue-50 text-blue-600">
          <Recycle className="w-4 h-4" />
        </div>
        <div>
          <div className="text-base font-black text-slate-800">{stats.analyzed}</div>
          <div className="text-[11px] text-slate-500 font-medium">Items Classified</div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex items-center gap-3">
        <div className="p-2.5 rounded-lg bg-amber-50 text-amber-600">
          <ShieldCheck className="w-4 h-4" />
        </div>
        <div>
          <div className="text-base font-black text-slate-800">{stats.hazardousSafeguarded}</div>
          <div className="text-[11px] text-slate-500 font-medium">Hazards Isolated</div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex items-center gap-3">
        <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-600">
          <Trees className="w-4 h-4" />
        </div>
        <div>
          <div className="text-base font-black text-slate-800">{stats.contaminationPrevented}</div>
          <div className="text-[11px] text-slate-500 font-medium">Contaminations Stopped</div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex items-center gap-3">
        <div className="p-2.5 rounded-lg bg-rose-50 text-rose-600">
          <Flame className="w-4 h-4" />
        </div>
        <div>
          <div className="text-base font-black text-slate-800">{stats.batteryFiresPrevented}</div>
          <div className="text-[11px] text-slate-500 font-medium">Fire Risks Neutralized</div>
        </div>
      </div>
    </div>
  );
}
