import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { VariableModel } from '../types/variable';
import { VariableTable } from '../components/VariableTable';
import { Braces } from 'lucide-react';

export const Variables: React.FC = () => {
  const { currentJobId } = useJob();
  const [variables, setVariables] = useState<VariableModel[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!currentJobId) return;
    setLoading(true);
    api.getVariables(currentJobId)
      .then((res) => setVariables(res.variables))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [currentJobId]);

  return (
    <div className="space-y-4">
      <div className="p-4 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-500/15 text-blue-400 border border-blue-500/30">
            <Braces className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Variables Explorer</h1>
            <p className="text-xs text-slate-400">
              Discovered variables, scopes, read/write usages, and Power Automate data type translations.
            </p>
          </div>
        </div>

        <div className="text-xs text-slate-400 font-mono">
          Total: <strong className="text-white">{variables.length}</strong> Variables
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading variables...</div>
      ) : (
        <VariableTable variables={variables} />
      )}
    </div>
  );
};
