import React, { useState } from 'react';
import { Users, GitBranch, MapPin, Sparkles, AlertCircle, ArrowRight, Shield } from 'lucide-react';
import { StoryGraphData } from '../types';

interface StoryMapExplorerProps {
  graphData: StoryGraphData;
}

export const StoryMapExplorer: React.FC<StoryMapExplorerProps> = ({ graphData }) => {
  const [activeTab, setActiveTab] = useState<'entities' | 'events' | 'causality'>('entities');
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);

  const characters = graphData.entities.filter((e) => e.type === 'character');
  const locations = graphData.entities.filter((e) => e.type === 'location');
  const objects = graphData.entities.filter((e) => e.type === 'object' || e.type === 'concept');

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-brand-400" />
            <h3 className="text-xl font-bold text-white">Story Graph & Character Explorer</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Explore AI-extracted semantic relationships, characters, and causal plot lines.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center p-1 bg-slate-950 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('entities')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'entities'
                ? 'bg-brand-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Characters ({characters.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('events')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'events'
                ? 'bg-brand-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <GitBranch className="w-3.5 h-3.5" />
            <span>Events ({graphData.events.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('causality')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'causality'
                ? 'bg-brand-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ArrowRight className="w-3.5 h-3.5" />
            <span>Causality ({graphData.causal_links.length})</span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'entities' && (
          <div className="space-y-6">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-brand-400 mb-3">
                Characters & Entities
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {characters.map((char) => {
                  const isSelected = selectedEntityId === char.id;
                  const rels = graphData.relationships.filter(
                    (r) => r.source_entity_id === char.id || r.target_entity_id === char.id
                  );
                  return (
                    <div
                      key={char.id}
                      onClick={() => setSelectedEntityId(isSelected ? null : char.id)}
                      className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-brand-950/40 border-brand-500 ring-1 ring-brand-500'
                          : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span className="font-bold text-white text-sm">{char.name}</span>
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300">
                          Imp: {char.importance_score}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-2 mb-2">{char.description}</p>
                      
                      {char.aliases && char.aliases.length > 0 && (
                        <div className="text-[10px] text-slate-500">
                          Aliases: {char.aliases.join(', ')}
                        </div>
                      )}

                      {rels.length > 0 && (
                        <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                          <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                            Relationships ({rels.length}):
                          </span>
                          <div className="space-y-1">
                            {rels.map((r) => {
                              const otherId = r.source_entity_id === char.id ? r.target_entity_id : r.source_entity_id;
                              const other = graphData.entities.find((e) => e.id === otherId);
                              return (
                                <div key={r.id} className="text-[11px] text-slate-300 flex items-center gap-1">
                                  <span className="text-brand-400 font-medium">{r.relation_type}</span>
                                  <span>→</span>
                                  <span className="font-semibold text-white">{other?.name || otherId}</span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {locations.length > 0 && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Key Locations</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {locations.map((loc) => (
                    <div key={loc.id} className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                      <span className="font-semibold text-sm text-slate-200">{loc.name}</span>
                      <p className="text-xs text-slate-400 mt-0.5">{loc.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'events' && (
          <div className="space-y-3">
            {graphData.events.map((ev, idx) => (
              <div
                key={ev.id}
                className="p-4 bg-slate-950/60 border border-slate-800 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div className="flex items-start gap-3">
                  <div className="w-7 h-7 rounded-full bg-brand-600/30 border border-brand-500/40 text-brand-300 flex items-center justify-center text-xs font-bold shrink-0">
                    {idx + 1}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white text-sm">{ev.title}</span>
                      {ev.is_crucial && (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/30 text-amber-300">
                          Crucial Plot Event
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{ev.description}</p>
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-[11px] font-mono text-slate-400 block">
                    Score: <span className="text-brand-300 font-semibold">{ev.importance_score}</span>
                  </span>
                  <span className="text-[10px] text-slate-500 block">Order: {ev.chronological_order}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'causality' && (
          <div className="space-y-3">
            <p className="text-xs text-slate-400 mb-4">
              Causality links ensure that no prerequisite cause is omitted when generating shorter narrative versions.
            </p>
            <div className="grid grid-cols-1 gap-3">
              {graphData.causal_links.map((link, idx) => {
                const cause = graphData.events.find((e) => e.id === link.cause_event_id);
                const effect = graphData.events.find((e) => e.id === link.effect_event_id);
                return (
                  <div
                    key={idx}
                    className="p-4 bg-slate-950/60 border border-slate-800 rounded-2xl flex flex-col md:flex-row items-center gap-4 text-xs"
                  >
                    <div className="flex-1 p-2.5 bg-slate-900 border border-slate-800 rounded-xl w-full">
                      <span className="text-[10px] uppercase font-bold text-amber-400 block mb-0.5">Cause Event</span>
                      <span className="font-semibold text-white">{cause?.title || link.cause_event_id}</span>
                      <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{cause?.description}</p>
                    </div>

                    <div className="flex items-center gap-1 text-brand-400 font-semibold px-2">
                      <span>--({link.link_type})--&gt;</span>
                    </div>

                    <div className="flex-1 p-2.5 bg-slate-900 border border-slate-800 rounded-xl w-full">
                      <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-0.5">Effect Event</span>
                      <span className="font-semibold text-white">{effect?.title || link.effect_event_id}</span>
                      <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{effect?.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
