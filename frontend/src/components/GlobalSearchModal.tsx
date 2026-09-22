import React, { useState, useEffect, useRef } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { Search, X, Layers, Braces, EyeOff, FolderTree, ArrowRight, Loader2 } from 'lucide-react';
import { MigrationBadge } from './MigrationBadge';

export const GlobalSearchModal: React.FC = () => {
  const { currentJobId, searchModalOpen, setSearchModalOpen, setActiveTab, setInspectingActionId } = useJob();
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<any>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut listener for Ctrl+K / Cmd+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setSearchModalOpen(true);
      }
      if (e.key === 'Escape') {
        setSearchModalOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setSearchModalOpen]);

  useEffect(() => {
    if (searchModalOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
      setResults(null);
    }
  }, [searchModalOpen]);

  // Debounced search
  useEffect(() => {
    if (!query.trim() || !currentJobId) {
      setResults(null);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await api.globalSearch(currentJobId, query.trim());
        setResults(res);
      } catch (err) {
        console.error('Search failed', err);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query, currentJobId]);

  if (!searchModalOpen) return null;

  const navigateToAction = (step: number) => {
    setSearchModalOpen(false);
    setActiveTab('actions');
    setInspectingActionId(String(step));
  };

  const navigateToVariables = () => {
    setSearchModalOpen(false);
    setActiveTab('variables');
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-start justify-center pt-20 p-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
        {/* Search Input Bar */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3 bg-slate-950">
          <Search className="w-5 h-5 text-primary-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search across workflow, tasks, actions, variables, commands, step numbers..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          {loading ? (
            <Loader2 className="w-5 h-5 text-slate-400 animate-spin shrink-0" />
          ) : query ? (
            <button
              onClick={() => setQuery('')}
              className="text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          ) : (
            <kbd className="px-2 py-0.5 text-[10px] bg-slate-800 rounded text-slate-400 border border-slate-700">
              ESC
            </kbd>
          )}
        </div>

        {/* Results Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!results && !loading && (
            <div className="py-12 text-center text-slate-500 text-xs">
              Type to search variables, commands, or step numbers.
            </div>
          )}

          {results && results.total_matches === 0 && !loading && (
            <div className="py-12 text-center text-slate-500 text-xs">
              No results found matching &quot;{query}&quot;
            </div>
          )}

          {results && results.total_matches > 0 && (
            <div className="space-y-4">
              {/* Action Matches */}
              {results.actions.length > 0 && (
                <div>
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                    Actions ({results.actions.length})
                  </span>
                  <div className="space-y-1.5">
                    {results.actions.map((act: any) => (
                      <div
                        key={act.step}
                        onClick={() => navigateToAction(act.step)}
                        className="p-3 rounded-xl bg-slate-850 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 cursor-pointer transition-all flex items-center justify-between gap-4"
                      >
                        <div className="flex items-center gap-3">
                          <span className="font-mono text-xs font-bold text-slate-400">
                            #{act.step}
                          </span>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-xs text-white">{act.command}</span>
                              <span className="text-slate-500 text-[11px]">in {act.task}</span>
                            </div>
                            <p className="text-[11px] text-emerald-400 font-medium">
                              ↳ {act.powerAutomateAction}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <MigrationBadge type="platform" value={act.platform} />
                          <ArrowRight className="w-4 h-4 text-slate-500" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Variable Matches */}
              {results.variables.length > 0 && (
                <div>
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                    Variables ({results.variables.length})
                  </span>
                  <div className="space-y-1.5">
                    {results.variables.map((v: any, i: number) => (
                      <div
                        key={i}
                        onClick={navigateToVariables}
                        className="p-3 rounded-xl bg-slate-850 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 cursor-pointer transition-all flex items-center justify-between"
                      >
                        <div className="flex items-center gap-2">
                          <Braces className="w-4 h-4 text-blue-400" />
                          <span className="font-mono text-xs font-bold text-blue-400">
                            ${v.name}$
                          </span>
                          <span className="text-slate-500 text-xs">({v.type})</span>
                        </div>
                        <div className="text-xs text-slate-300 font-medium">
                          Maps to: <strong className="text-emerald-400">{v.powerAutomateEquivalent}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Task Matches */}
              {results.tasks.length > 0 && (
                <div>
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                    Tasks ({results.tasks.length})
                  </span>
                  <div className="space-y-1.5">
                    {results.tasks.map((t: any, i: number) => (
                      <div
                        key={i}
                        onClick={() => {
                          setSearchModalOpen(false);
                          setActiveTab('dependencies');
                        }}
                        className="p-3 rounded-xl bg-slate-850 hover:bg-slate-800 border border-slate-800 cursor-pointer transition-all flex items-center justify-between"
                      >
                        <div className="flex items-center gap-2">
                          <FolderTree className="w-4 h-4 text-purple-400" />
                          <span className="font-semibold text-xs text-white">{t.name}</span>
                          <span className="text-slate-400 text-xs">• {t.purpose}</span>
                        </div>
                        <span className="text-xs text-slate-400 font-mono">{t.stepsCount} steps</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
