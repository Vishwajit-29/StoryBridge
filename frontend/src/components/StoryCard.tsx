import React from 'react';
import { Link } from 'react-router-dom';
import { Play, Sparkles, ShieldCheck, Clock, Globe } from 'lucide-react';
import { Story } from '../types';

interface StoryCardProps {
  story: Story;
}

export const StoryCard: React.FC<StoryCardProps> = ({ story }) => {
  // Default stylish placeholders if no cover image
  const defaultBgColors = [
    'from-brand-900 via-indigo-950 to-slate-950',
    'from-emerald-950 via-slate-900 to-slate-950',
    'from-amber-950 via-slate-900 to-slate-950',
    'from-rose-950 via-purple-950 to-slate-950',
  ];
  const colorIndex = Math.abs(story.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)) % defaultBgColors.length;

  return (
    <Link
      to={`/stories/${story.id}`}
      className="group flex flex-col bg-slate-900 border border-slate-800/80 hover:border-brand-500/50 rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-brand-500/10 hover:-translate-y-1"
    >
      {/* Cover Banner */}
      <div className={`relative h-44 w-full bg-gradient-to-br ${defaultBgColors[colorIndex]} p-4 flex flex-col justify-between overflow-hidden`}>
        {/* Decorative subtle pattern */}
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#8b5cf6_1px,transparent_1px)] [background-size:16px_16px]"></div>

        {/* Top Badges */}
        <div className="relative z-10 flex items-center justify-between gap-2">
          <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-full bg-slate-950/70 border border-slate-700/60 text-brand-300 backdrop-blur-sm">
            {story.category || 'Story'}
          </span>
          <span className="flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 backdrop-blur-sm">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            {story.rightsType === 'PUBLIC_DOMAIN' ? 'Public Domain' : 'Open License'}
          </span>
        </div>

        {/* Title in banner if no image */}
        <div className="relative z-10">
          <h4 className="text-lg font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2">
            {story.title}
          </h4>
          {story.originalAuthor && (
            <p className="text-xs text-slate-300 line-clamp-1 mt-0.5">by {story.originalAuthor}</p>
          )}
        </div>

        {/* Play hover button */}
        <div className="absolute right-4 bottom-4 w-10 h-10 rounded-full bg-brand-600 group-hover:bg-brand-500 text-white flex items-center justify-center shadow-lg shadow-brand-600/30 scale-90 group-hover:scale-100 transition-all">
          <Play className="w-4 h-4 fill-white ml-0.5" />
        </div>
      </div>

      {/* Body Details */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <p className="text-xs text-slate-400 line-clamp-2 mb-3">
          {story.description || 'Experience this narrative in your preferred language and customized duration.'}
        </p>

        <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-brand-400" />
            <span>5m · 15m · 45m</span>
          </div>

          <div className="flex items-center gap-1">
            <Globe className="w-3.5 h-3.5 text-indigo-400" />
            <span className="font-medium text-slate-300">EN · HI · MR</span>
          </div>
        </div>
      </div>
    </Link>
  );
};
