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
  Bot,
  Network,
  ArrowRight,
  Code2,
  Copy,
  Check,
  FileCode,
  Terminal,
  X,
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
  const [taskFilter, setTaskFilter] = useState<string>('ALL');

  // Code Generation Modal States
  const [showCodeModal, setShowCodeModal] = useState<boolean>(false);
  const [codeLoading, setCodeLoading] = useState<boolean>(false);
  const [generatedCode, setGeneratedCode] = useState<any>(null);
  const [activeCodeTab, setActiveCodeTab] = useState<'pad' | 'cloud' | 'ps1'>('pad');
  const [copied, setCopied] = useState<boolean>(false);

  const handleOpenCodeModal = async () => {
    if (!currentJobId) return;
    if (workflow?.botCentricity === 'Cloud-Centric') {
      setActiveCodeTab('cloud');
    } else {
      setActiveCodeTab('pad');
    }
    setShowCodeModal(true);
    if (!generatedCode) {
      setCodeLoading(true);
      try {
        const data = await api.getGeneratedCode(currentJobId);
        setGeneratedCode(data);
        if (data?.bot_centricity === 'Cloud-Centric') {
          setActiveCodeTab('cloud');
        }
      } catch (err: any) {
        console.error('Failed to generate code:', err);
      } finally {
        setCodeLoading(false);
      }
    }
  };

  const handleCopyCode = () => {
    if (!generatedCode) return;
    let textToCopy = '';
    if (activeCodeTab === 'pad') {
      textToCopy = generatedCode.pad_script || '';
    } else if (activeCodeTab === 'cloud') {
      textToCopy = JSON.stringify(generatedCode.cloud_flow_json, null, 2);
    } else {
      textToCopy = generatedCode.powershell_script || '';
    }
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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
      if (taskFilter !== 'ALL' && s.task !== taskFilter) return false;
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
  }, [combinedSteps, statusFilter, platformFilter, taskFilter, searchQuery]);

  // Sub-bots and Rough Idea Overview
  const subBotsOverview = useMemo(() => {
    if (!workflow) return null;
    if (workflow.explanation) return workflow.explanation;

    const mainTask = workflow.tasks?.find((t) => t.isMain) || (workflow.tasks && workflow.tasks[0]);
    const mainName = mainTask ? mainTask.name : 'MainTask';
    const subTasks = (workflow.tasks || []).filter((t) => t.name !== mainName);
    const hasSubBots = subTasks.length > 0;

    return {
      rough_idea: hasSubBots
        ? `Multi-Bot Process: The main orchestrator '${mainName}' coordinates ${subTasks.length} dedicated sub-bot(s) across ${workflow.statistics.totalActions} total steps.`
        : `Standalone Automation: '${mainName}' operates as an independent single taskbot executing ${workflow.statistics.totalActions} sequential steps without child sub-bots.`,
      has_sub_bots: hasSubBots,
      sub_bot_count: subTasks.length,
      main_bot_name: mainName,
      sub_bots: subTasks.map((t) => ({
        name: t.name,
        purpose: t.purpose,
        steps: t.stepsCount,
        platform: t.cloudOrDesktop === 'Desktop' ? 'Power Automate Desktop' : t.cloudOrDesktop === 'Cloud' ? 'Power Automate Cloud' : 'Hybrid',
        called_by: t.parentTask || mainName,
      })),
      architecture_recommendation: hasSubBots
        ? `Deploy '${mainName}' as a parent Cloud Flow (or Master Desktop Flow) that manages process state and triggers child subflows.`
        : `Migrate '${mainName}' as a single consolidated Power Automate Flow.`,
      ai_enhanced: false,
    };
  }, [workflow]);

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
          <div className="flex flex-wrap items-center gap-2.5">
            <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border ${complexityBadge.badgeClass} flex items-center gap-1.5`}>
              <Sparkles className="w-3.5 h-3.5" />
              {complexityBadge.label}
            </span>
            {workflow.botCentricity && (
              <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border flex items-center gap-1.5 ${
                workflow.botCentricity === 'Desktop-Centric'
                  ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40 shadow-sm shadow-indigo-500/20'
                  : workflow.botCentricity === 'Cloud-Centric'
                  ? 'bg-sky-500/20 text-sky-300 border-sky-500/40 shadow-sm shadow-sky-500/20'
                  : 'bg-purple-500/20 text-purple-300 border-purple-500/40 shadow-sm shadow-purple-500/20'
              }`}>
                {workflow.botCentricity === 'Desktop-Centric' ? (
                  <Monitor className="w-3.5 h-3.5 text-indigo-400" />
                ) : workflow.botCentricity === 'Cloud-Centric' ? (
                  <Cloud className="w-3.5 h-3.5 text-sky-400" />
                ) : (
                  <Network className="w-3.5 h-3.5 text-purple-400" />
                )}
                <span>{workflow.botCentricity}</span>
              </span>
            )}
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

        {/* Primary Code Generation & Download Actions */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <button
            onClick={handleOpenCodeModal}
            className="flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-primary-600 hover:from-violet-500 hover:via-indigo-500 hover:to-primary-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all border border-indigo-400/40 hover:scale-[1.02] active:scale-[0.98] group"
          >
            <Code2 className="w-4 h-4 text-violet-200 group-hover:rotate-12 transition-transform" />
            <span>Generate Code</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-white/20 text-white uppercase font-extrabold tracking-wider">
              {workflow?.botCentricity === 'Cloud-Centric' ? 'Cloud Flow' : 'PAD & Cloud'}
            </span>
          </button>
          <a
            href={api.getDownloadExcelUrl(currentJobId)}
            download="AA_to_PowerAutomate_Migration_Plan.xlsx"
            className="flex items-center justify-center gap-2.5 px-5 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition-all border border-emerald-400/30 hover:scale-[1.02] active:scale-[0.98]"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Download Excel</span>
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

      {/* 2. Automation Overview & Multi-Bot Architecture Panel */}
      {subBotsOverview && (
        <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 shadow-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-primary-500/10 text-primary-400 border border-primary-500/20">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  Automation Overview & Multi-Bot Architecture
                  {subBotsOverview.ai_enhanced && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> GPT-4.1 Powered
                    </span>
                  )}
                </h3>
                <p className="text-[11px] text-slate-400">
                  {subBotsOverview.has_sub_bots
                    ? `Hierarchical Multi-Bot Process: 1 Main Orchestrator + ${subBotsOverview.sub_bot_count} Specialized Sub-Bots`
                    : 'Standalone Single Taskbot: Self-contained business process'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${
                subBotsOverview.has_sub_bots
                  ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                  : 'bg-blue-500/15 text-blue-300 border-blue-500/30'
              }`}>
                {subBotsOverview.has_sub_bots
                  ? `${subBotsOverview.sub_bot_count} Sub-Bots Detected`
                  : 'Single Taskbot'}
              </span>
            </div>
          </div>

          {/* Rough Idea Description */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800/80">
            <h4 className="text-[11px] uppercase tracking-wider font-bold text-slate-400 mb-1.5 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-primary-400" />
              Process Overview & Rough Idea
            </h4>
            <p className="text-xs text-slate-200 leading-relaxed">
              {subBotsOverview.rough_idea}
            </p>
          </div>

          {/* Centricity Architecture Insight */}
          {workflow.botCentricity && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start gap-3.5">
              <div className={`p-2.5 rounded-xl shrink-0 border ${
                workflow.botCentricity === 'Desktop-Centric'
                  ? 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30'
                  : workflow.botCentricity === 'Cloud-Centric'
                  ? 'bg-sky-500/15 text-sky-400 border-sky-500/30'
                  : 'bg-purple-500/15 text-purple-400 border-purple-500/30'
              }`}>
                {workflow.botCentricity === 'Desktop-Centric' ? (
                  <Monitor className="w-4 h-4" />
                ) : workflow.botCentricity === 'Cloud-Centric' ? (
                  <Cloud className="w-4 h-4" />
                ) : (
                  <Network className="w-4 h-4" />
                )}
              </div>
              <div className="space-y-1">
                <div className="text-xs font-bold text-white flex items-center gap-2">
                  <span>Runtime Architecture Affinity:</span>
                  <span className={`px-2 py-0.5 rounded text-[11px] font-extrabold uppercase tracking-wide border ${
                    workflow.botCentricity === 'Desktop-Centric'
                      ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30'
                      : workflow.botCentricity === 'Cloud-Centric'
                      ? 'bg-sky-500/20 text-sky-300 border-sky-500/30'
                      : 'bg-purple-500/20 text-purple-300 border-purple-500/30'
                  }`}>
                    {workflow.botCentricity}
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                    Actions Harmonized
                  </span>
                </div>
                <p className="text-[11px] text-slate-300 leading-relaxed">
                  {workflow.botCentricityReason || (
                    workflow.botCentricity === 'Desktop-Centric'
                      ? 'Local desktop dependencies detected. All compatible loops, conditionals, strings, and variables are harmonized to native Power Automate Desktop actions to avoid cloud-desktop context switching.'
                      : 'Serverless cloud flow. All compatible actions are harmonized to native Power Automate Cloud connectors and expressions.'
                  )}
                </p>
              </div>
            </div>
          )}

          {/* Sub-Bots Breakdown (if multiple bots) */}
          {subBotsOverview.has_sub_bots && (
            <div className="space-y-2 pt-1">
              <div className="flex items-center justify-between">
                <h4 className="text-[11px] uppercase tracking-wider font-bold text-slate-400 flex items-center gap-1.5">
                  <Network className="w-3.5 h-3.5 text-amber-400" />
                  Sub-Bot Breakdown & Call Hierarchy
                </h4>
                <span className="text-[11px] text-slate-500">
                  Click a bot card to filter the actions table below
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                {/* Main Bot Card */}
                <div
                  onClick={() => setTaskFilter(taskFilter === subBotsOverview.main_bot_name ? 'ALL' : subBotsOverview.main_bot_name)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer hover:scale-[1.02] space-y-2 ${
                    taskFilter === subBotsOverview.main_bot_name
                      ? 'bg-primary-600/20 border-primary-400 shadow-md shadow-primary-500/20'
                      : 'bg-primary-950/20 border-primary-500/30 hover:border-primary-400'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-primary-500/20 text-primary-300 border border-primary-500/40">
                      Main Bot
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">Orchestrator</span>
                  </div>
                  <div className="font-bold text-xs text-white truncate" title={subBotsOverview.main_bot_name}>
                    {subBotsOverview.main_bot_name}
                  </div>
                  <div className="text-[11px] text-slate-400 line-clamp-1">
                    Coordinates {subBotsOverview.sub_bot_count} sub-bots
                  </div>
                </div>

                {/* Child Sub-Bots Cards */}
                {subBotsOverview.sub_bots.map((sub) => {
                  const isSelected = taskFilter === sub.name;
                  return (
                    <div
                      key={sub.name}
                      onClick={() => setTaskFilter(isSelected ? 'ALL' : sub.name)}
                      className={`p-3.5 rounded-xl border transition-all cursor-pointer hover:scale-[1.02] space-y-2 ${
                        isSelected
                          ? 'bg-amber-600/20 border-amber-400 shadow-md shadow-amber-500/20'
                          : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                          Sub-Bot
                        </span>
                        <span className="text-[10px] text-emerald-400 font-mono">
                          {sub.steps} steps
                        </span>
                      </div>
                      <div className="font-bold text-xs text-slate-200 truncate" title={sub.name}>
                        {sub.name}
                      </div>
                      <div className="text-[11px] text-slate-400 line-clamp-1" title={sub.purpose}>
                        {sub.purpose}
                      </div>
                      <div className="pt-1 flex items-center justify-between text-[10px]">
                        <span className="text-slate-500">Target:</span>
                        <span className="font-medium text-slate-300">
                          {sub.platform === 'Power Automate Desktop' ? 'Desktop (PAD)' : sub.platform === 'Power Automate Cloud' ? 'Cloud Flow' : 'Hybrid'}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

        </div>
      )}

      {/* 3. Key Metrics Grid */}
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

            {/* Task Filter */}
            {workflow.tasks && workflow.tasks.length > 1 && (
              <select
                value={taskFilter}
                onChange={(e) => setTaskFilter(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-750 text-xs text-slate-300 focus:outline-none focus:border-primary-500"
              >
                <option value="ALL">All Tasks ({workflow.tasks.length})</option>
                {workflow.tasks.map((t) => (
                  <option key={t.name} value={t.name}>
                    {t.name} {t.isMain ? '(Main Orchestrator)' : '(Sub-Bot)'}
                  </option>
                ))}
              </select>
            )}
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

      {/* 4. Code Generation Modal */}
      {showCodeModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-fadeIn">
          <div className="bg-slate-900 border border-slate-750 rounded-2xl w-full max-w-5xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-850">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-violet-500/15 border border-violet-500/30 text-violet-400">
                  <Code2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-black text-white flex items-center gap-2.5">
                    Power Automate Code Generator
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-500/20 text-violet-300 border border-violet-500/30">
                      Deterministic / No-LLM
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Target code blueprints for {workflow.workflow.name} ({workflow.statistics.totalActions} steps)
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <a
                  href={api.getDownloadCodeUrl(currentJobId, 'all')}
                  className="hidden sm:flex items-center gap-2 px-3.5 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-semibold shadow-md shadow-violet-600/20 transition-all"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Code Bundle (.zip)</span>
                </a>
                <button
                  onClick={() => setShowCodeModal(false)}
                  className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex items-center gap-2 px-6 pt-4 bg-slate-900 border-b border-slate-800 text-xs font-semibold">
              <button
                onClick={() => setActiveCodeTab('pad')}
                className={`flex items-center gap-2 px-4 py-2.5 border-b-2 transition-all ${
                  activeCodeTab === 'pad'
                    ? 'border-violet-500 text-violet-400 font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Monitor className="w-4 h-4" />
                <span>Desktop Flow Script (.pad)</span>
                {generatedCode?.summary?.pad_lines && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                    {generatedCode.summary.pad_lines} lines
                  </span>
                )}
              </button>

              <button
                onClick={() => setActiveCodeTab('cloud')}
                className={`flex items-center gap-2 px-4 py-2.5 border-b-2 transition-all ${
                  activeCodeTab === 'cloud'
                    ? 'border-sky-500 text-sky-400 font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Cloud className="w-4 h-4" />
                <span>Cloud Flow Definition (.json)</span>
                {generatedCode?.summary?.cloud_actions_count && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                    {generatedCode.summary.cloud_actions_count} actions
                  </span>
                )}
              </button>

              <button
                onClick={() => setActiveCodeTab('ps1')}
                className={`flex items-center gap-2 px-4 py-2.5 border-b-2 transition-all ${
                  activeCodeTab === 'ps1'
                    ? 'border-emerald-500 text-emerald-400 font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Terminal className="w-4 h-4" />
                <span>PowerShell Deployment (.ps1)</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300">
                  CLI
                </span>
              </button>
            </div>

            {/* Code Body */}
            <div className="flex-1 overflow-hidden flex flex-col p-5 bg-slate-950">
              {/* Code Toolbar */}
              <div className="flex items-center justify-between pb-3 text-xs text-slate-400 border-b border-slate-800/80 mb-3">
                <div className="flex items-center gap-2 font-mono text-[11px] text-slate-300">
                  <FileCode className="w-3.5 h-3.5 text-violet-400" />
                  <span>
                    {activeCodeTab === 'pad'
                      ? `${workflow.workflow.name.replace(/ /g, '_')}_Desktop.pad`
                      : activeCodeTab === 'cloud'
                      ? `${workflow.workflow.name.replace(/ /g, '_')}_CloudFlow.json`
                      : `Deploy_${workflow.workflow.name.replace(/ /g, '_')}.ps1`}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopyCode}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 transition-all hover:scale-105 active:scale-95"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400 font-bold">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy Code</span>
                      </>
                    )}
                  </button>

                  <a
                    href={api.getDownloadCodeUrl(currentJobId, activeCodeTab)}
                    download
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 transition-all hover:scale-105 active:scale-95"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download File</span>
                  </a>
                </div>
              </div>

              {/* Code Pre Container */}
              <div className="flex-1 overflow-auto rounded-xl bg-slate-900/90 border border-slate-800 p-4 text-xs font-mono text-slate-200 leading-relaxed selection:bg-violet-500/30 selection:text-white">
                {codeLoading ? (
                  <div className="p-12 text-center text-slate-400 flex flex-col items-center gap-3">
                    <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
                    <span>Generating native Power Automate code blueprints...</span>
                  </div>
                ) : (
                  <pre className="whitespace-pre">
                    {activeCodeTab === 'pad'
                      ? generatedCode?.pad_script || '# No desktop flow script generated.'
                      : activeCodeTab === 'cloud'
                      ? JSON.stringify(generatedCode?.cloud_flow_json, null, 2)
                      : generatedCode?.powershell_script || '# No deployment script generated.'}
                  </pre>
                )}
              </div>

              {/* Pro-Tips Footer Bar */}
              <div className="mt-3 p-3 rounded-xl bg-violet-950/30 border border-violet-500/20 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2 text-violet-300">
                  <Sparkles className="w-4 h-4 text-violet-400 shrink-0" />
                  <span>
                    {activeCodeTab === 'pad'
                      ? 'Pro-Tip: In Power Automate Desktop designer, press Ctrl+A then Ctrl+V to paste this entire script directly into the flow canvas!'
                      : activeCodeTab === 'cloud'
                      ? 'Pro-Tip: Import this JSON definition into Power Platform Solutions or Logic Apps Designer to deploy cloud orchestrators.'
                      : 'Pro-Tip: Run this PowerShell script with PAC CLI to automatically provision the solution, flows, and connections.'}
                  </span>
                </div>
                <a
                  href={api.getDownloadCodeUrl(currentJobId, 'all')}
                  className="sm:hidden text-violet-400 hover:underline font-semibold"
                >
                  Download .zip
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
