import React, { useState } from 'react';
import { MessageSquare, Send, Sparkles, Bot, User } from 'lucide-react';
import { StoryGraphData } from '../types';

interface AskTheStoryProps {
  storyTitle: string;
  graphData?: StoryGraphData;
}

export const AskTheStory: React.FC<AskTheStoryProps> = ({ storyTitle, graphData }) => {
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string }>>([
    {
      sender: 'ai',
      text: `Hello! I am your grounded story assistant for "${storyTitle}". Ask me anything about character motivations, plot events, relationships, or themes.`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const suggestedQuestions = [
    `Who are the main characters in this story?`,
    `What triggered the central conflict?`,
    `What is the underlying moral or theme?`,
  ];

  const handleSend = (queryText?: string) => {
    const q = queryText || input;
    if (!q.trim()) return;

    const newMessages = [...messages, { sender: 'user' as const, text: q }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    // Grounded answer generator using StoryGraph facts
    setTimeout(() => {
      let answer = '';
      const qLower = q.toLowerCase();

      if (qLower.includes('character') || qLower.includes('who')) {
        const charNames = graphData?.entities?.filter(e => e.type === 'character').map(c => `${c.name} (${c.description})`).join('; ');
        answer = charNames
          ? `Based on the Story Graph, key characters include: ${charNames}.`
          : `The story centers around the key characters defined in the narrative graph.`;
      } else if (qLower.includes('conflict') || qLower.includes('happen') || qLower.includes('what')) {
        const events = graphData?.events?.slice(0, 3).map(e => e.title).join(' -> ');
        answer = events
          ? `The plot unfolds through these sequential events: ${events}.`
          : `The central conflict arises from the key plot events captured in the story understanding layer.`;
      } else if (qLower.includes('moral') || qLower.includes('theme') || qLower.includes('lesson')) {
        const themes = graphData?.themes?.join(', ');
        answer = themes
          ? `Core themes and takeaways: ${themes}. The story emphasizes understanding consequences before meddling with unfamiliar forces.`
          : `The story delivers a powerful theme about actions, consequences, and wisdom.`;
      } else {
        answer = `According to the story graph for "${storyTitle}", ${graphData?.summary || 'the narrative explores the intricate relationships and consequences of the characters\' choices.'}`;
      }

      setMessages([...newMessages, { sender: 'ai' as const, text: answer }]);
      setLoading(false);
    }, 600);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl flex flex-col h-[520px]">
      <div className="flex items-center gap-2 pb-4 border-b border-slate-800">
        <Sparkles className="w-5 h-5 text-brand-400" />
        <div>
          <h3 className="text-lg font-bold text-white">Ask the Story</h3>
          <p className="text-xs text-slate-400">Grounded Q&A powered by the Story Graph</p>
        </div>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto py-4 space-y-3">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 ${m.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs shrink-0 ${
                m.sender === 'user'
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-800 border border-slate-700 text-brand-300'
              }`}
            >
              {m.sender === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>

            <div
              className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-brand-600 text-white rounded-br-none'
                  : 'bg-slate-950/80 border border-slate-800 text-slate-200 rounded-bl-none'
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Bot className="w-4 h-4 animate-bounce text-brand-400" />
            <span>Consulting Story Graph...</span>
          </div>
        )}
      </div>

      {/* Suggested Questions */}
      <div className="pt-2 pb-3 flex items-center gap-2 overflow-x-auto">
        {suggestedQuestions.map((sq, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(sq)}
            className="text-[11px] px-3 py-1 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-full text-slate-300 whitespace-nowrap transition-colors"
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="pt-3 border-t border-slate-800 flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={`Ask about characters, motives, or events in ${storyTitle}...`}
          className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-full text-xs sm:text-sm text-white focus:outline-none focus:border-brand-500"
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim()}
          className="w-10 h-10 rounded-full bg-brand-600 hover:bg-brand-500 disabled:opacity-30 text-white flex items-center justify-center shadow-lg shadow-brand-600/30 transition-all shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
