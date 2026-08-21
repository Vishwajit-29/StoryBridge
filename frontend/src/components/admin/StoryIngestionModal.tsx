import React, { useState } from 'react';
import { Upload, FileText, ShieldCheck, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';
import { adminApi } from '../../services/api';
import { Story } from '../../types';

interface StoryIngestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStoryCreated: (story: Story) => void;
}

export const StoryIngestionModal: React.FC<StoryIngestionModalProps> = ({
  isOpen,
  onClose,
  onStoryCreated,
}) => {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [category, setCategory] = useState('Mythology & Folklore');
  const [description, setDescription] = useState('');
  const [rightsType, setRightsType] = useState('PUBLIC_DOMAIN');
  const [rightsEvidence, setRightsEvidence] = useState('Public Domain classic literature (CC0 equivalent)');
  const [rightsVerified, setRightsVerified] = useState(true);
  const [sourceText, setSourceText] = useState('');
  const [selectedPresets, setSelectedPresets] = useState<string[]>(['quick', 'standard']);
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>(['hi', 'mr']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handlePresetToggle = (p: string) => {
    if (selectedPresets.includes(p)) {
      setSelectedPresets(selectedPresets.filter((x) => x !== p));
    } else {
      setSelectedPresets([...selectedPresets, p]);
    }
  };

  const handleLangToggle = (lang: string) => {
    if (selectedLanguages.includes(lang)) {
      setSelectedLanguages(selectedLanguages.filter((x) => x !== lang));
    } else {
      setSelectedLanguages([...selectedLanguages, lang]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceText.trim()) {
      setError('Please provide the story text or upload a source document.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // 1. Create Story record
      const storyRes = await adminApi.createStory({
        title,
        originalAuthor: author,
        category,
        description,
        rightsType: rightsType as any,
        rightsVerified,
        rightsEvidence,
      });

      const story = storyRes.data;

      // 2. Trigger pipeline
      await adminApi.triggerPipeline(story.id, {
        sourceText,
        sourceFormat: 'markdown',
        fileName: `${story.id}.md`,
        durationPresets: selectedPresets,
        languages: selectedLanguages,
      });

      onStoryCreated(story);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to ingest story');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-2xl p-6 sm:p-8 shadow-2xl relative my-8">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white"
        >
          ✕
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-brand-600/20 border border-brand-500/30 text-brand-400 flex items-center justify-center">
            <Upload className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Ingest New Story Source</h3>
            <p className="text-xs text-slate-400">
              Normalize source into Canonical Story Graph and start AI compression pipeline.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center gap-3 text-xs text-rose-300">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Story Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. The Monkey and the Wedge"
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Original Author / Tradition</label>
              <input
                type="text"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                placeholder="e.g. Vishnu Sharma (The Panchatantra)"
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500"
              >
                <option value="Mythology & Folklore">Mythology & Folklore</option>
                <option value="Fables & Moral Tales">Fables & Moral Tales</option>
                <option value="Classic Literature">Classic Literature</option>
                <option value="Historical Epics">Historical Epics</option>
                <option value="Sci-Fi & Fantasy">Sci-Fi & Fantasy</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Content Rights & Verification (SRS §28) *</span>
              </label>
              <select
                value={rightsType}
                onChange={(e) => setRightsType(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500"
              >
                <option value="PUBLIC_DOMAIN">PUBLIC_DOMAIN (Verified)</option>
                <option value="OPEN_LICENSE">OPEN_LICENSE (CC-BY / MIT)</option>
                <option value="ORIGINAL">ORIGINAL (StoryBridge Owned)</option>
                <option value="LICENSED">LICENSED (Explicit Contract)</option>
                <option value="UNKNOWN">UNKNOWN (Restricted from publish)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Rights Verification Evidence Note</label>
            <input
              type="text"
              value={rightsEvidence}
              onChange={(e) => setRightsEvidence(e.target.value)}
              placeholder="e.g. Author died >70 yrs ago / Open license documented"
              className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Source Text / Story Content (Markdown / Text) *</label>
            <textarea
              rows={6}
              required
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
              placeholder="# Chapter 1: The Beginning&#10;Paste full story text, chapters, or markdown..."
              className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs sm:text-sm font-mono text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          {/* Preset & Language Selection */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-slate-950/60 border border-slate-800 rounded-2xl">
            <div>
              <span className="block text-xs font-semibold text-slate-300 mb-2">Duration Presets</span>
              <div className="flex flex-wrap gap-2">
                {[
                  { id: 'quick', label: 'Quick (5m)' },
                  { id: 'standard', label: 'Standard (15m)' },
                  { id: 'complete', label: 'Complete (45m)' },
                ].map((p) => (
                  <button
                    type="button"
                    key={p.id}
                    onClick={() => handlePresetToggle(p.id)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors ${
                      selectedPresets.includes(p.id)
                        ? 'bg-brand-600 border-brand-500 text-white'
                        : 'bg-slate-900 border-slate-800 text-slate-400'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <span className="block text-xs font-semibold text-slate-300 mb-2">Localization Target Languages</span>
              <div className="flex flex-wrap gap-2">
                {[
                  { id: 'hi', label: 'Hindi (हिंदी)' },
                  { id: 'mr', label: 'Marathi (मराठी)' },
                  { id: 'ta', label: 'Tamil (தமிழ்)' },
                ].map((l) => (
                  <button
                    type="button"
                    key={l.id}
                    onClick={() => handleLangToggle(l.id)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors ${
                      selectedLanguages.includes(l.id)
                        ? 'bg-indigo-600 border-indigo-500 text-white'
                        : 'bg-slate-900 border-slate-800 text-slate-400'
                    }`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-lg shadow-brand-600/30 flex items-center justify-center gap-2 transition-all"
          >
            {loading ? (
              <span>Dispatching AI Pipeline...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Launch Ingestion & AI Pipeline</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
