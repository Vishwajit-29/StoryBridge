import React, { useEffect, useState } from 'react';
import { RefreshCw, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { adminApi } from '../../services/api';
import { PipelineJob } from '../../types';

interface JobTrackerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const JobTrackerModal: React.FC<JobTrackerModalProps> = ({ isOpen, onClose }) => {
  const [jobs, setJobs] = useState<PipelineJob[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const res = await adminApi.getAllJobs();
      setJobs(res.data);
    } catch (e) {
      console.error('Failed to fetch jobs', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchJobs();
      const timer = setInterval(fetchJobs, 4000);
      return () => clearInterval(timer);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-3xl p-6 sm:p-8 shadow-2xl relative my-8">
        <button onClick={onClose} className="absolute top-5 right-5 text-slate-400 hover:text-white">
          ✕
        </button>

        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-xl font-bold text-white">Pipeline Jobs & Worker Monitor</h3>
            <p className="text-xs text-slate-400">
              Live status of asynchronous AI ingestion, graph extraction, compression, and TTS tasks.
            </p>
          </div>
          <button
            onClick={fetchJobs}
            disabled={loading}
            className="p-2 text-slate-400 hover:text-brand-400 rounded-xl bg-slate-950 border border-slate-800"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="space-y-3 max-h-[480px] overflow-y-auto">
          {jobs.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-sm">
              No active pipeline jobs found.
            </div>
          ) : (
            jobs.map((job) => {
              const isCompleted = job.status === 'COMPLETED';
              const isFailed = job.status === 'FAILED';
              const isProcessing = job.status === 'PROCESSING' || job.status === 'QUEUED';

              return (
                <div
                  key={job.id}
                  className="p-4 bg-slate-950/70 border border-slate-800 rounded-2xl space-y-2.5"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      {isCompleted && <CheckCircle className="w-4 h-4 text-emerald-400" />}
                      {isFailed && <XCircle className="w-4 h-4 text-rose-400" />}
                      {isProcessing && <Clock className="w-4 h-4 text-amber-400 animate-spin" />}
                      <span className="font-bold text-sm text-white">{job.storyId}</span>
                      <span className="text-xs text-slate-400">({job.id})</span>
                    </div>

                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                        isCompleted
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : isFailed
                          ? 'bg-rose-500/20 text-rose-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}
                    >
                      {job.status} · {job.stage}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 font-mono">{job.currentStep || 'In progress...'}</p>

                  {/* Progress bar */}
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        isFailed ? 'bg-rose-500' : 'bg-brand-500'
                      }`}
                      style={{ width: `${job.progressPercentage || (isCompleted ? 100 : 35)}%` }}
                    />
                  </div>

                  {job.errorMessage && (
                    <div className="p-2.5 bg-rose-950/40 border border-rose-800/40 rounded-xl text-[11px] text-rose-300">
                      {job.errorMessage}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
