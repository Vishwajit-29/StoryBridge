import React from 'react';
import { Clock, Zap, BookOpen, Sparkles } from 'lucide-react';

interface DurationSliderProps {
  selectedPreset: 'all' | 'quick' | 'standard' | 'complete';
  onChange: (preset: 'all' | 'quick' | 'standard' | 'complete') => void;
}

export const DurationSlider: React.FC<DurationSliderProps> = ({ selectedPreset, onChange }) => {
  const presets = [
    { id: 'all', label: 'All Durations', time: 'Any time', icon: Clock, desc: 'Explore all' },
    { id: 'quick', label: 'Quick Story', time: '3–7 min', icon: Zap, desc: 'Core plot & key twists' },
    { id: 'standard', label: 'Standard Story', time: '10–20 min', icon: Sparkles, desc: 'Main compressed narrative' },
    { id: 'complete', label: 'Complete Story', time: '30–60+ min', icon: BookOpen, desc: 'Full rich experience' },
  ];

  return (
    <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800/80 rounded-2xl p-5 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-brand-400" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              How much time do you have?
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            StoryBridge automatically compresses narratives to fit your schedule perfectly.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        {presets.map((p) => {
          const Icon = p.icon;
          const isSelected = selectedPreset === p.id;
          return (
            <button
              key={p.id}
              onClick={() => onChange(p.id as any)}
              className={`flex flex-col items-start text-left p-3 rounded-xl border transition-all ${
                isSelected
                  ? 'bg-brand-600/15 border-brand-500/80 text-white shadow-lg shadow-brand-500/10 ring-1 ring-brand-500/40'
                  : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between w-full mb-1.5">
                <Icon className={`w-4 h-4 ${isSelected ? 'text-brand-400' : 'text-slate-500'}`} />
                <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                  isSelected ? 'bg-brand-500/20 text-brand-300' : 'bg-slate-900 text-slate-400'
                }`}>
                  {p.time}
                </span>
              </div>
              <span className="text-sm font-semibold text-slate-100">{p.label}</span>
              <span className="text-[11px] text-slate-400 line-clamp-1">{p.desc}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
