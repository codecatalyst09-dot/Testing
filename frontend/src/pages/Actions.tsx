import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { ActionModel } from '../types/action';
import { ActionTable } from '../components/ActionTable';
import { ActionDetailPanel } from '../components/ActionDetailPanel';
import { ListTree, Layers } from 'lucide-react';

export const Actions: React.FC = () => {
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

  return (
    <div className="space-y-4">
      {/* Top Banner */}
      <div className="p-4 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-500/15 text-blue-400 border border-blue-500/30">
            <ListTree className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Action-by-Action Explorer</h1>
            <p className="text-xs text-slate-400">
              Granular inspection of every A360 step, Power Automate target, complexity, and rationale.
            </p>
          </div>
        </div>

        <div className="text-xs text-slate-400 font-mono">
          Total: <strong className="text-white">{actions.length}</strong> Steps
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading actions...</div>
      ) : (
        <ActionTable actions={actions} onSelectAction={handleSelectAction} />
      )}

      {/* Slide-over Detail Panel */}
      <ActionDetailPanel action={selectedAction} onClose={handleClosePanel} />
    </div>
  );
};
