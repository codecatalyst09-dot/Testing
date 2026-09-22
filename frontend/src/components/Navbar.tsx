import React from 'react';
import { useJob } from '../context/JobContext';
import { Search, UploadCloud, Cpu, CheckCircle2, Clock, AlertTriangle, Layers } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { currentJob, currentJobId, jobsList, setCurrentJobId, setSearchModalOpen, setActiveTab } = useJob();

  const getStatusBadge = () => {
    if (!currentJob) return null;
    switch (currentJob.status) {
      case 'COMPLETED':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Analyzed
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/30 animate-pulse">
            <Clock className="w-3.5 h-3.5" />
            Analyzing ({currentJob.progress_percentage}%)
          </span>
        );
      case 'FAILED':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            Failed
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <Clock className="w-3.5 h-3.5" />
            Pending
          </span>
        );
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <Cpu className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base text-white tracking-tight">A360 → Power Automate</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
              Enterprise
            </span>
          </div>
          <p className="text-xs text-slate-400">RPA Modernization & Migration Analyzer</p>
        </div>
      </div>

      {/* Middle: Active Job Selector & Status */}
      <div className="flex items-center gap-3">
        {jobsList.length > 0 && (
          <div className="flex items-center gap-2 bg-slate-850 border border-slate-800 rounded-lg px-3 py-1.5">
            <Layers className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-400">Package:</span>
            <select
              value={currentJobId || ''}
              onChange={(e) => setCurrentJobId(e.target.value)}
              className="bg-transparent text-xs font-medium text-slate-200 outline-none cursor-pointer max-w-[200px] truncate"
            >
              {jobsList.map((j) => (
                <option key={j.job_id} value={j.job_id} className="bg-slate-900 text-slate-200">
                  {j.filename} ({j.job_id.slice(0, 6)})
                </option>
              ))}
            </select>
          </div>
        )}
        {getStatusBadge()}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Global Search Button */}
        <button
          onClick={() => setSearchModalOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 text-xs transition-colors"
          title="Search anything across actions, variables, tasks (Ctrl+K)"
        >
          <Search className="w-4 h-4" />
          <span className="hidden sm:inline">Search...</span>
          <kbd className="hidden sm:inline px-1.5 py-0.5 text-[10px] bg-slate-800 rounded border border-slate-700 text-slate-400">
            Ctrl K
          </kbd>
        </button>

        {/* Upload Button */}
        <button
          onClick={() => setActiveTab('upload')}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-md shadow-primary-500/20 transition-all hover:shadow-primary-500/30"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload Package</span>
        </button>
      </div>
    </header>
  );
};
