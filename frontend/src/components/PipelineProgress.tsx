import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { PipelineStage, JobStatusResponse } from '../types/job';
import { CheckCircle2, Circle, Loader2, AlertCircle, ArrowRight, GitFork, LayoutDashboard } from 'lucide-react';

const STAGES: { stage: PipelineStage; label: string; desc: string }[] = [
  { stage: 'FILE_UPLOADED', label: 'File Uploaded', desc: 'Validated input archive and checksums' },
  { stage: 'ZIP_EXTRACTED', label: 'ZIP Extracted', desc: 'Unpacked safely with path traversal defense' },
  { stage: 'A360_FILES_DISCOVERED', label: 'A360 Files Discovered', desc: 'Identified taskbot workflows and manifests' },
  { stage: 'ORIGINAL_ACTIONS_CAPTURED', label: 'Original Actions Captured', desc: 'Indexed source action sequence and attributes' },
  { stage: 'DISABLED_ACTIONS_DETECTED', label: 'Disabled Actions Recorded', desc: 'Preserved disabled steps before pruning' },
  { stage: 'JSON_CLEANED', label: 'JSON Cleaned', desc: 'Applied authoritative A360 preprocessing algorithm' },
  { stage: 'WORKFLOW_PARSED', label: 'Workflow Parsed', desc: 'Parsed nested blocks, loops, and conditions' },
  { stage: 'VARIABLES_EXTRACTED', label: 'Variables Extracted', desc: 'Extracted variables, scopes, and types' },
  { stage: 'SUBTASKS_IDENTIFIED', label: 'Subtasks Identified', desc: 'Built Run Task hierarchy and dependency tree' },
  { stage: 'ACTIONS_ANALYZED', label: 'Actions Analyzed', desc: 'Step-by-step RPA operation evaluation' },
  { stage: 'CLASSIFICATION_COMPLETE', label: 'Classification Complete', desc: 'Categorized into Cloud, Desktop, Hybrid, or Review' },
  { stage: 'MAPPING_COMPLETE', label: 'Migration Mapping Complete', desc: 'Mapped to Power Automate connectors & PAD actions' },
  { stage: 'REPORT_GENERATED', label: 'Report Generated', desc: 'Compiled blueprint, HTML report, and ZIP package' },
];

export const PipelineProgress: React.FC = () => {
  const { currentJobId, setActiveTab, refreshJobs } = useJob();
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentJobId) return;

    let isMounted = true;
    const fetchStatus = async () => {
      try {
        const data = await api.getJobStatus(currentJobId);
        if (isMounted) {
          setStatus(data);
          if (data.status === 'COMPLETED' || data.status === 'FAILED') {
            await refreshJobs();
          }
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Error tracking pipeline');
      }
    };

    fetchStatus();
    const interval = setInterval(() => {
      if (status?.status !== 'COMPLETED' && status?.status !== 'FAILED') {
        fetchStatus();
      }
    }, 1200);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [currentJobId, status?.status]);

  if (!currentJobId) {
    return (
      <div className="p-8 text-center bg-slate-850 rounded-2xl border border-slate-800 text-slate-400">
        No active analysis selected. Please upload an A360 package to begin.
      </div>
    );
  }

  const currentStageIndex = STAGES.findIndex((s) => s.stage === status?.current_stage);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header card with progress bar */}
      <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 shadow-md">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-primary-400 uppercase tracking-wider">
              Real-Time Analysis Pipeline
            </span>
            <h2 className="text-lg font-bold text-slate-100 mt-1">
              {status?.status === 'COMPLETED'
                ? 'Migration Analysis Ready'
                : status?.status === 'FAILED'
                ? 'Analysis Failed'
                : 'Processing A360 Package...'}
            </h2>
          </div>
          <div className="text-right">
            <div className="text-2xl font-black text-primary-400 font-mono">
              {status?.progress_percentage ?? 0}%
            </div>
            <div className="text-xs text-slate-400">
              Stage {Math.max(1, currentStageIndex + 1)} of {STAGES.length}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-2.5 bg-slate-800 rounded-full mt-4 overflow-hidden border border-slate-700/50">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              status?.status === 'FAILED'
                ? 'bg-rose-500'
                : 'bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-400'
            }`}
            style={{ width: `${status?.progress_percentage ?? 8}%` }}
          />
        </div>

        {/* Error notice */}
        {status?.error_message && (
          <div className="mt-4 p-3 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{status.error_message}</span>
          </div>
        )}

        {/* Post-Completion Action buttons */}
        {status?.status === 'COMPLETED' && (
          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center gap-3">
            <button
              onClick={() => setActiveTab('dashboard')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-md shadow-primary-500/20 transition-all"
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>View Dashboard</span>
            </button>
            <button
              onClick={() => setActiveTab('workflow')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-xs font-semibold transition-all"
            >
              <GitFork className="w-4 h-4 text-purple-400" />
              <span>Explore Interactive Flow</span>
            </button>
            <button
              onClick={() => setActiveTab('migration')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-xs font-semibold transition-all ml-auto"
            >
              <span>Target Blueprint</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* 13 Stage Step List */}
      <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-3">
        {STAGES.map((s, idx) => {
          const isDone =
            status?.status === 'COMPLETED' ||
            (currentStageIndex !== -1 && idx < currentStageIndex);
          const isCurrent =
            status?.status === 'PROCESSING' && idx === currentStageIndex;

          return (
            <div
              key={s.stage}
              className={`flex items-start gap-4 p-3 rounded-xl border transition-all ${
                isDone
                  ? 'bg-slate-900/60 border-slate-800/80 text-slate-300'
                  : isCurrent
                  ? 'bg-primary-500/10 border-primary-500/30 text-white shadow-sm'
                  : 'bg-slate-900/20 border-slate-850 text-slate-500'
              }`}
            >
              <div className="pt-0.5">
                {isDone ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-600" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-xs">{s.label}</span>
                  {isCurrent && (
                    <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-primary-500/20 text-primary-400 animate-pulse">
                      In Progress
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5">{s.desc}</p>
              </div>
              <div className="text-[11px] font-mono text-slate-500">
                Step {idx + 1}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
