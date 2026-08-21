import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { StoryCard } from '../components/StoryCard';
import { userApi } from '../services/api';
import { Story } from '../types';
import { BookOpen, Clock, Bookmark, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const MyLibraryPage: React.FC = () => {
  const [bookmarks, setBookmarks] = useState<Story[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUserData = async () => {
      setLoading(true);
      try {
        const [bRes, hRes] = await Promise.allSettled([
          userApi.getBookmarks(),
          userApi.getHistory(),
        ]);
        if (bRes.status === 'fulfilled') setBookmarks(bRes.value.data);
        if (hRes.status === 'fulfilled') setHistory(hRes.value.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadUserData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10 w-full">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-brand-400" />
            <span>My Library</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">Your saved bookmarks and listening journey.</p>
        </div>

        {/* Bookmarks Section */}
        <div>
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-amber-400" />
            <span>Bookmarked Stories ({bookmarks.length})</span>
          </h2>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
              {[1, 2].map((i) => (
                <div key={i} className="h-56 bg-slate-900 rounded-2xl border border-slate-800"></div>
              ))}
            </div>
          ) : bookmarks.length === 0 ? (
            <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-xs text-slate-400">
              You haven't bookmarked any stories yet. Explore the catalog and click the bookmark icon on any story!
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {bookmarks.map((s) => (
                <StoryCard key={s.id} story={s} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
