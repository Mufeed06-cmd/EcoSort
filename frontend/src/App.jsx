import React, { useState } from 'react';
import Header from './components/Header';
import WasteInputForm from './components/WasteInputForm';
import AnalysisResult from './components/AnalysisResult';
import QuickPresets from './components/QuickPresets';
import CategoryGuideModal from './components/CategoryGuideModal';
import EnvironmentalStats from './components/EnvironmentalStats';
import { analyzeWaste } from './services/api';
import { AlertTriangle, RefreshCw, Sparkles, Shield, Cpu } from 'lucide-react';

export default function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [validationError, setValidationError] = useState(null);
  const [forceMock, setForceMock] = useState(true); // Default to mock mode for easy local demo
  const [isGuideOpen, setIsGuideOpen] = useState(false);

  // Stats accumulator for hackathon gamification
  const [stats, setStats] = useState({
    analyzed: 4,
    hazardousSafeguarded: 2,
    contaminationPrevented: 3,
    batteryFiresPrevented: 1,
  });

  const handleAnalyze = async ({ text, image, forceMock: mockChoice }) => {
    setIsLoading(true);
    setApiError(null);
    setValidationError(null);

    try {
      const data = await analyzeWaste({
        text,
        image,
        forceMock: mockChoice,
      });

      setResult(data);

      // Update session statistics
      setStats((prev) => {
        const isHazard = data.category === 'hazardous';
        const isSoiled = data.summary?.toLowerCase().includes('greas') || data.rules_applied?.some((r) => r.includes('Contamination'));
        const isBattery = data.item_name?.toLowerCase().includes('battery');

        return {
          analyzed: prev.analyzed + 1,
          hazardousSafeguarded: isHazard ? prev.hazardousSafeguarded + 1 : prev.hazardousSafeguarded,
          contaminationPrevented: isSoiled ? prev.contaminationPrevented + 1 : prev.contaminationPrevented,
          batteryFiresPrevented: isBattery ? prev.batteryFiresPrevented + 1 : prev.batteryFiresPrevented,
        };
      });

      // Smooth scroll to result
      window.scrollTo({ top: 300, behavior: 'smooth' });
    } catch (err) {
      console.error('Analysis error:', err);
      setApiError({
        message: err.message || 'An unexpected error occurred while communicating with the waste analyzer.',
        isConnectionError: Boolean(err.isConnectionError),
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPreset = (preset) => {
    handleAnalyze({
      text: preset.description,
      image: null,
      forceMock,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-eco-50/20 to-slate-100 flex flex-col font-sans">
      <Header onOpenGuide={() => setIsGuideOpen(true)} forceMock={forceMock} />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
        {/* Hero Section */}
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-eco-100/90 text-eco-800 border border-eco-200 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-eco-600" />
            <span>Zero-Contamination AI Waste Segregation</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Sort Waste Safely. Protect the Planet.
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            Multimodal AI classification powered by Amazon Bedrock with a deterministic Python rules engine.
            Never compromises on hazardous safety or invents fake recycling certainty.
          </p>
        </div>

        {/* Live Environmental Session Stats */}
        <EnvironmentalStats stats={stats} />

        {/* API Error Alert */}
        {apiError && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm shadow-sm animate-fade-in flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <strong className="font-bold block text-rose-900">Communication Error</strong>
                <p className="text-xs text-rose-700 mt-0.5">{apiError.message}</p>
                {apiError.isConnectionError && (
                  <p className="text-[11px] text-rose-600 mt-1">
                    Tip: If running locally without backend, you can start the backend with{' '}
                    <code className="bg-rose-100/80 px-1 py-0.5 rounded font-mono">python3 -m backend.local_server</code>.
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={() => setApiError(null)}
              className="self-end sm:self-center px-3 py-1.5 text-xs font-bold text-rose-700 hover:bg-rose-100 rounded-lg transition-colors border border-rose-300"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Quick Demo Presets */}
        <QuickPresets onSelectPreset={handleSelectPreset} disabled={isLoading} />

        {/* Main Input Form */}
        <WasteInputForm
          onSubmit={handleAnalyze}
          isLoading={isLoading}
          forceMock={forceMock}
          setForceMock={setForceMock}
          validationError={validationError}
          setValidationError={setValidationError}
        />

        {/* Loading Spinner / Scanner UI */}
        {isLoading && (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center space-y-4 animate-pulse">
            <div className="w-12 h-12 mx-auto rounded-full bg-eco-100 text-eco-600 flex items-center justify-center animate-spin">
              <RefreshCw className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-800">
                Analyzing Waste Composition & Hazards...
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                Executing computer vision inference and evaluating environmental safety rules.
              </p>
            </div>
          </div>
        )}

        {/* Analysis Output Section */}
        {result && !isLoading && (
          <AnalysisResult result={result} onReset={() => setResult(null)} />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-6 border-t border-slate-200/80 bg-white/50 text-center text-xs text-slate-500">
        <div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© 2026 EcoSort AI — Environmental Hacks Hackathon MVP.</p>
          <p className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-eco-600" />
            <span>Deterministic Safety Overrides • Amazon Bedrock • AWS Lambda</span>
          </p>
        </div>
      </footer>

      {/* Segregation Guide Modal */}
      <CategoryGuideModal
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
      />
    </div>
  );
}
