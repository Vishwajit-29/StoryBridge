import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { adminApi } from '../services/api';
import { Story } from '../types';
import { StoryIngestionModal } from '../components/admin/StoryIngestionModal';
import { JobTrackerModal } from '../components/admin/JobTrackerModal';
import { ApprovalGateModal } from '../components/admin/ApprovalGateModal';
import {
  ShieldCheck,
  Plus,
  Activity,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Clock,
  Sparkles,
  Settings,
} from 'lucide-react';

export const AdminDashboardPage: React.FC = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [showIngestionModal, setShowIngestionModal] = useState(false);
  const [showJobTracker, setShowJobTracker] = useState(false);
  const [selectedStoryForApproval, setSelectedStoryForApproval] = useState<Story | null>(null);

  const fetchStories = async () => {
    setLoading(true);
    try {
      const res = await adminApi.getAllStories();
      setStories(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStories();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 w-full">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-amber-400" />
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
                Admin CMS & Pipeline Operations
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Manage content rights, monitor asynchronous AI workers, and approve generated stories.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowJobTracker(true)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-200 text-xs font-semibold rounded-xl shadow-sm transition-all"
            >
              <Activity className="w-4 h-4 text-brand-400" />
              <span>Pipeline Monitor</span>
            </button>

            <button
              onClick={() => setShowIngestionModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-brand-600/30 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>Ingest New Story</span>
            </button>
          </div>
        </div>

        {/* Stories Management Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <h3 className="font-bold text-white text-sm">All Platform Stories ({stories.length})</h3>
            <button
              onClick={fetchStories}
              className="text-xs text-brand-400 hover:underline"
            >
              Refresh
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Story ID & Title</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Rights Status</th>
                  <th className="py-3 px-4">Publication</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {stories.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-slate-500">
                      No stories ingested yet. Click "Ingest New Story" to start!
                    </td>
                  </tr>
                ) : (
                  stories.map((story) => (
                    <tr key={story.id} className="hover:bg-slate-950/40 transition-colors">
                      <td className="py-3 px-4">
                        <div className="font-bold text-white text-sm">{story.title}</div>
                        <div className="text-[11px] text-slate-500 font-mono">{story.id}</div>
                      </td>

                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
                          {story.category}
                        </span>
                      </td>

                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              story.rightsVerified ? 'bg-emerald-400' : 'bg-rose-400'
                            }`}
                          />
                          <span className="font-medium text-slate-200">{story.rightsType}</span>
                        </div>
                        <div className="text-[10px] text-slate-500">
                          {story.rightsVerified ? 'Verified' : 'Unverified'}
                        </div>
                      </td>

                      <td className="py-3 px-4">
                        <span
                          className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-md ${
                            story.status === 'PUBLISHED'
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : story.status === 'PROCESSING'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {story.status}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setSelectedStoryForApproval(story)}
                          className="px-3 py-1.5 bg-brand-600/20 hover:bg-brand-600/30 border border-brand-500/40 text-brand-300 text-xs font-semibold rounded-lg transition-colors"
                        >
                          Review & Gate
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Ingestion Modal */}
      <StoryIngestionModal
        isOpen={showIngestionModal}
        onClose={() => setShowIngestionModal(false)}
        onStoryCreated={() => {
          fetchStories();
          setShowJobTracker(true);
        }}
      />

      {/* Pipeline Job Tracker */}
      <JobTrackerModal
        isOpen={showJobTracker}
        onClose={() => setShowJobTracker(false)}
      />

      {/* Approval Gate Reviewer Modal */}
      {selectedStoryForApproval && (
        <ApprovalGateModal
          story={selectedStoryForApproval}
          isOpen={!!selectedStoryForApproval}
          onClose={() => setSelectedStoryForApproval(null)}
          onStoryUpdated={() => {
            fetchStories();
          }}
        />
      )}
    </div>
  );
};
