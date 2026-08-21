import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { StoryPlayer } from '../components/StoryPlayer';
import { StoryMapExplorer } from '../components/StoryMapExplorer';
import { AskTheStory } from '../components/AskTheStory';
import { storiesApi, userApi } from '../services/api';
import {
  Story,
  StoryGraphEntity,
  StoryGraphData,
  NarrativeEntity,
  NarrativeData,
  LocalizationEntity,
  LocalizedScriptData,
  AudioEntity,
  AudioAssetData,
} from '../types';
import {
  Sparkles,
  Clock,
  Globe,
  ShieldCheck,
  Headphones,
  GitBranch,
  MessageSquare,
  Bookmark,
  ChevronLeft,
} from 'lucide-react';

export const StoryDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const storyId = id || '';

  const [story, setStory] = useState<Story | null>(null);
  const [graphEntity, setGraphEntity] = useState<StoryGraphEntity | null>(null);
  const [narratives, setNarratives] = useState<NarrativeEntity[]>([]);
  const [localizations, setLocalizations] = useState<LocalizationEntity[]>([]);
  const [audioAssets, setAudioAssets] = useState<AudioEntity[]>([]);
  const [loading, setLoading] = useState(true);

  // User selections
  const [durationPreset, setDurationPreset] = useState<'quick' | 'standard' | 'complete'>('standard');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('hi'); // Default to Hindi
  const [activeTab, setActiveTab] = useState<'player' | 'map' | 'ask'>('player');

  useEffect(() => {
    const loadStoryData = async () => {
      setLoading(true);
      try {
        const [sRes, gRes, nRes, lRes, aRes] = await Promise.allSettled([
          storiesApi.getById(storyId),
          storiesApi.getGraph(storyId),
          storiesApi.getNarratives(storyId),
          storiesApi.getLocalizations(storyId),
          storiesApi.getAudioAssets(storyId),
        ]);

        if (sRes.status === 'fulfilled') setStory(sRes.value.data);
        if (gRes.status === 'fulfilled') setGraphEntity(gRes.value.data);
        if (nRes.status === 'fulfilled') setNarratives(nRes.value.data);
        if (lRes.status === 'fulfilled') setLocalizations(lRes.value.data);
        if (aRes.status === 'fulfilled') setAudioAssets(aRes.value.data);
      } catch (e) {
        console.error('Failed to load story details', e);
      } finally {
        setLoading(false);
      }
    };

    if (storyId) {
      loadStoryData();
    }
  }, [storyId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">
          <div className="flex items-center gap-3 text-brand-400">
            <Sparkles className="w-6 h-6 animate-spin" />
            <span className="text-sm font-semibold">Loading StoryBridge Narrative...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!story) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          <h2 className="text-xl font-bold text-white mb-2">Story not found</h2>
          <Link to="/" className="text-xs text-brand-400 hover:underline">
            Return to Explore
          </Link>
        </div>
      </div>
    );
  }

  // Parse JSON data objects
  let parsedGraph: StoryGraphData | undefined;
  if (graphEntity?.graphDataJson) {
    try {
      parsedGraph = JSON.parse(graphEntity.graphDataJson);
    } catch (e) {}
  }

  // Active localized script with fallback
  const activeLocEntity =
    localizations.find(
      (l) => l.durationPreset.toLowerCase() === durationPreset && l.languageCode.toLowerCase() === selectedLanguage
    ) ||
    localizations.find(
      (l) => l.languageCode.toLowerCase() === selectedLanguage
    ) ||
    localizations[0];

  let parsedScript: LocalizedScriptData | undefined;
  if (activeLocEntity?.scriptJson) {
    try {
      parsedScript = JSON.parse(activeLocEntity.scriptJson);
    } catch (e) {}
  }

  // Active audio asset
  const activeAudioEntity =
    audioAssets.find(
      (a) => a.durationPreset.toLowerCase() === durationPreset && a.languageCode.toLowerCase() === selectedLanguage
    ) ||
    audioAssets.find(
      (a) => a.languageCode.toLowerCase() === selectedLanguage
    );

  let parsedAudioChapters: any[] = [];
  if (activeAudioEntity?.chaptersJson) {
    try {
      const parsed = JSON.parse(activeAudioEntity.chaptersJson);
      parsedAudioChapters = parsed.chapters || parsed;
    } catch (e) {}
  }

  // Fallback English narrative chapters if localized script is missing
  const activeNarrative =
    narratives.find((n) => n.durationPreset.toLowerCase() === durationPreset) ||
    narratives[0];

  let parsedNarrative: NarrativeData | undefined;
  if (activeNarrative?.narrativeJson) {
    try {
      parsedNarrative = JSON.parse(activeNarrative.narrativeJson);
    } catch (e) {}
  }

  const chaptersToDisplay = parsedScript?.chapters || parsedNarrative?.chapters || [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 w-full">
        {/* Back Link */}
        <Link
          to="/"
          className="inline-flex items-center gap-1 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Back to Stories</span>
        </Link>

        {/* Story Title & Meta Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-slate-800">
          <div className="space-y-2 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-brand-500/20 text-brand-300">
                {story.category}
              </span>
              <span className="flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300">
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                {story.rightsType === 'PUBLIC_DOMAIN' ? 'Public Domain' : 'Open License'}
              </span>
            </div>

            <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              {parsedScript?.title || story.title}
            </h1>

            {story.originalAuthor && (
              <p className="text-xs sm:text-sm text-slate-400">
                Original work by <span className="text-slate-200 font-medium">{story.originalAuthor}</span>
              </p>
            )}

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed pt-1">
              {parsedScript?.synopsis || story.description}
            </p>
          </div>

          {/* Preset & Language Selector Toolbar */}
          <div className="flex flex-col gap-3 p-4 bg-slate-900 border border-slate-800 rounded-2xl shrink-0">
            {/* Duration Selector */}
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5 flex items-center gap-1">
                <Clock className="w-3 h-3 text-brand-400" />
                <span>Select Duration</span>
              </span>
              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
                {[
                  { id: 'quick', label: 'Quick (5m)' },
                  { id: 'standard', label: 'Standard (15m)' },
                  { id: 'complete', label: 'Complete (45m)' },
                ].map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setDurationPreset(p.id as any)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      durationPreset === p.id
                        ? 'bg-brand-600 text-white shadow-md shadow-brand-600/20'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Language Selector */}
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5 flex items-center gap-1">
                <Globe className="w-3 h-3 text-indigo-400" />
                <span>Select Language</span>
              </span>
              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
                {[
                  { id: 'hi', label: 'हिंदी (Hindi)' },
                  { id: 'mr', label: 'मराठी (Marathi)' },
                  { id: 'en', label: 'English' },
                ].map((l) => (
                  <button
                    key={l.id}
                    onClick={() => setSelectedLanguage(l.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      selectedLanguage === l.id
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* View Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
          <button
            onClick={() => setActiveTab('player')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-colors ${
              activeTab === 'player'
                ? 'bg-brand-600 text-white'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900'
            }`}
          >
            <Headphones className="w-4 h-4" />
            <span>Narration & Audio Player</span>
          </button>

          <button
            onClick={() => setActiveTab('map')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-colors ${
              activeTab === 'map'
                ? 'bg-brand-600 text-white'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900'
            }`}
          >
            <GitBranch className="w-4 h-4" />
            <span>Story Map & Characters</span>
          </button>

          <button
            onClick={() => setActiveTab('ask')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-colors ${
              activeTab === 'ask'
                ? 'bg-brand-600 text-white'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Ask the Story (Q&A)</span>
          </button>
        </div>

        {/* Active Tab View */}
        {activeTab === 'player' && (
          <StoryPlayer
            storyId={story.id}
            storyTitle={parsedScript?.title || story.title}
            durationPreset={durationPreset}
            language={selectedLanguage}
            chapters={chaptersToDisplay}
            audioChapters={parsedAudioChapters}
            onProgress={(chIdx, curTime) => {
              userApi.updateProgress({
                storyId: story.id,
                languageCode: selectedLanguage,
                durationPreset,
                chapterIndex: chIdx,
                progressSeconds: curTime,
                completed: false,
              }).catch(() => {});
            }}
          />
        )}

        {activeTab === 'map' && parsedGraph && (
          <StoryMapExplorer graphData={parsedGraph} />
        )}

        {activeTab === 'ask' && (
          <AskTheStory storyTitle={story.title} graphData={parsedGraph} />
        )}
      </main>
    </div>
  );
};
