import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { WorkflowModel } from '../types/workflow';
import { StatCard } from '../components/StatCard';
import {
  Layers,
  Activity,
  Cloud,
  Monitor,
  GitMerge,
  AlertTriangle,
  Braces,
  FolderTree,
  EyeOff,
  Clock,
  ArrowRight,
  DownloadCloud,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { currentJobId, setActiveTab } = useJob();
  const [workflow, setWorkflow] = useState<WorkflowModel | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentJobId) return;
    setLoading(true);
    api.getWorkflow(currentJobId)
      .then((data) => {
        setWorkflow(data);
        setError(null);
      })
      .catch((err) => {
        setError(err.message || 'Analysis data not yet available.');
      })
      .finally(() => setLoading(false));
  }, [currentJobId]);

  if (!currentJobId) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-primary-500/15 border border-primary-500/30 flex items-center justify-center mx-auto text-primary-400">
          <Layers className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-white">No Automation Package Selected</h2>
        <p className="text-xs text-slate-400">
          Upload an Automation Anywhere A360 .zip or .json package to begin end-to-end migration analysis.
        </p>
        <button
          onClick={() => setActiveTab('upload')}
          className="px-5 py-2 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-md shadow-primary-500/20"
        >
          Upload Package Now
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-400 text-xs flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        <span>Loading executive dashboard metrics...</span>
      </div>
    );
  }

  if (error || !workflow) {
    return (
      <div className="p-8 max-w-lg mx-auto bg-slate-850 rounded-2xl border border-slate-800 text-center space-y-4">
        <Clock className="w-10 h-10 text-primary-400 mx-auto animate-pulse" />
        <h3 className="text-sm font-bold text-white">Analysis In Progress or Pending</h3>
        <p className="text-xs text-slate-400">
          The selected job is currently running or has not completed all pipeline stages yet.
        </p>
        <button
          onClick={() => setActiveTab('analysis')}
          className="px-4 py-2 rounded-xl bg-primary-600 text-white text-xs font-semibold shadow-sm"
        >
          Track Pipeline Progress
        </button>
      </div>
    );
  }

  const s = workflow.statistics;
  const dist = s.platformDistribution;

  return (
    <div className="space-y-6">
      {/* Top Welcome & Summary Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-850 via-slate-900 to-slate-850 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-primary-400 uppercase tracking-wider">
            Executive Summary
          </span>
          <h1 className="text-2xl font-black text-white mt-1 tracking-tight">
            {workflow.workflow.name}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Source: {workflow.workflow.source} • {s.totalTasks} Taskbot(s) • {s.totalActions} RPA Action Steps
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('workflow')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-lg shadow-primary-500/25 transition-all"
          >
            <span>Interactive Flow Canvas</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => setActiveTab('downloads')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-xs font-semibold transition-all"
          >
            <DownloadCloud className="w-4 h-4" />
            <span>Download Analysis ZIP</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Actions"
          value={s.totalActions}
          subtitle="RPA sequence steps"
          icon={Activity}
          colorTheme="blue"
          onClick={() => setActiveTab('actions')}
        />
        <StatCard
          title="Cloud Actions"
          value={s.cloudActions}
          subtitle={`${dist['Power Automate Cloud'] ?? 0}% serverless`}
          icon={Cloud}
          colorTheme="blue"
          onClick={() => setActiveTab('actions')}
        />
        <StatCard
          title="Desktop Actions"
          value={s.desktopActions}
          subtitle={`${dist['Power Automate Desktop'] ?? 0}% requires PAD`}
          icon={Monitor}
          colorTheme="purple"
          onClick={() => setActiveTab('actions')}
        />
        <StatCard
          title="Hybrid Actions"
          value={s.hybridActions}
          subtitle={`${dist['Hybrid'] ?? 0}% cross-orchestrated`}
          icon={GitMerge}
          colorTheme="amber"
          onClick={() => setActiveTab('actions')}
        />
        <StatCard
          title="Manual Review"
          value={s.manualReviewActions}
          subtitle={`${dist['Manual Review'] ?? 0}% proprietary`}
          icon={AlertTriangle}
          colorTheme={s.manualReviewActions > 0 ? 'rose' : 'emerald'}
          onClick={() => setActiveTab('actions')}
        />
      </div>

      {/* Secondary Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Tasks"
          value={s.totalTasks}
          subtitle="Taskbots in package"
          icon={Layers}
          colorTheme="slate"
          onClick={() => setActiveTab('dependencies')}
        />
        <StatCard
          title="Variables"
          value={s.totalVariables}
          subtitle="Extracted & mapped"
          icon={Braces}
          colorTheme="slate"
          onClick={() => setActiveTab('variables')}
        />
        <StatCard
          title="Subtasks"
          value={s.totalSubtasks}
          subtitle="Modular subflows"
          icon={FolderTree}
          colorTheme="slate"
          onClick={() => setActiveTab('dependencies')}
        />
        <StatCard
          title="Disabled Actions"
          value={s.totalDisabledActions}
          subtitle="Preserved before pruning"
          icon={EyeOff}
          colorTheme={s.totalDisabledActions > 0 ? 'amber' : 'slate'}
          onClick={() => setActiveTab('disabled')}
        />
      </div>

      {/* Platform Distribution Visualizer */}
      <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white">Platform Classification Distribution</h3>
            <p className="text-xs text-slate-400">Architectural allocation for Microsoft Power Platform target</p>
          </div>
          <span className="text-xs font-mono text-slate-400">100% Normalized</span>
        </div>

        {/* Stacked Percentage Bar */}
        <div className="w-full h-4 rounded-full bg-slate-900 overflow-hidden flex border border-slate-800">
          <div
            style={{ width: `${dist['Power Automate Cloud'] ?? 0}%` }}
            className="bg-blue-500 h-full transition-all"
            title={`Cloud: ${dist['Power Automate Cloud'] ?? 0}%`}
          />
          <div
            style={{ width: `${dist['Power Automate Desktop'] ?? 0}%` }}
            className="bg-purple-500 h-full transition-all"
            title={`Desktop: ${dist['Power Automate Desktop'] ?? 0}%`}
          />
          <div
            style={{ width: `${dist['Hybrid'] ?? 0}%` }}
            className="bg-amber-500 h-full transition-all"
            title={`Hybrid: ${dist['Hybrid'] ?? 0}%`}
          />
          <div
            style={{ width: `${dist['Manual Review'] ?? 0}%` }}
            className="bg-rose-500 h-full transition-all"
            title={`Manual Review: ${dist['Manual Review'] ?? 0}%`}
          />
        </div>

        {/* Distribution Legend & Percentages */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-400" />
              <span className="text-slate-300">Cloud Flows</span>
            </div>
            <span className="font-mono font-bold text-xs text-blue-400">
              {dist['Power Automate Cloud'] ?? 0}%
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-400" />
              <span className="text-slate-300">Desktop (PAD)</span>
            </div>
            <span className="font-mono font-bold text-xs text-purple-400">
              {dist['Power Automate Desktop'] ?? 0}%
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
              <span className="text-slate-300">Hybrid Bridge</span>
            </div>
            <span className="font-mono font-bold text-xs text-amber-400">
              {dist['Hybrid'] ?? 0}%
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-400" />
              <span className="text-slate-300">Manual Review</span>
            </div>
            <span className="font-mono font-bold text-xs text-rose-400">
              {dist['Manual Review'] ?? 0}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
