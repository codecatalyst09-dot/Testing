import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { MigrationPlanModel } from '../types/migration';
import { TargetArchitectureView } from '../components/TargetArchitectureView';
import { Compass } from 'lucide-react';

export const Migration: React.FC = () => {
  const { currentJobId } = useJob();
  const [plan, setPlan] = useState<MigrationPlanModel | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!currentJobId) return;
    setLoading(true);
    api.getMigrationPlan(currentJobId)
      .then(setPlan)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [currentJobId]);

  return (
    <div className="space-y-4">
      <div className="p-4 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-500/15 text-blue-400 border border-primary-500/30">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Power Automate Target Architecture</h1>
            <p className="text-xs text-slate-400">
              Solution blueprint, Cloud Flow and Desktop Flow schemas, connection recommendations, and risk assessment.
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading target architecture blueprint...</div>
      ) : plan ? (
        <TargetArchitectureView plan={plan} />
      ) : (
        <div className="p-8 text-center text-slate-500 text-xs">Migration blueprint not generated.</div>
      )}
    </div>
  );
};
