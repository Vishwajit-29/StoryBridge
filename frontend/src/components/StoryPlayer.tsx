import React, { useState, useRef, useEffect } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  RotateCw,
  Volume2,
  VolumeX,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  AlertCircle,
} from 'lucide-react';
import { AudioChapter, LocalizedChapter } from '../types';
import { userApi } from '../services/api';

interface StoryPlayerProps {
  storyId: string;
  storyTitle: string;
  durationPreset: string;
  language: string;
  chapters: LocalizedChapter[];
  audioChapters?: AudioChapter[];
  onProgress?: (chapterIndex: number, progressSeconds: number) => void;
}

export const StoryPlayer: React.FC<StoryPlayerProps> = ({
  storyId,
  storyTitle,
  durationPreset,
  language,
  chapters,
  audioChapters,
  onProgress,
}) => {
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);

  const currentChapter = chapters[currentChapterIndex] || {
    chapter_number: 1,
    title: 'Chapter 1',
    content: 'Story narrative loading...',
  };

  const chNum = currentChapter.chapter_number || currentChapterIndex + 1;
  const audioSrc = `/api/audio/stream/${storyId}/${language.toLowerCase()}/${durationPreset.toLowerCase()}/ch${String(chNum).padStart(2, '0')}.mp3`;

  useEffect(() => {
    // Reset chapter and time when preset or language changes
    setCurrentTime(0);
    setIsPlaying(false);
    setAudioError(null);
  }, [storyId, language, durationPreset]);

  useEffect(() => {
    const token = localStorage.getItem('storybridge_token');
    if (token) {
      userApi.getBookmarkStatus(storyId)
        .then((res) => setIsBookmarked(res.data.bookmarked))
        .catch(() => {});
    }
  }, [storyId]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackRate;
    }
  }, [playbackRate]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    setAudioError(null);

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current
        .play()
        .then(() => setIsPlaying(true))
        .catch((e) => {
          console.warn('Audio playback error:', e);
          setAudioError('Click to play audio or verify audio file availability.');
          setIsPlaying(false);
        });
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      const cur = audioRef.current.currentTime;
      setCurrentTime(cur);
      if (onProgress) {
        onProgress(currentChapterIndex, cur);
      }
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration || 0);
      setAudioError(null);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = val;
      setCurrentTime(val);
    }
  };

  const skipTime = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.max(0, Math.min(duration, audioRef.current.currentTime + seconds));
    }
  };

  const changeChapter = (index: number) => {
    if (index >= 0 && index < chapters.length) {
      setCurrentChapterIndex(index);
      setCurrentTime(0);
      setIsPlaying(false);
      setAudioError(null);
    }
  };

  const toggleBookmark = async () => {
    try {
      const res = await userApi.toggleBookmark(storyId);
      setIsBookmarked(res.data.bookmarked);
    } catch (e) {
      alert('Please sign in to bookmark this story.');
    }
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs) || secs <= 0) return '0:00';
    const mins = Math.floor(secs / 60);
    const remainingSecs = Math.floor(secs % 60);
    return `${mins}:${remainingSecs < 10 ? '0' : ''}${remainingSecs}`;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
      {/* Audio Element */}
      <audio
        ref={audioRef}
        key={audioSrc}
        src={audioSrc}
        preload="metadata"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onError={() => {
          setAudioError('Audio streaming from storage...');
        }}
        onEnded={() => {
          if (currentChapterIndex < chapters.length - 1) {
            changeChapter(currentChapterIndex + 1);
          } else {
            setIsPlaying(false);
          }
        }}
      />

      {/* Player Header */}
      <div className="p-6 bg-gradient-to-b from-brand-950/40 via-slate-900 to-slate-900 border-b border-slate-800">
        <div className="flex items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-brand-500/20 text-brand-300">
                {durationPreset.toUpperCase()} STORY
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-slate-800 text-slate-300">
                {language.toUpperCase()}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              {currentChapter.title}
            </h2>
            <p className="text-xs text-slate-400">
              Chapter {currentChapter.chapter_number} of {chapters.length || 1} · {storyTitle}
            </p>
          </div>

          <button
            onClick={toggleBookmark}
            className={`p-2.5 rounded-xl border transition-all ${
              isBookmarked
                ? 'bg-amber-500/10 border-amber-500/40 text-amber-400'
                : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-white'
            }`}
          >
            <Bookmark className={`w-5 h-5 ${isBookmarked ? 'fill-amber-400' : ''}`} />
          </button>
        </div>

        {/* Scrubber & Duration */}
        <div className="space-y-1 mb-4">
          <input
            type="range"
            min="0"
            max={duration > 0 ? duration : 100}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-500"
          />
          <div className="flex justify-between text-[11px] font-mono text-slate-400">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Audio Controls */}
        <div className="flex items-center justify-between gap-2">
          {/* Speed Selector */}
          <div className="flex items-center gap-1">
            {[0.75, 1, 1.25, 1.5].map((rate) => (
              <button
                key={rate}
                onClick={() => setPlaybackRate(rate)}
                className={`px-2 py-1 rounded text-xs font-semibold ${
                  playbackRate === rate
                    ? 'bg-brand-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {rate}x
              </button>
            ))}
          </div>

          {/* Core Transport Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => changeChapter(currentChapterIndex - 1)}
              disabled={currentChapterIndex === 0}
              className="p-2 text-slate-400 hover:text-white disabled:opacity-30"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <button
              onClick={() => skipTime(-10)}
              className="p-2 text-slate-400 hover:text-white"
              title="Back 10s"
            >
              <RotateCcw className="w-5 h-5" />
            </button>

            <button
              onClick={togglePlay}
              className="w-12 h-12 rounded-2xl bg-brand-600 hover:bg-brand-500 text-white flex items-center justify-center shadow-lg shadow-brand-600/30 transition-transform active:scale-95"
            >
              {isPlaying ? <Pause className="w-6 h-6 fill-white" /> : <Play className="w-6 h-6 fill-white ml-0.5" />}
            </button>

            <button
              onClick={() => skipTime(10)}
              className="p-2 text-slate-400 hover:text-white"
              title="Forward 10s"
            >
              <RotateCw className="w-5 h-5" />
            </button>

            <button
              onClick={() => changeChapter(currentChapterIndex + 1)}
              disabled={currentChapterIndex === (chapters.length > 0 ? chapters.length - 1 : 0)}
              className="p-2 text-slate-400 hover:text-white disabled:opacity-30"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Chapter Selector Dropdown */}
          <select
            value={currentChapterIndex}
            onChange={(e) => changeChapter(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-brand-500 max-w-[140px] truncate"
          >
            {chapters.map((ch, idx) => (
              <option key={ch.chapter_id || idx} value={idx}>
                Ch {ch.chapter_number || idx + 1}: {ch.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Script Reader Body */}
      <div className="p-6 max-h-[480px] overflow-y-auto bg-slate-950/60 leading-relaxed text-slate-200 space-y-4">
        {currentChapter.cultural_notes && (
          <div className="p-3 bg-brand-950/30 border border-brand-800/40 rounded-xl text-xs text-brand-300">
            <span className="font-semibold">Cultural Note: </span>
            {currentChapter.cultural_notes}
          </div>
        )}

        <div className="text-base sm:text-lg leading-8 font-serif font-normal text-slate-200 whitespace-pre-line selection:bg-brand-600/40">
          {currentChapter.content}
        </div>
      </div>
    </div>
  );
};
