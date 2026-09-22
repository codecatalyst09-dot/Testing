import React from 'react';
import { useJob } from '../context/JobContext';
import {
  LayoutDashboard,
  UploadCloud,
  Activity,
  GitFork,
  ListTree,
  Braces,
  EyeOff,
  FolderTree,
  Compass,
  FileText,
  DownloadCloud,
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab, currentJob } = useJob();

  const navItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload Package', icon: UploadCloud },
    {
      id: 'analysis',
      label: 'Pipeline Tracker',
      icon: Activity,
      badge: currentJob?.status === 'PROCESSING' ? `${currentJob.progress_percentage}%` : undefined
    },
    { id: 'workflow', label: 'Interactive Flow', icon: GitFork },
    { id: 'actions', label: 'Action Explorer', icon: ListTree },
    { id: 'variables', label: 'Variables', icon: Braces },
    { id: 'disabled', label: 'Disabled Actions', icon: EyeOff },
    { id: 'dependencies', label: 'Dependencies', icon: FolderTree },
    { id: 'migration', label: 'Target Architecture', icon: Compass },
    { id: 'reports', label: 'Migration Reports', icon: FileText },
    { id: 'downloads', label: 'Download Center', icon: DownloadCloud },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between shrink-0">
      <div className="py-4">
        <div className="px-4 mb-3 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
          Navigation
        </div>
        <nav className="space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-primary-600/15 text-primary-400 font-semibold border border-primary-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-primary-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-400 animate-pulse">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Package / Migration Target Indicator */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
          Target Environment
        </div>
        <div className="p-2.5 rounded-lg bg-slate-850 border border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-slate-200 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Power Automate Cloud & Desktop
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Microsoft Power Platform 2026+</p>
        </div>
      </div>
    </aside>
  );
};
