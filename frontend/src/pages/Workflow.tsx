import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { ActionModel } from '../types/action';
import { WorkflowGraph } from '../components/WorkflowGraph';
import { ActionDetailPanel } from '../components/ActionDetailPanel';
import { GitFork, Layers, Info } from 'lucide-react';

export const Workflow: React.FC = () => {
  const { currentJobId, inspectingActionId, setInspectingActionId } = useJob();
  const [actions, setActions] = useState<ActionModel[]>([]);
  const [selectedAction, setSelectedAction] = useState<ActionModel | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!currentJobId) return;
    setLoading(true);
    api.getActions(currentJobId)
      .then((res) => {
        setActions(res.actions);
        if (inspectingActionId) {
          const matched = res.actions.find(
            (a) => a.id === inspectingActionId || String(a.step) === inspectingActionId
          );
          if (matched) setSelectedAction(matched);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [currentJobId, inspectingActionId]);

  const handleSelectAction = (action: ActionModel) => {
    setSelectedAction(action);
    setInspectingActionId(action.id);
  };

  const handleClosePanel = () => {
    setSelectedAction(null);
    setInspectingActionId(null);
  };

  if (!currentJobId) {
    return (
      <div className="p-8 text-center text-slate-500 text-xs">
        No active package selected.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Top Banner */}
      <div className="p-4 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-purple-500/15 text-purple-400 border border-purple-500/30">
            <GitFork className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Interactive RPA Flow Canvas</h1>
            <p className="text-xs text-slate-400">
              Interactive node execution sequence with color classification. Click any node to inspect migration specifications.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
          <Info className="w-4 h-4 text-primary-400" />
          <span>Click any node to view Power Automate equivalent</span>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading workflow graph...</div>
      ) : actions.length > 0 ? (
        <WorkflowGraph actions={actions} onSelectAction={handleSelectAction} />
      ) : (
        <div className="p-8 text-center text-slate-500 text-xs">No actions found.</div>
      )}

      {/* Slide-over Detail Panel */}
      <ActionDetailPanel action={selectedAction} onClose={handleClosePanel} />
    </div>
  );
};
