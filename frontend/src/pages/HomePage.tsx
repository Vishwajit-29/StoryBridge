import React, { useState, useEffect } from 'react';
import { storiesApi } from '../services/api';
import { Story } from '../types';
import { Navbar } from '../components/Navbar';
import { DurationSlider } from '../components/DurationSlider';
import { StoryCard } from '../components/StoryCard';
import { Sparkles, Compass, BookOpen, Layers, ShieldCheck } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

export const HomePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';

  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPreset, setSelectedPreset] = useState<'all' | 'quick' | 'standard' | 'complete'>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState(queryParam);

  const categories = [
    'All',
    'Mythology & Folklore',
    'Fables & Moral Tales',
    'Classic Literature',
    'Historical Epics',
    'Sci-Fi & Fantasy',
  ];

  const fetchStories = async () => {
    setLoading(true);
    try {
      if (searchQuery.trim()) {
        const res = await storiesApi.search(searchQuery);
        setStories(res.data);
      } else {
        const cat = selectedCategory === 'All' ? undefined : selectedCategory;
        const res = await storiesApi.getPublished(cat);
        setStories(res.data);
      }
    } catch (e) {
      console.error('Failed to load stories', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStories();
  }, [selectedCategory, searchQuery]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar onSearch={(q) => setSearchQuery(q)} />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10 w-full">
        {/* Hero Section */}
        <div className="relative rounded-3xl bg-gradient-to-br from-brand-950/70 via-slate-900 to-slate-950 border border-brand-800/30 p-8 sm:p-12 overflow-hidden shadow-2xl">
          <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-brand-500/10 rounded-full blur-3xl pointer-events-none"></div>

          <div className="relative z-10 max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Story Understanding & Narrative Compression</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
              Every story. <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-400 via-indigo-300 to-purple-400">
                Your language. Your time.
              </span>
            </h1>

            <p className="text-sm sm:text-base text-slate-300 max-w-2xl leading-relaxed">
              StoryBridge converts long epics, classics, and folk narratives into structured semantic story graphs, compresses them into your desired duration, and narrates them in native Indian regional languages with zero semantic drift.
            </p>
          </div>
        </div>

        {/* Duration discovery filter slider */}
        <DurationSlider
          selectedPreset={selectedPreset}
          onChange={(p) => setSelectedPreset(p)}
        />

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => {
                setSelectedCategory(cat);
                setSearchQuery('');
              }}
              className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat && !searchQuery
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-600/20'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Story Grid */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Compass className="w-5 h-5 text-brand-400" />
              <span>
                {searchQuery ? `Search Results for "${searchQuery}"` : `${selectedCategory} Stories`}
              </span>
            </h2>
            <span className="text-xs text-slate-400">{stories.length} stories available</span>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-64 bg-slate-900 rounded-2xl border border-slate-800"></div>
              ))}
            </div>
          ) : stories.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/40 rounded-3xl border border-slate-800">
              <BookOpen className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <h4 className="text-base font-bold text-slate-300">No stories found</h4>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Check back soon or open the Admin CMS to ingest new public domain stories into the pipeline.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {stories.map((story) => (
                <StoryCard key={story.id} story={story} />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-8 text-center text-xs text-slate-500 mt-auto">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span className="font-semibold text-slate-300">StoryBridge v2.0</span>
            <span>— AI-Powered Multilingual Storytelling Platform</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>Public Domain & Open License Content</span>
            <span>·</span>
            <span>NVIDIA NIM Engine</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
