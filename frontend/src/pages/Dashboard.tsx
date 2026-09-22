import React, { useEffect, useState, useMemo } from 'react';
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
  EyeOff,
  Clock,
  Download,
  FileSpreadsheet,
  Search,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
} from 'lucide-react';

interface CombinedStep {
  stepNumber: number;
  status: 'ACTIVE' | 'DISABLED';
  task: string;
  command: string;
  operation: string;
  description: string;
  targetPlatform: string;
  padCategory: string;
  padAction: string;
  cloudAction: string;
  recommendedAction: string;
  parameters: string;
  variablesRead: string;
  variablesWritten: string;
  disabledReason: string;
  notes: string;
}

export const Dashboard: React.FC = () => {
  const { currentJobId, setActiveTab } = useJob();
  const [workflow, setWorkflow] = useState<WorkflowModel | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Table filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'ACTIVE' | 'DISABLED'>('ALL');
  const [platformFilter, setPlatformFilter] = useState<string>('ALL');

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

  // Combine Active and Disabled actions in chronological sequence
  const combinedSteps = useMemo<CombinedStep[]>(() => {
    if (!workflow) return [];

    const list: { sortKey: number; data: CombinedStep }[] = [];

    // Active actions
    (workflow.actions || []).forEach((a) => {
      const attrs = a.attributes || {};
      const paramsList = Object.entries(attrs)
        .filter(([k]) => !['action', 'operation'].includes(k))
        .map(([k, v]) => `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`)
        .join('; ');

      list.push({
        sortKey: a.step,
        data: {
          stepNumber: a.step,
          status: 'ACTIVE',
          task: a.task,
          command: a.aaPackage || a.command,
          operation: a.aaAction || a.operation || 'Execute',
          description: a.aaDescription || '',
          targetPlatform: a.cloudOrDesktop,
          padCategory: a.padCategory || '',
          padAction: a.padAction || '',
          cloudAction: a.cloudAction || '',
          recommendedAction: a.powerAutomateAction,
          parameters: paramsList,
          variablesRead: (a.variablesUsed || []).join(', '),
          variablesWritten: (a.variablesCreated || []).join(', '),
          disabledReason: 'N/A (Active in Flow)',
          notes: a.migrationNotes || a.reason || '',
        },
      });
    });

    // Disabled actions
    (workflow.disabledActions || []).forEach((da) => {
      const attrs = da.attributes || {};
      const paramsList = Object.entries(attrs)
        .filter(([k]) => !['action', 'operation'].includes(k))
        .map(([k, v]) => `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`)
        .join('; ');

      list.push({
        sortKey: da.originalStep,
        data: {
          stepNumber: da.originalStep,
          status: 'DISABLED',
          task: da.task,
          command: da.aaPackage || da.command,
          operation: da.aaAction || da.action || 'Execute',
          description: da.aaDescription || '',
          targetPlatform: da.targetPlatform || 'Power Automate Desktop',
          padCategory: da.padCategory || '',
          padAction: da.padAction || '',
          cloudAction: da.cloudAction || '',
          recommendedAction: da.recommendedAction || da.padAction || 'Disabled Step',
          parameters: paramsList,
          variablesRead: '',
          variablesWritten: '',
          disabledReason: da.reason || 'Action was disabled in A360',
          notes: da.migrationNotes || 'Action was disabled in source A360 bot. Verify requirement before porting.',
        },
      });
    });

    // Sort chronologically
    list.sort((a, b) => a.sortKey - b.sortKey);
    return list.map((item, idx) => ({ ...item.data, stepNumber: idx + 1 }));
  }, [workflow]);

  // Filtered steps
  const filteredSteps = useMemo(() => {
    return combinedSteps.filter((s) => {
      if (statusFilter !== 'ALL' && s.status !== statusFilter) return false;
      if (platformFilter !== 'ALL' && s.targetPlatform !== platformFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const match =
          s.command.toLowerCase().includes(q) ||
          s.operation.toLowerCase().includes(q) ||
          s.recommendedAction.toLowerCase().includes(q) ||
          s.parameters.toLowerCase().includes(q) ||
          s.task.toLowerCase().includes(q) ||
          s.notes.toLowerCase().includes(q);
        if (!match) return false;
      }
      return true;
    });
  }, [combinedSteps, statusFilter, platformFilter, searchQuery]);

  if (!currentJobId) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-primary-500/15 border border-primary-500/30 flex items-center justify-center mx-auto text-primary-400">
          <Layers className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-white">No Automation Package Selected</h2>
        <p className="text-xs text-slate-400">
          Upload an Automation Anywhere A360 .zip or .json package to begin automated preprocessing, parsing, and Excel migration generation.
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
        <span>Loading preprocessing and migration mapping data...</span>
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
  const totalStepsEvaluated = s.totalStepsEvaluated || combinedSteps.length;
  const complexity = s.migrationComplexity || (totalStepsEvaluated > 400 ? 'Hard' : totalStepsEvaluated >= 200 ? 'Medium' : 'Easy');

  // Complexity styling
  const complexityBadge = {
    Easy: {
      label: 'EASY MIGRATION',
      rule: '< 200 Total Steps',
      badgeClass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      bannerBg: 'from-emerald-950/40 via-slate-900 to-slate-900 border-emerald-500/30',
      desc: 'Low step volume. Suitable for direct conversion into Power Automate Flows.',
    },
    Medium: {
      label: 'MEDIUM MIGRATION',
      rule: '200 to 400 Total Steps',
      badgeClass: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      bannerBg: 'from-amber-950/40 via-slate-900 to-slate-900 border-amber-500/30',
      desc: 'Moderate step volume. Recommended modular division between Cloud Flows and Desktop Flows.',
    },
    Hard: {
      label: 'HARD MIGRATION',
      rule: '> 400 Total Steps',
      badgeClass: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
      bannerBg: 'from-rose-950/40 via-slate-900 to-slate-900 border-rose-500/30',
      desc: 'High step volume. Complex enterprise workflow requiring phased decomposition and queue decoupling.',
    },
  }[complexity] || {
    label: 'EASY MIGRATION',
    rule: '< 200 Steps',
    badgeClass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    bannerBg: 'from-emerald-950/40 via-slate-900 to-slate-900 border-emerald-500/30',
    desc: 'Low step volume.',
  };

  return (
    <div className="space-y-6">
      {/* 1. Top Executive Banner with Migration Complexity & Direct Download */}
      <div className={`p-6 rounded-2xl bg-gradient-to-r ${complexityBadge.bannerBg} border flex flex-wrap items-center justify-between gap-6 shadow-xl`}>
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border ${complexityBadge.badgeClass} flex items-center gap-1.5`}>
              <Sparkles className="w-3.5 h-3.5" />
              {complexityBadge.label}
            </span>
            <span className="text-xs font-mono text-slate-400">
              Rule: {complexityBadge.rule}
            </span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">
            {workflow.workflow.name}
          </h1>
          <p className="text-xs text-slate-300">
            {complexityBadge.desc} Evaluated <strong className="text-white">{totalStepsEvaluated} total steps</strong> (
            <span className="text-emerald-400 font-semibold">{s.totalActions} Active</span>,{' '}
            <span className="text-amber-400 font-semibold">{s.totalDisabledActions} Disabled</span>). Mapped with 274 reference actions.
          </p>
        </div>

        {/* Primary Download Action */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <a
            href={api.getDownloadExcelUrl(currentJobId)}
            download="AA_to_PowerAutomate_Migration_Plan.xlsx"
            className="flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition-all border border-emerald-400/30 hover:scale-[1.02] active:scale-[0.98]"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Download Migration Excel (.xlsx)</span>
          </a>
          <a
            href={api.getDownloadBundleUrl(currentJobId)}
            download
            className="flex items-center justify-center gap-2 px-4 py-3.5 rounded-xl bg-slate-800/90 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 font-semibold text-xs transition-all"
          >
            <Download className="w-4 h-4" />
            <span>All Artifacts (.zip)</span>
          </a>
        </div>
      </div>

      {/* 2. Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Evaluated Steps"
          value={totalStepsEvaluated}
          subtitle={`Complexity: ${complexity}`}
          icon={Activity}
          colorTheme="blue"
        />
        <StatCard
          title="Active Actions"
          value={s.totalActions}
          subtitle="Ready for production flow"
          icon={CheckCircle2}
          colorTheme="emerald"
        />
        <StatCard
          title="Disabled Actions"
          value={s.totalDisabledActions}
          subtitle="Preserved with reasons"
          icon={EyeOff}
          colorTheme="amber"
        />
        <StatCard
          title="Target Platform Split"
          value={`${s.desktopActions} PAD / ${s.cloudActions} Cloud`}
          subtitle={`${s.hybridActions} Hybrid Bridge`}
          icon={GitMerge}
          colorTheme="purple"
        />
      </div>

      {/* 3. Definitive Step-by-Step Mapping Table */}
      <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>Step-by-Step A360 → Power Automate Action Mapping</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Exact replica of the downloaded Excel blueprint. Ready for downstream migration agent execution.
            </p>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-2.5">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search action, package, param..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-750 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 w-48 sm:w-60"
              />
            </div>

            {/* Status Filter */}
            <div className="flex items-center bg-slate-900 rounded-lg p-0.5 border border-slate-750 text-xs">
              <button
                onClick={() => setStatusFilter('ALL')}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  statusFilter === 'ALL' ? 'bg-primary-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                All ({combinedSteps.length})
              </button>
              <button
                onClick={() => setStatusFilter('ACTIVE')}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  statusFilter === 'ACTIVE' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Active ({s.totalActions})
              </button>
              <button
                onClick={() => setStatusFilter('DISABLED')}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  statusFilter === 'DISABLED' ? 'bg-amber-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Disabled ({s.totalDisabledActions})
              </button>
            </div>

            {/* Platform Filter */}
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-750 text-xs text-slate-300 focus:outline-none focus:border-primary-500"
            >
              <option value="ALL">All Platforms</option>
              <option value="Power Automate Desktop">Power Automate Desktop</option>
              <option value="Power Automate Cloud">Power Automate Cloud</option>
              <option value="Hybrid">Hybrid</option>
              <option value="Manual Review">Manual Review</option>
            </select>
          </div>
        </div>

        {/* Table View */}
        <div className="overflow-x-auto rounded-xl border border-slate-750">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-900 text-slate-300 border-b border-slate-750 font-semibold">
                <th className="py-3 px-3 w-14 text-center">Step #</th>
                <th className="py-3 px-3 w-24 text-center">Status</th>
                <th className="py-3 px-4 w-44">AA Package & Action</th>
                <th className="py-3 px-3 w-40 text-center">Target Platform</th>
                <th className="py-3 px-4 w-52">Recommended PA Action</th>
                <th className="py-3 px-4 min-w-[220px]">Parameters & Variables</th>
                <th className="py-3 px-4 min-w-[200px]">Migration Guidance & Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredSteps.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No steps match the active filters.
                  </td>
                </tr>
              ) : (
                filteredSteps.map((step) => {
                  const isDisabled = step.status === 'DISABLED';
                  return (
                    <tr
                      key={`${step.stepNumber}-${step.command}-${step.operation}`}
                      className={`hover:bg-slate-800/40 transition-colors ${
                        isDisabled ? 'bg-amber-950/10' : ''
                      }`}
                    >
                      {/* Step Number */}
                      <td className="py-3 px-3 text-center font-mono font-bold text-slate-400">
                        {step.stepNumber}
                      </td>

                      {/* Status */}
                      <td className="py-3 px-3 text-center">
                        {isDisabled ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-rose-500/20 text-rose-400 border border-rose-500/30">
                            <EyeOff className="w-3 h-3" />
                            Disabled
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            <CheckCircle2 className="w-3 h-3" />
                            Active
                          </span>
                        )}
                      </td>

                      {/* AA Package & Action */}
                      <td className="py-3 px-4">
                        <div className="font-bold text-white flex items-center gap-1.5">
                          <span>{step.command}</span>
                          <span className="text-slate-500">›</span>
                          <span className="text-primary-300 font-mono">{step.operation}</span>
                        </div>
                        {step.description && (
                          <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                            {step.description}
                          </p>
                        )}
                        <span className="text-[10px] text-slate-500">Task: {step.task}</span>
                      </td>

                      {/* Target Platform */}
                      <td className="py-3 px-3 text-center">
                        <span
                          className={`inline-block px-2.5 py-1 rounded-lg text-[11px] font-semibold border ${
                            step.targetPlatform === 'Power Automate Cloud'
                              ? 'bg-blue-500/15 text-blue-300 border-blue-500/30'
                              : step.targetPlatform === 'Power Automate Desktop'
                              ? 'bg-purple-500/15 text-purple-300 border-purple-500/30'
                              : step.targetPlatform === 'Hybrid'
                              ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                              : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                          }`}
                        >
                          {step.targetPlatform === 'Power Automate Desktop' ? 'Desktop (PAD)' : step.targetPlatform === 'Power Automate Cloud' ? 'Cloud Flow' : step.targetPlatform}
                        </span>
                      </td>

                      {/* Recommended PA Action */}
                      <td className="py-3 px-4">
                        <div className="font-semibold text-slate-200">
                          {step.recommendedAction}
                        </div>
                        {step.padCategory && (
                          <span className="text-[10px] text-slate-400">
                            PAD Category: {step.padCategory}
                          </span>
                        )}
                      </td>

                      {/* Parameters & Variables */}
                      <td className="py-3 px-4">
                        {step.parameters ? (
                          <div className="font-mono text-[11px] text-slate-300 bg-slate-900/80 px-2 py-1 rounded border border-slate-800 max-h-16 overflow-y-auto">
                            {step.parameters}
                          </div>
                        ) : (
                          <span className="text-slate-500 text-[11px]">No custom attributes</span>
                        )}
                        {(step.variablesRead || step.variablesWritten) && (
                          <div className="flex flex-wrap gap-2 text-[10px] mt-1 text-slate-400">
                            {step.variablesRead && <span>Read: <code className="text-blue-300">{step.variablesRead}</code></span>}
                            {step.variablesWritten && <span>Write: <code className="text-emerald-300">{step.variablesWritten}</code></span>}
                          </div>
                        )}
                      </td>

                      {/* Migration Guidance & Notes */}
                      <td className="py-3 px-4">
                        {isDisabled && step.disabledReason && (
                          <p className="text-[11px] text-amber-400 font-medium mb-1">
                            ⚠️ {step.disabledReason}
                          </p>
                        )}
                        <p className="text-[11px] text-slate-300">
                          {step.notes || 'Standard 1-to-1 migration equivalent.'}
                        </p>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Table Footer Count & Summary */}
        <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
          <span>
            Showing <strong className="text-white">{filteredSteps.length}</strong> of{' '}
            <strong className="text-white">{combinedSteps.length}</strong> total evaluated steps
          </span>
          <a
            href={api.getDownloadExcelUrl(currentJobId)}
            className="text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 hover:underline"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Download All in Formatted Excel (.xlsx)</span>
          </a>
        </div>
      </div>
    </div>
  );
};
