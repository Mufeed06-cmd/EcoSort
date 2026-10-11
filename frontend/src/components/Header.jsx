import React from 'react';
import { Leaf, Info, FlaskConical, Zap } from 'lucide-react';

export default function Header({ onOpenGuide, forceMock }) {
  return (
    <header className="bg-white/80 backdrop-blur-md sticky top-0 z-40 border-b border-slate-200/80 transition-all">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-eco-600 to-eco-400 text-white flex items-center justify-center shadow-md shadow-eco-600/20">
            <Leaf className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-black tracking-tight text-slate-900">
                EcoSort AI
              </h1>
              <span className="hidden sm:inline-block px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-eco-100 text-eco-800 border border-eco-200">
                Environmental Hacks MVP
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium hidden sm:block">
              AI Waste Segregation Advisor • Amazon Bedrock & Rules Engine
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          {/* Engine Status Pill */}
          <div
            className={`hidden xs:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${
              forceMock
                ? 'bg-amber-50 text-amber-800 border-amber-200'
                : 'bg-purple-50 text-purple-800 border-purple-200'
            }`}
          >
            {forceMock ? (
              <>
                <FlaskConical className="w-3.5 h-3.5 text-amber-600" />
                <span>Mock Mode Active</span>
              </>
            ) : (
              <>
                <Zap className="w-3.5 h-3.5 text-purple-600" />
                <span>Bedrock Mode Active</span>
              </>
            )}
          </div>

          <button
            onClick={onOpenGuide}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-eco-700 bg-slate-100/80 hover:bg-eco-50 rounded-xl border border-slate-200/80 transition-colors"
          >
            <Info className="w-4 h-4 text-eco-600" />
            <span className="hidden sm:inline">Segregation Guide</span>
          </button>
        </div>
      </div>
    </header>
  );
}
