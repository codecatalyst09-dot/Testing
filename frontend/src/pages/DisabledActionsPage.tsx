import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { DisabledActionModel } from '../types/action';
import { DisabledActionsTable } from '../components/DisabledActionsTable';
import { EyeOff } from 'lucide-react';

export const DisabledActionsPage: React.FC = () => {
  const { currentJobId } = useJob();
  const [disabledActions, setDisabledActions] = useState<DisabledActionModel[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!currentJobId) return;
    setLoading(true);
    api.getDisabledActions(currentJobId)
      .then(setDisabledActions)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [currentJobId]);

  return (
    <div className="space-y-4">
      <div className="p-4 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <EyeOff className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Disabled Actions Audit</h1>
            <p className="text-xs text-slate-400">
              Actions detected as disabled prior to preprocessing removal, preserved into disabled_actions.json.
            </p>
          </div>
        </div>

        <div className="text-xs text-slate-400 font-mono">
          Total: <strong className="text-white">{disabledActions.length}</strong> Disabled Steps
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading disabled actions...</div>
      ) : (
        <DisabledActionsTable disabledActions={disabledActions} />
      )}
    </div>
  );
};
