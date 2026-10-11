import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  Leaf,
  Layers,
  ArrowRight,
  ShieldCheck,
  Cpu,
  RefreshCw,
  ExternalLink,
  HelpCircle,
  FlaskConical,
  Zap,
  Info
} from 'lucide-react';
import CategoryBadge from './CategoryBadge';
import SafetyAlert from './SafetyAlert';

export default function AnalysisResult({ result, onReset }) {
  if (!result) return null;

  const {
    item_name,
    category,
    is_uncertain,
    confidence,
    confidence_level,
    summary,
    material,
    disposal_instructions = [],
    safety_warnings = [],
    preparation_steps = [],
    alternative_options = [],
    environmental_impact,
    rules_applied = [],
    source = 'mock',
    ai_explanation,
  } = result;

  const isMock = source === 'mock';
  const confidencePercentage = Math.round(confidence * 100);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 p-5 md:p-6 transition-all animate-fade-in space-y-5">
      {/* Engine Source Banner (Requirement 7: Clearly Distinguishes Mock vs Bedrock) */}
      <div
        className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl border ${
          isMock
            ? 'bg-amber-50/80 border-amber-200/90 text-amber-950'
            : 'bg-purple-50/80 border-purple-200/90 text-purple-950'
        }`}
      >
        <div className="flex items-start sm:items-center gap-2.5">
          <div
            className={`p-2 rounded-lg shrink-0 ${
              isMock ? 'bg-amber-200/80 text-amber-900' : 'bg-purple-200/80 text-purple-900'
            }`}
          >
            {isMock ? <FlaskConical className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider">
                {isMock ? 'Local Mock Mode Simulation' : 'Amazon Bedrock Multimodal AI'}
              </span>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  isMock
                    ? 'bg-amber-200 text-amber-900 border border-amber-300'
                    : 'bg-purple-200 text-purple-900 border border-purple-300'
                }`}
              >
                {isMock ? 'Zero AWS Charges' : 'Live Foundation Model'}
              </span>
            </div>
            <p className="text-[11px] opacity-80 mt-0.5 leading-normal">
              {isMock
                ? 'Generated using deterministic environmental rules & local mock taxonomy.'
                : 'Processed via Amazon Bedrock Converse multimodal vision & language model.'}
            </p>
          </div>
        </div>

        <button
          onClick={onReset}
          className="self-start sm:self-center inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-eco-700 bg-white hover:bg-eco-50 rounded-lg border border-slate-200 shadow-sm transition-colors shrink-0"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>New Inspection</span>
        </button>
      </div>

      {/* Image-in-Mock Notice if applicable */}
      {isMock && is_uncertain && item_name.toLowerCase().includes('image') && (
        <div className="p-3.5 rounded-xl bg-blue-50/80 border border-blue-200 text-blue-900 text-xs flex items-start gap-2.5">
          <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
          <div>
            <strong className="font-bold">Image Recognition in Mock Mode:</strong>
            <p className="mt-0.5 text-blue-800 leading-relaxed text-[11px]">
              Offline mock mode does not run computer vision on image pixels. To classify this item locally, enter a descriptive text label (e.g. <em>&quot;banana peel&quot;</em>) alongside your image or pick a 1-click preset. Live image recognition is enabled when connected to Amazon Bedrock.
            </p>
          </div>
        </div>
      )}

      {/* Header Bar */}
      <div className="pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs uppercase font-extrabold tracking-wider text-slate-400">
            Identified Material
          </span>
          <span className="text-slate-300">•</span>
          <span className="text-xs font-semibold text-slate-600">
            {material}
          </span>
        </div>
        <h3 className="text-xl md:text-2xl font-black text-slate-900 tracking-tight">
          {item_name}
        </h3>
      </div>

      {/* Main Category Banner */}
      <CategoryBadge category={category} isUncertain={is_uncertain} size="large" />

      {/* Confidence & Uncertainty Status */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/70">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="font-bold text-slate-700 flex items-center gap-1.5">
            Classification Confidence
            {is_uncertain && (
              <span className="font-semibold text-rose-600">
                (Safe Uncertainty Guardrail Enforced)
              </span>
            )}
          </span>
          <span className="font-extrabold text-slate-800">
            {confidencePercentage}% ({confidence_level.toUpperCase()})
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-700 ${
              confidence_level === 'high'
                ? 'bg-eco-500'
                : confidence_level === 'medium'
                ? 'bg-amber-500'
                : 'bg-rose-500'
            }`}
            style={{ width: `${confidencePercentage}%` }}
          />
        </div>
        <p className="text-xs text-slate-600 mt-2.5 leading-relaxed">
          {summary}
        </p>
        {ai_explanation && (
          <p className="text-[11px] text-slate-500 mt-1.5 pt-1.5 border-t border-slate-200/60 font-mono">
            <strong>Classifier Reasoning:</strong> {ai_explanation}
          </p>
        )}
      </div>

      {/* Critical Safety Alert Banner (if applicable) */}
      <SafetyAlert warnings={safety_warnings} />

      {/* Preparation Steps (if any) */}
      {preparation_steps && preparation_steps.length > 0 && (
        <div className="bg-eco-50/50 rounded-xl p-4 border border-eco-200/60">
          <h4 className="text-xs font-bold text-eco-900 tracking-tight uppercase flex items-center gap-1.5 mb-2.5">
            <ShieldCheck className="w-4 h-4 text-eco-700" />
            Preparation Steps Before Disposal
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {preparation_steps.map((prep, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-xs font-medium text-eco-800 bg-white/80 p-2 rounded-lg border border-eco-100"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-eco-500 shrink-0" />
                <span>{prep}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step-by-Step Disposal Instructions */}
      <div>
        <h4 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2 mb-3">
          <CheckCircle2 className="w-4 h-4 text-eco-600" />
          Disposal Action Protocol
        </h4>
        <div className="space-y-2">
          {disposal_instructions.map((step, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 bg-white hover:border-eco-300 transition-colors"
            >
              <div className="w-6 h-6 rounded-full bg-slate-100 text-slate-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                {idx + 1}
              </div>
              <p className="text-xs md:text-sm font-medium text-slate-800 leading-normal">
                {step}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Alternative Options (Bottle deposits, community drop-off) */}
      {alternative_options && alternative_options.length > 0 && (
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70">
          <h5 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <ExternalLink className="w-3.5 h-3.5 text-slate-500" />
            Alternative Recovery & Reuse Pathways
          </h5>
          <ul className="space-y-1">
            {alternative_options.map((alt, idx) => (
              <li key={idx} className="text-xs text-slate-600 flex items-start gap-1.5">
                <span className="text-eco-600 font-bold">•</span>
                <span>{alt}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Environmental Impact Note */}
      {environmental_impact && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-eco-50 to-emerald-50 border border-eco-200/80 flex items-start gap-3">
          <div className="p-2 rounded-lg bg-eco-600 text-white shrink-0">
            <Leaf className="w-4 h-4" />
          </div>
          <div>
            <h5 className="text-xs font-bold text-eco-900 uppercase tracking-wider">
              Ecological Impact
            </h5>
            <p className="text-xs text-eco-800 mt-1 leading-relaxed">
              {environmental_impact}
            </p>
          </div>
        </div>
      )}

      {/* Rules Applied Audit Trail */}
      <details className="group border border-slate-200 rounded-xl overflow-hidden bg-slate-50/50">
        <summary className="p-3 text-xs font-semibold text-slate-600 cursor-pointer select-none flex items-center justify-between hover:bg-slate-100 transition-colors">
          <span className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-slate-500" />
            Deterministic Rules Engine Audit Trail ({rules_applied.length} rules checked)
          </span>
          <span className="text-[11px] text-slate-400 group-open:rotate-90 transition-transform">
            ▶
          </span>
        </summary>
        <div className="p-3 pt-0 border-t border-slate-200 bg-white space-y-1 text-xs text-slate-600 font-mono">
          {rules_applied.map((rule, idx) => (
            <div key={idx} className="p-1.5 rounded bg-slate-50 border border-slate-100 text-[11px]">
              {rule}
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}
