import React from 'react';
import { PipelineProgress } from '../components/PipelineProgress';
import { Activity } from 'lucide-react';

export const Analysis: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-blue-500/15 text-blue-400 border border-blue-500/30">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Pipeline Execution Tracker</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              13-Stage deterministic extraction, preprocessor pruning, classification, and blueprint generation.
            </p>
          </div>
        </div>
      </div>

      <PipelineProgress />
    </div>
  );
};
