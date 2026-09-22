import React, { useState, useMemo } from 'react';
import { ActionModel, PlatformType, ComplexityType } from '../types/action';
import { MigrationBadge } from './MigrationBadge';
import { Search, Filter, ArrowUpDown, ChevronRight, Layers } from 'lucide-react';

interface ActionTableProps {
  actions: ActionModel[];
  onSelectAction: (action: ActionModel) => void;
}

export const ActionTable: React.FC<ActionTableProps> = ({ actions, onSelectAction }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('All');
  const [selectedComplexity, setSelectedComplexity] = useState<string>('All');
  const [selectedTask, setSelectedTask] = useState<string>('All');
  const [sortField, setSortField] = useState<'step' | 'confidence'>('step');
  const [sortAsc, setSortAsc] = useState<boolean>(true);

  // Extract unique tasks
  const uniqueTasks = useMemo(() => {
    return Array.from(new Set(actions.map((a) => a.task))).filter(Boolean);
  }, [actions]);

  // Filtering & Sorting
  const filteredActions = useMemo(() => {
    return actions
      .filter((a) => {
        if (selectedPlatform !== 'All' && a.cloudOrDesktop !== selectedPlatform) return false;
        if (selectedComplexity !== 'All' && a.migrationComplexity !== selectedComplexity) return false;
        if (selectedTask !== 'All' && a.task !== selectedTask) return false;
        if (searchTerm) {
          const s = searchTerm.toLowerCase();
          const match =
            a.command.toLowerCase().includes(s) ||
            a.powerAutomateAction.toLowerCase().includes(s) ||
            a.reason.toLowerCase().includes(s) ||
            a.task.toLowerCase().includes(s) ||
            String(a.step).includes(s) ||
            a.variablesUsed.some((v) => v.toLowerCase().includes(s));
          if (!match) return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (sortField === 'step') {
          return sortAsc ? a.step - b.step : b.step - a.step;
        } else {
          return sortAsc ? a.confidence - b.confidence : b.confidence - a.confidence;
        }
      });
  }, [actions, selectedPlatform, selectedComplexity, selectedTask, searchTerm, sortField, sortAsc]);

  const toggleSort = (field: 'step' | 'confidence') => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls & Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-850 border border-slate-800 flex flex-wrap items-center justify-between gap-3">
        {/* Search */}
        <div className="relative min-w-[260px] flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search command, Power Automate target, variable..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-primary-500"
          />
        </div>

        {/* Filter Dropdowns */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Platform Filter */}
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 outline-none focus:border-primary-500 cursor-pointer"
          >
            <option value="All">All Platforms</option>
            <option value="Power Automate Cloud">Cloud Flow</option>
            <option value="Power Automate Desktop">Desktop Flow (PAD)</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Manual Review">Manual Review</option>
          </select>

          {/* Complexity Filter */}
          <select
            value={selectedComplexity}
            onChange={(e) => setSelectedComplexity(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 outline-none focus:border-primary-500 cursor-pointer"
          >
            <option value="All">All Complexities</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>

          {/* Task Filter */}
          {uniqueTasks.length > 1 && (
            <select
              value={selectedTask}
              onChange={(e) => setSelectedTask(e.target.value)}
              className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 outline-none focus:border-primary-500 cursor-pointer"
            >
              <option value="All">All Tasks</option>
              {uniqueTasks.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          )}

          <div className="text-xs text-slate-400 pl-2">
            Showing <strong className="text-slate-200">{filteredActions.length}</strong> of {actions.length}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-850 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900 text-slate-400 font-semibold uppercase tracking-wider">
                <th
                  onClick={() => toggleSort('step')}
                  className="py-3 px-4 cursor-pointer hover:text-slate-200 select-none w-20"
                >
                  <div className="flex items-center gap-1">
                    <span>Step</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4">Taskbot</th>
                <th className="py-3 px-4">A360 Action</th>
                <th className="py-3 px-4">Power Automate Equivalent</th>
                <th className="py-3 px-4">Platform</th>
                <th className="py-3 px-4">Complexity</th>
                <th
                  onClick={() => toggleSort('confidence')}
                  className="py-3 px-4 cursor-pointer hover:text-slate-200 select-none text-right"
                >
                  <div className="flex items-center justify-end gap-1">
                    <span>Confidence</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-3 w-10"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredActions.length > 0 ? (
                filteredActions.map((action) => (
                  <tr
                    key={action.id}
                    onClick={() => onSelectAction(action)}
                    className="hover:bg-slate-800/60 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-slate-300">
                      #{action.step}
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-[11px] font-medium border border-slate-700">
                        {action.task}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-100 flex items-center gap-1.5">
                        <span>{action.command}</span>
                        {action.operation && (
                          <span className="text-slate-400 font-normal text-[11px] font-mono">
                            • {action.operation}
                          </span>
                        )}
                      </div>
                      {action.variablesUsed.length > 0 && (
                        <div className="flex gap-1 mt-1">
                          {action.variablesUsed.slice(0, 2).map((v) => (
                            <span key={v} className="text-[10px] text-blue-400 font-mono">
                              ${v}$
                            </span>
                          ))}
                          {action.variablesUsed.length > 2 && (
                            <span className="text-[10px] text-slate-500">
                              +{action.variablesUsed.length - 2}
                            </span>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium text-slate-200">
                        {action.powerAutomateAction}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate max-w-xs">
                        {action.migrationStrategy}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <MigrationBadge type="platform" value={action.cloudOrDesktop} />
                    </td>
                    <td className="py-3 px-4">
                      <MigrationBadge type="complexity" value={action.migrationComplexity} />
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-semibold text-slate-300">
                      {Math.round(action.confidence * 100)}%
                    </td>
                    <td className="py-3 px-3 text-right">
                      <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-primary-400 transition-colors" />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">
                    No actions match the selected filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
