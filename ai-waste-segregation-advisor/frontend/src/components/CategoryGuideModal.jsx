import React from 'react';
import { X, Recycle, Apple, AlertTriangle, Trash2, ShieldCheck } from 'lucide-react';

export default function CategoryGuideModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 transition-all">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-eco-100 text-eco-700 rounded-lg">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Four-Stream Waste Segregation Guide
              </h3>
              <p className="text-xs text-slate-500">
                Standard municipal rules & contamination prevention protocols
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-5 space-y-4">
          {/* Recyclables */}
          <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50">
            <div className="flex items-center gap-2 mb-1.5">
              <div className="p-1.5 rounded bg-blue-500 text-white">
                <Recycle className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-blue-900">
                1. Recyclable Stream (Blue Bin)
              </h4>
            </div>
            <p className="text-xs text-blue-800 leading-relaxed mb-2">
              Clean, rigid materials that can be remanufactured. Must be emptied of fluids and wiped or rinsed.
            </p>
            <div className="text-[11px] text-blue-900 bg-white/80 p-2.5 rounded-lg border border-blue-100">
              <strong>Accepted:</strong> Aluminum/tin cans, PET/HDPE bottles, clean cardboard, office paper, clean glass jars.<br />
              <strong>Never:</strong> Greasy pizza boxes, styrofoam, garden hoses, chip packets, batteries.
            </div>
          </div>

          {/* Organics */}
          <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/50">
            <div className="flex items-center gap-2 mb-1.5">
              <div className="p-1.5 rounded bg-emerald-500 text-white">
                <Apple className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-emerald-900">
                2. Organic Compost (Green Bin)
              </h4>
            </div>
            <p className="text-xs text-emerald-800 leading-relaxed mb-2">
              Biodegradable biomass that decomposes aerobically to form nutrient-rich humus and prevent methane emissions.
            </p>
            <div className="text-[11px] text-emerald-900 bg-white/80 p-2.5 rounded-lg border border-emerald-100">
              <strong>Accepted:</strong> Fruit & vegetable trimmings, coffee grounds, eggshells, leaves, yard clippings.<br />
              <strong>Never:</strong> Plastic fruit stickers, treated lumber, pet waste, synthetic teabags.
            </div>
          </div>

          {/* Hazardous */}
          <div className="p-4 rounded-xl border border-amber-300 bg-amber-50/60">
            <div className="flex items-center gap-2 mb-1.5">
              <div className="p-1.5 rounded bg-amber-500 text-white">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-amber-900">
                3. Hazardous Waste (Special Collection / HHW)
              </h4>
            </div>
            <p className="text-xs text-amber-800 leading-relaxed mb-2">
              Toxic, flammable, corrosive, or heavy metal waste. Strictly prohibited in curbside bins to prevent landfill fires and groundwater contamination.
            </p>
            <div className="text-[11px] text-amber-900 bg-white/80 p-2.5 rounded-lg border border-amber-200">
              <strong>Accepted:</strong> Batteries (lithium/alkaline), fluorescent CFL bulbs (mercury), motor oil, paint, pesticides, medical sharps.<br />
              <strong>Handling:</strong> Tape battery terminals, transport upright, deliver to designated HHW depot.
            </div>
          </div>

          {/* General */}
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70">
            <div className="flex items-center gap-2 mb-1.5">
              <div className="p-1.5 rounded bg-slate-600 text-white">
                <Trash2 className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-slate-900">
                4. General Waste (Black / Gray Landfill Bin)
              </h4>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed mb-2">
              Non-hazardous, non-recyclable items that cannot be processed in current circular streams.
            </p>
            <div className="text-[11px] text-slate-800 bg-white/80 p-2.5 rounded-lg border border-slate-200">
              <strong>Accepted:</strong> Greasy food-soiled cardboard, styrofoam cups, broken ceramics, chip bags, diapers, vacuum dust.<br />
              <strong>Handling:</strong> Bag securely to prevent litter and worker exposure.
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 text-xs font-bold text-white bg-eco-600 hover:bg-eco-700 rounded-xl transition-colors"
          >
            Understood
          </button>
        </div>
      </div>
    </div>
  );
}
