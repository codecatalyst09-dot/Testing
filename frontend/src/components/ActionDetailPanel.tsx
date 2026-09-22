import React, { useState } from 'react';
import { ActionModel } from '../types/action';
import { MigrationBadge } from './MigrationBadge';
import { X, Code, CheckSquare, Layers, HelpCircle, ArrowRight } from 'lucide-react';

interface ActionDetailPanelProps {
  action: ActionModel | null;
  onClose: () => void;
}

export const ActionDetailPanel: React.FC<ActionDetailPanelProps> = ({ action, onClose }) => {
  const [showRawJson, setShowRawJson] = useState<boolean>(false);

  if (!action) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-xl bg-slate-900 border-l border-slate-800 shadow-2xl z-50 flex flex-col transition-all">
      {/* Drawer Header */}
      <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-slate-400">Step {action.step}</span>
            <span className="text-slate-600">•</span>
            <span className="text-xs font-semibold text-slate-300">{action.task}</span>
          </div>
          <h3 className="text-base font-bold text-white mt-1 flex items-center gap-2">
            <span>{action.command}</span>
            {action.operation && (
              <span className="text-xs font-normal text-slate-400 font-mono">→ {action.operation}</span>
            )}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Power Automate Equivalent Card */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-slate-850 to-slate-900 border border-primary-500/30 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-primary-400 uppercase tracking-wider">
              Power Automate Equivalent
            </span>
            <MigrationBadge type="platform" value={action.cloudOrDesktop} />
          </div>
          <div className="text-base font-bold text-white flex items-center gap-2">
            <ArrowRight className="w-4 h-4 text-primary-400 shrink-0" />
            <span>{action.powerAutomateAction}</span>
          </div>

          <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400">Strategy:</span>
              <MigrationBadge type="strategy" value={action.migrationStrategy} />
            </div>
            <div className="flex items-center gap-1.5 ml-auto">
              <span className="text-slate-400">Complexity:</span>
              <MigrationBadge type="complexity" value={action.migrationComplexity} />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400">Confidence:</span>
              <span className="font-mono font-bold text-slate-200">{Math.round(action.confidence * 100)}%</span>
            </div>
          </div>
        </div>

        {/* Reason / Architecture Justification */}
        <div>
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5" />
            Migration Rationale
          </h4>
          <div className="p-3.5 rounded-xl bg-slate-850 border border-slate-800 text-xs text-slate-300 leading-relaxed">
            {action.reason}
          </div>
        </div>

        {/* Parameters & Attributes */}
        <div>
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5" />
            Action Parameters
          </h4>
          <div className="p-3.5 rounded-xl bg-slate-850 border border-slate-800 text-xs space-y-2">
            {Object.keys(action.attributes).length > 0 ? (
              Object.entries(action.attributes).map(([k, v]) => (
                <div key={k} className="flex items-start justify-between gap-4 font-mono text-[11px] border-b border-slate-800/60 pb-1.5 last:border-0 last:pb-0">
                  <span className="text-slate-400 shrink-0">{k}:</span>
                  <span className="text-slate-200 text-right break-all">{String(v)}</span>
                </div>
              ))
            ) : (
              <span className="text-slate-500 italic">No custom attributes</span>
            )}
          </div>
        </div>

        {/* Variables Used & Created */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3.5 rounded-xl bg-slate-850 border border-slate-800 text-xs">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Variables Read
            </span>
            {action.variablesUsed.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {action.variablesUsed.map((v) => (
                  <span key={v} className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-mono text-[11px] border border-blue-500/20">
                    ${v}$
                  </span>
                ))}
              </div>
            ) : (
              <span className="text-slate-500 italic">None</span>
            )}
          </div>

          <div className="p-3.5 rounded-xl bg-slate-850 border border-slate-800 text-xs">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Variables Assigned
            </span>
            {action.variablesCreated.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {action.variablesCreated.map((v) => (
                  <span key={v} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-mono text-[11px] border border-emerald-500/20">
                    ${v}$
                  </span>
                ))}
              </div>
            ) : (
              <span className="text-slate-500 italic">None</span>
            )}
          </div>
        </div>

        {/* Dependencies */}
        {action.dependencies.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Required Dependencies
            </h4>
            <div className="flex flex-wrap gap-2">
              {action.dependencies.map((d, i) => (
                <span key={i} className="px-2.5 py-1 rounded-lg bg-slate-850 border border-slate-700 text-slate-300 text-xs font-medium">
                  {d}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Manual Migration Steps */}
        {action.manualSteps.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 text-amber-400">
              <CheckSquare className="w-3.5 h-3.5" />
              Migration Engineer Checklist
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-300 p-3 rounded-xl bg-slate-850 border border-slate-800">
              {action.manualSteps.map((s, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-400 font-bold">•</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Raw JSON toggle */}
        <div>
          <button
            onClick={() => setShowRawJson(!showRawJson)}
            className="flex items-center gap-2 text-xs font-semibold text-primary-400 hover:text-primary-300 transition-colors"
          >
            <Code className="w-4 h-4" />
            <span>{showRawJson ? 'Hide Raw A360 JSON' : 'View Raw A360 JSON'}</span>
          </button>
          {showRawJson && (
            <pre className="mt-2 p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-60">
              {JSON.stringify(action.rawAction, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};
