import React, { useState } from 'react';
import { DisabledActionModel } from '../types/action';
import { EyeOff, AlertCircle, Layers, Code } from 'lucide-react';

interface DisabledActionsTableProps {
  disabledActions: DisabledActionModel[];
}

export const DisabledActionsTable: React.FC<DisabledActionsTableProps> = ({ disabledActions }) => {
  const [selectedAction, setSelectedAction] = useState<DisabledActionModel | null>(null);

  return (
    <div className="space-y-4">
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-start gap-3">
        <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-amber-400" />
        <div>
          <strong className="font-semibold block mb-0.5">Pre-Pruning Capture Notice:</strong>
          These actions were flagged as <code className="bg-amber-500/20 px-1 py-0.5 rounded">disabled: true</code> in the original A360 automation package.
          They were captured and preserved into <code className="bg-amber-500/20 px-1 py-0.5 rounded font-mono">disabled_actions.json</code> before the cleaning stage intentionally removed them from runtime execution.
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-850 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Original Step</th>
                <th className="py-3 px-4">Taskbot</th>
                <th className="py-3 px-4">A360 Command</th>
                <th className="py-3 px-4">Action / Operation</th>
                <th className="py-3 px-4">Parent Scope</th>
                <th className="py-3 px-4">Reason</th>
                <th className="py-3 px-4 text-right">Attributes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {disabledActions.length > 0 ? (
                disabledActions.map((da, idx) => (
                  <tr
                    key={idx}
                    className="hover:bg-slate-800/60 transition-colors"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-slate-400">
                      #{da.originalStep}
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-300">
                      {da.task}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-rose-400 flex items-center gap-1.5 line-through opacity-80">
                        <EyeOff className="w-3.5 h-3.5 shrink-0" />
                        {da.command}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-mono">
                      {da.action}
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {da.parent || 'Root'}
                    </td>
                    <td className="py-3 px-4 text-slate-400 italic">
                      {da.reason}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedAction(da)}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-mono border border-slate-700 transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No disabled actions recorded in this automation package.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal / Dialog for inspecting disabled action attributes */}
      {selectedAction && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <span className="text-xs font-mono text-slate-400">Disabled Step #{selectedAction.originalStep}</span>
                <h3 className="text-base font-bold text-white mt-0.5 flex items-center gap-2">
                  <EyeOff className="w-4 h-4 text-rose-400" />
                  <span>{selectedAction.command}</span>
                </h3>
              </div>
              <button
                onClick={() => setSelectedAction(null)}
                className="text-slate-400 hover:text-white text-xs font-semibold px-2 py-1 rounded bg-slate-800"
              >
                Close
              </button>
            </div>

            <div>
              <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Captured Attributes (Original JSON)
              </h5>
              <pre className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-64">
                {JSON.stringify(selectedAction.attributes, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
