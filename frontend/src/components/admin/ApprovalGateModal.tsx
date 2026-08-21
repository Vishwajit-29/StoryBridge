import React, { useState, useEffect } from 'react';
import { ShieldCheck, CheckCircle2, XCircle, RefreshCw, Sparkles, BookOpen, Globe, FileText } from 'lucide-react';
import { adminApi, storiesApi } from '../../services/api';
import { Story, StoryGraphEntity, NarrativeEntity, LocalizationEntity, AudioEntity } from '../../types';

interface ApprovalGateModalProps {
  story: Story;
  isOpen: boolean;
  onClose: () => void;
  onStoryUpdated: (story: Story) => void;
}

export const ApprovalGateModal: React.FC<ApprovalGateModalProps> = ({
  story,
  isOpen,
  onClose,
  onStoryUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<'rights' | 'graph' | 'narrative' | 'localization' | 'audio'>('rights');
  const [graphEntity, setGraphEntity] = useState<StoryGraphEntity | null>(null);
  const [narratives, setNarratives] = useState<NarrativeEntity[]>([]);
  const [localizations, setLocalizations] = useState<LocalizationEntity[]>([]);
  const [audioAssets, setAudioAssets] = useState<AudioEntity[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [message, setMessage] = useState('');

  const loadStoryArtifacts = async () => {
    setLoading(true);
    try {
      const [gRes, nRes, lRes, aRes] = await Promise.allSettled([
        storiesApi.getGraph(story.id),
        storiesApi.getNarratives(story.id),
        storiesApi.getLocalizations(story.id),
        storiesApi.getAudioAssets(story.id),
      ]);

      if (gRes.status === 'fulfilled') setGraphEntity(gRes.value.data);
      if (nRes.status === 'fulfilled') setNarratives(nRes.value.data);
      if (lRes.status === 'fulfilled') setLocalizations(lRes.value.data);
      if (aRes.status === 'fulfilled') setAudioAssets(aRes.value.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadStoryArtifacts();
    }
  }, [isOpen, story.id]);

  if (!isOpen) return null;

  const handleSyncArtifacts = async () => {
    setSyncing(true);
    setMessage('');
    try {
      const res = await adminApi.syncArtifacts(story.id);
      setMessage(`Successfully synced ${res.data.artifactsCount} artifacts from storage into database.`);
      await loadStoryArtifacts();
    } catch (e: any) {
      setMessage(`Sync failed: ${e.response?.data?.error || e.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const handlePublish = async () => {
    try {
      const res = await adminApi.publishStory(story.id);
      onStoryUpdated(res.data);
      setMessage('Story published successfully!');
    } catch (e: any) {
      alert(e.response?.data?.message || 'Publishing failed. Check rights verification.');
    }
  };

  const handleUnpublish = async () => {
    try {
      const res = await adminApi.unpublishStory(story.id);
      onStoryUpdated(res.data);
      setMessage('Story unpublished.');
    } catch (e: any) {
      alert(e.response?.data?.message || 'Unpublishing failed.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-4xl p-6 sm:p-8 shadow-2xl relative my-8">
        <button onClick={onClose} className="absolute top-5 right-5 text-slate-400 hover:text-white">
          ✕
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300">
                Review Gate
              </span>
              <h3 className="text-xl font-bold text-white">{story.title}</h3>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">Story ID: {story.id} · Status: {story.status}</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleSyncArtifacts}
              disabled={syncing}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 rounded-xl transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
              <span>Sync Storage Artifacts</span>
            </button>

            {story.status === 'PUBLISHED' ? (
              <button
                onClick={handleUnpublish}
                className="px-4 py-1.5 bg-rose-600/20 border border-rose-500/40 hover:bg-rose-600/30 text-rose-300 text-xs font-bold rounded-xl transition-colors"
              >
                Unpublish
              </button>
            ) : (
              <button
                onClick={handlePublish}
                className="flex items-center gap-1.5 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-600/20 transition-all"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Approve & Publish</span>
              </button>
            )}
          </div>
        </div>

        {message && (
          <div className="mt-4 p-3 bg-brand-500/10 border border-brand-500/30 rounded-xl text-xs text-brand-300">
            {message}
          </div>
        )}

        {/* Tab Switcher */}
        <div className="flex items-center gap-2 mt-5 border-b border-slate-800 pb-3 overflow-x-auto">
          {[
            { id: 'rights', label: '1. Rights & Legality', icon: ShieldCheck },
            { id: 'graph', label: '2. Story Graph', icon: Sparkles },
            { id: 'narrative', label: '3. Canonical Narratives', icon: BookOpen },
            { id: 'localization', label: '4. Regional Scripts', icon: Globe },
            { id: 'audio', label: '5. Audio Assets', icon: FileText },
          ].map((t) => {
            const Icon = t.icon;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id as any)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors ${
                  activeTab === t.id
                    ? 'bg-brand-600 text-white'
                    : 'bg-slate-950 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Bodies */}
        <div className="py-5 max-h-[440px] overflow-y-auto">
          {activeTab === 'rights' && (
            <div className="space-y-4 bg-slate-950/60 p-5 rounded-2xl border border-slate-800 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-300">Rights Category:</span>
                <span className="font-mono px-2 py-0.5 bg-brand-950 text-brand-300 border border-brand-800 rounded">
                  {story.rightsType}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-300">Verification Status:</span>
                <span className={`font-semibold ${story.rightsVerified ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {story.rightsVerified ? 'Verified & Documented' : 'Unverified (Cannot Publish)'}
                </span>
              </div>
              <div>
                <span className="font-semibold text-slate-300 block mb-1">Evidence / Attribution Note:</span>
                <p className="p-3 bg-slate-900 rounded-xl text-slate-400 font-mono">
                  {story.rightsEvidence || 'No evidence note provided.'}
                </p>
              </div>
            </div>
          )}

          {activeTab === 'graph' && (
            <div className="space-y-3">
              {graphEntity ? (
                <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 text-xs space-y-2">
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Story Graph Version: {graphEntity.version}</span>
                    <span className="text-emerald-400">Approved</span>
                  </div>
                  <pre className="p-3 bg-slate-900 rounded-xl text-[11px] font-mono text-slate-300 overflow-x-auto max-h-80">
                    {JSON.stringify(JSON.parse(graphEntity.graphDataJson || '{}'), null, 2)}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-10 text-slate-500 text-xs">
                  No Story Graph artifact registered yet. Run the pipeline or click "Sync Storage Artifacts".
                </div>
              )}
            </div>
          )}

          {activeTab === 'narrative' && (
            <div className="space-y-4">
              {narratives.length > 0 ? (
                narratives.map((n) => (
                  <div key={n.id} className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-brand-300 uppercase">{n.durationPreset} Story Blueprint</span>
                      <span className="text-slate-400">{n.wordCount} words · ~{n.targetDurationMinutes} min</span>
                    </div>
                    <pre className="p-3 bg-slate-900 rounded-xl text-[11px] font-mono text-slate-300 overflow-x-auto max-h-60">
                      {JSON.stringify(JSON.parse(n.narrativeJson || '{}'), null, 2)}
                    </pre>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-slate-500 text-xs">
                  No Narrative artifacts registered yet.
                </div>
              )}
            </div>
          )}

          {activeTab === 'localization' && (
            <div className="space-y-4">
              {localizations.length > 0 ? (
                localizations.map((loc) => (
                  <div key={loc.id} className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-indigo-300 uppercase">{loc.languageName} ({loc.languageCode}) - {loc.durationPreset}</span>
                      <span className="text-emerald-400">QA Passed</span>
                    </div>
                    <pre className="p-3 bg-slate-900 rounded-xl text-[11px] font-mono text-slate-300 overflow-x-auto max-h-60">
                      {JSON.stringify(JSON.parse(loc.scriptJson || '{}'), null, 2)}
                    </pre>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-slate-500 text-xs">
                  No Localized scripts registered yet.
                </div>
              )}
            </div>
          )}

          {activeTab === 'audio' && (
            <div className="space-y-4">
              {audioAssets.length > 0 ? (
                audioAssets.map((a) => (
                  <div key={a.id} className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white uppercase">{a.languageCode.toUpperCase()} · {a.durationPreset} Audio</span>
                      <span className="text-slate-400">Total Duration: {a.totalDurationSeconds.toFixed(1)}s</span>
                    </div>
                    <pre className="p-3 bg-slate-900 rounded-xl text-[11px] font-mono text-slate-300 overflow-x-auto max-h-40">
                      {JSON.stringify(JSON.parse(a.chaptersJson || '[]'), null, 2)}
                    </pre>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-slate-500 text-xs">
                  No Audio assets registered yet.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
