import React, { useState, useRef } from 'react';
import { Camera, Upload, X, Sparkles, AlertCircle, FileText, CheckCircle2, FlaskConical, Zap, Info } from 'lucide-react';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

export default function WasteInputForm({
  onSubmit,
  isLoading,
  forceMock,
  setForceMock,
  validationError,
  setValidationError,
}) {
  const [text, setText] = useState('');
  const [imagePreview, setImagePreview] = useState(null);
  const [imageBase64, setImageBase64] = useState(null);
  const [fileName, setFileName] = useState('');
  const [fileSizeKb, setFileSizeKb] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleTextChange = (e) => {
    setText(e.target.value);
    if (validationError) setValidationError(null);
  };

  const processFile = (file) => {
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setValidationError('Please select a valid image file (JPEG, PNG, WEBP).');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setValidationError('Selected image exceeds 5 MB. Please select a smaller photo.');
      return;
    }

    setValidationError(null);
    setFileName(file.name);
    setFileSizeKb(Math.round(file.size / 1024));

    const reader = new FileReader();
    reader.onload = () => {
      setImagePreview(reader.result);
      setImageBase64(reader.result);
    };
    reader.onerror = () => {
      setValidationError('Failed to read image file. Please try another image.');
    };
    reader.readAsDataURL(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    processFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    processFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const clearImage = () => {
    setImagePreview(null);
    setImageBase64(null);
    setFileName('');
    setFileSizeKb(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const clearAll = () => {
    setText('');
    clearImage();
    setValidationError(null);
  };

  // Helper to prefill description from filename in mock mode if user desires
  const autoFillFromName = () => {
    if (!fileName) return;
    const cleanName = fileName.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
    setText(cleanName);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const cleanText = text.trim();
    if (!cleanText && !imageBase64) {
      setValidationError('Please enter a waste description or upload a photo to analyze.');
      return;
    }

    setValidationError(null);
    onSubmit({
      text: cleanText,
      image: imageBase64,
      forceMock,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-slate-200/80 p-5 md:p-6 transition-all">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 mb-4 border-b border-slate-100">
        <div>
          <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
            <Camera className="w-5 h-5 text-eco-600" />
            Waste Inspection Input
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Describe the item, paste text, or drag & drop a waste photograph for AI classification.
          </p>
        </div>

        {/* Mock Mode vs Bedrock Toggle (Requirement 7) */}
        <div className="flex items-center gap-2 self-start sm:self-center bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200/90 shadow-sm">
          <label htmlFor="mock-toggle" className="text-xs font-bold cursor-pointer select-none flex items-center gap-1.5">
            {forceMock ? (
              <span className="flex items-center gap-1 text-amber-800">
                <FlaskConical className="w-3.5 h-3.5 text-amber-600" />
                Mock Mode (Offline)
              </span>
            ) : (
              <span className="flex items-center gap-1 text-purple-800">
                <Zap className="w-3.5 h-3.5 text-purple-600" />
                Amazon Bedrock (Live AWS)
              </span>
            )}
          </label>
          <input
            id="mock-toggle"
            type="checkbox"
            checked={forceMock}
            onChange={(e) => setForceMock(e.target.checked)}
            className="w-4 h-4 text-eco-600 rounded border-slate-300 focus:ring-eco-500 cursor-pointer accent-eco-600 ml-1"
          />
        </div>
      </div>

      {validationError && (
        <div className="mb-4 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium flex items-center gap-2 animate-shake">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Text Input Area */}
      <div className="mb-4">
        <label htmlFor="waste-description" className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center justify-between">
          <span>Waste Item Description</span>
          <span className="text-[11px] font-normal text-slate-400">
            {text.length} characters
          </span>
        </label>
        <div className="relative">
          <textarea
            id="waste-description"
            rows={3}
            value={text}
            onChange={handleTextChange}
            placeholder="e.g. Greasy pepperoni pizza box, rechargeable lithium smartphone battery, clean aluminum soda can, empty bleach bottle..."
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:border-eco-500 focus:ring-2 focus:ring-eco-100 text-sm text-slate-800 placeholder-slate-400 transition-all resize-none shadow-inner"
          />
          {text && (
            <button
              type="button"
              onClick={() => setText('')}
              className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 p-1"
              title="Clear text"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Image Upload Area */}
      <div className="mb-5">
        <label className="block text-xs font-semibold text-slate-700 mb-1.5">
          Waste Photo Upload (Optional)
        </label>

        {imagePreview ? (
          <div className="rounded-xl border border-slate-200 overflow-hidden bg-slate-50 p-3 space-y-2.5">
            <div className="flex items-center gap-4">
              <div className="relative w-20 h-20 rounded-lg overflow-hidden border border-slate-200 bg-white shrink-0">
                <img
                  src={imagePreview}
                  alt="Waste preview"
                  className="w-full h-full object-cover"
                />
                {isLoading && (
                  <div className="absolute inset-0 bg-eco-900/40 backdrop-blur-[1px] flex items-center justify-center">
                    <div className="w-full h-1 bg-eco-400 absolute animate-scan shadow-lg"></div>
                  </div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                  <CheckCircle2 className="w-4 h-4 text-eco-600" />
                  <span className="truncate">{fileName || 'Attached Image'}</span>
                  {fileSizeKb > 0 && (
                    <span className="text-[10px] text-slate-400 font-normal">({fileSizeKb} KB)</span>
                  )}
                </div>

                <div className="mt-1">
                  {forceMock ? (
                    <p className="text-[11px] text-amber-800 font-medium">
                      🧪 In Mock Mode: Image pixels cannot be inspected locally. Real vision requires Amazon Bedrock.
                    </p>
                  ) : (
                    <p className="text-[11px] text-purple-700 font-medium">
                      ⚡ Amazon Bedrock AI: Multimodal model will inspect visual textures & materials.
                    </p>
                  )}
                </div>

                <div className="mt-2 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={clearImage}
                    disabled={isLoading}
                    className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-lg border border-rose-200 transition-colors"
                  >
                    <X className="w-3.5 h-3.5" />
                    Remove
                  </button>

                  {forceMock && !text && fileName && (
                    <button
                      type="button"
                      onClick={autoFillFromName}
                      className="text-[11px] text-eco-700 hover:text-eco-900 font-semibold underline underline-offset-2"
                    >
                      Use &quot;{fileName.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ')}&quot; as description
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Explanatory Mock Guidance Box if in mock mode without text */}
            {forceMock && !text && (
              <div className="p-2 rounded-lg bg-amber-50/80 border border-amber-200/70 text-[11px] text-amber-800 flex items-start gap-1.5">
                <Info className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                <span>
                  Tip: In offline mock mode, add a brief text description above (e.g. <em>&quot;banana peel&quot;</em>) to test rule classification with this photo, or submit directly to test safe uncertainty handling.
                </span>
              </div>
            )}
          </div>
        ) : (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-eco-500 bg-eco-50/60 scale-[1.01]'
                : 'border-slate-300 hover:border-eco-400 hover:bg-slate-50/60'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center gap-2">
              <div className="p-2.5 rounded-full bg-slate-100 text-slate-600 group-hover:bg-eco-100 group-hover:text-eco-600 transition-colors">
                <Upload className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-700">
                  Click to browse or drag and drop waste photo
                </p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  JPEG, PNG, or WEBP up to 5 MB
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between gap-3 pt-2">
        <button
          type="button"
          onClick={clearAll}
          disabled={isLoading || (!text && !imagePreview)}
          className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Reset Form
        </button>

        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-bold text-xs text-white bg-eco-600 hover:bg-eco-700 active:scale-[0.98] shadow-sm shadow-eco-600/30 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:scale-100"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Analyzing Waste...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Segregate Waste</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
