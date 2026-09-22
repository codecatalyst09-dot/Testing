import React from 'react';
import { useJob } from '../context/JobContext';
import { Cpu, PlusCircle, Layers, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { currentJob, currentJobId, jobsList, setCurrentJobId, activeTab, setActiveTab } = useJob();

  const getStatusBadge = () => {
    if (!currentJob) return null;
    switch (currentJob.status) {
      case 'COMPLETED':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Analyzed
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/30 animate-pulse">
            <Clock className="w-3.5 h-3.5" />
            Processing
          </span>
        );
      case 'FAILED':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            Failed
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/95 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand */}
      <div
        onClick={() => setActiveTab(currentJobId ? 'dashboard' : 'upload')}
        className="flex items-center gap-3 cursor-pointer select-none"
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-teal-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <Cpu className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base text-white tracking-tight">
              A360 → Power Automate
            </span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Migration Tool
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Preprocess • Parse • Map Actions • Excel Blueprint
          </p>
        </div>
      </div>

      {/* Right Controls: Package selector & Upload button */}
      <div className="flex items-center gap-3">
        {jobsList.length > 0 && (
          <div className="flex items-center gap-2 bg-slate-850 border border-slate-800 rounded-xl px-3 py-1.5">
            <Layers className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-400 hidden sm:inline">Package:</span>
            <select
              value={currentJobId || ''}
              onChange={(e) => {
                setCurrentJobId(e.target.value);
                setActiveTab('dashboard');
              }}
              className="bg-transparent text-xs font-medium text-slate-200 outline-none cursor-pointer max-w-[180px] truncate"
            >
              {jobsList.map((j) => (
                <option key={j.job_id} value={j.job_id} className="bg-slate-900 text-slate-200">
                  {j.filename}
                </option>
              ))}
            </select>
          </div>
        )}

        {getStatusBadge()}

        {/* Upload New Package button */}
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all border ${
            activeTab === 'upload'
              ? 'bg-primary-600 text-white border-primary-500 shadow-md shadow-primary-500/25'
              : 'bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white border-slate-750'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          <span>Upload Package</span>
        </button>
      </div>
    </header>
  );
};
