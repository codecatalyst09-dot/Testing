import React, { useState, useMemo } from 'react';
import { VariableModel } from '../types/variable';
import { Search, Braces, ArrowRight, Tag } from 'lucide-react';

interface VariableTableProps {
  variables: VariableModel[];
  onSelectVariable?: (variable: VariableModel) => void;
}

export const VariableTable: React.FC<VariableTableProps> = ({ variables, onSelectVariable }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('All');
  const [selectedScope, setSelectedScope] = useState<string>('All');

  const uniqueTypes = useMemo(() => {
    return Array.from(new Set(variables.map((v) => v.type))).filter(Boolean);
  }, [variables]);

  const uniqueScopes = useMemo(() => {
    return Array.from(new Set(variables.map((v) => v.scope))).filter(Boolean);
  }, [variables]);

  const filtered = useMemo(() => {
    return variables.filter((v) => {
      if (selectedType !== 'All' && v.type !== selectedType) return false;
      if (selectedScope !== 'All' && v.scope !== selectedScope) return false;
      if (searchTerm) {
        const s = searchTerm.toLowerCase();
        return (
          v.name.toLowerCase().includes(s) ||
          v.powerAutomateEquivalent.toLowerCase().includes(s) ||
          v.type.toLowerCase().includes(s) ||
          v.scope.toLowerCase().includes(s)
        );
      }
      return true;
    });
  }, [variables, selectedType, selectedScope, searchTerm]);

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="p-4 rounded-xl bg-slate-850 border border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="relative min-w-[260px] flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search variable name, Power Automate type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-primary-500"
          />
        </div>

        <div className="flex items-center gap-2">
          {uniqueTypes.length > 1 && (
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 outline-none cursor-pointer"
            >
              <option value="All">All Types</option>
              {uniqueTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          )}

          {uniqueScopes.length > 1 && (
            <select
              value={selectedScope}
              onChange={(e) => setSelectedScope(e.target.value)}
              className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 outline-none cursor-pointer"
            >
              <option value="All">All Scopes</option>
              {uniqueScopes.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          )}

          <div className="text-xs text-slate-400 pl-2">
            Showing <strong className="text-slate-200">{filtered.length}</strong> of {variables.length}
          </div>
        </div>
      </div>

      {/* Variables Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-850 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Variable Name</th>
                <th className="py-3 px-4">A360 Type</th>
                <th className="py-3 px-4">Power Automate Equivalent</th>
                <th className="py-3 px-4">Scope</th>
                <th className="py-3 px-4">I/O Mode</th>
                <th className="py-3 px-4">Usage</th>
                <th className="py-3 px-4">Used in Steps</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.length > 0 ? (
                filtered.map((v, i) => (
                  <tr
                    key={i}
                    onClick={() => onSelectVariable && onSelectVariable(v)}
                    className="hover:bg-slate-800/60 transition-colors"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-blue-400">
                      ${v.name}$
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium border border-slate-700">
                        {v.type}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-medium text-emerald-400 flex items-center gap-1.5">
                      <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                      <span>{v.powerAutomateEquivalent}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {v.scope}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-1">
                        {v.isInput && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-purple-500/15 text-purple-400 border border-purple-500/30">
                            IN
                          </span>
                        )}
                        {v.isOutput && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
                            OUT
                          </span>
                        )}
                        {!v.isInput && !v.isOutput && (
                          <span className="text-[11px] text-slate-500">Internal</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                          v.usage === 'Read/Write'
                            ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30'
                            : v.usage === 'Write'
                            ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {v.usage}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px]">
                      {v.usedInSteps.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {v.usedInSteps.slice(0, 6).map((st) => (
                            <span key={st} className="px-1.5 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                              #{st}
                            </span>
                          ))}
                          {v.usedInSteps.length > 6 && (
                            <span className="text-slate-500 text-[10px]">
                              +{v.usedInSteps.length - 6}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-slate-500 italic">None</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No variables found.
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
