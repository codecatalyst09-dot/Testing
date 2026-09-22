import React, { useState } from 'react';
import { TaskModel, DependencyModel } from '../types/workflow';
import {
  FolderTree,
  FileCode,
  Layers,
  ArrowRight,
  Database,
  Globe,
  Lock,
  FileSpreadsheet,
  FileText,
  Monitor,
  CheckCircle2,
} from 'lucide-react';

interface DependencyTreeProps {
  tasks: TaskModel[];
  dependencies: DependencyModel[];
}

export const DependencyTree: React.FC<DependencyTreeProps> = ({ tasks, dependencies }) => {
  const [selectedTask, setSelectedTask] = useState<TaskModel | null>(tasks[0] || null);

  const getDepIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'application':
      case 'desktop software':
        return <FileSpreadsheet className="w-4 h-4 text-purple-400" />;
      case 'browser':
        return <Globe className="w-4 h-4 text-blue-400" />;
      case 'api':
        return <Globe className="w-4 h-4 text-emerald-400" />;
      case 'database':
        return <Database className="w-4 h-4 text-amber-400" />;
      case 'credential':
        return <Lock className="w-4 h-4 text-rose-400" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top: Task Hierarchy and Subtask Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Taskbot Hierarchy Tree */}
        <div className="p-5 rounded-2xl bg-slate-850 border border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <FolderTree className="w-5 h-5 text-primary-400" />
            <h3 className="text-sm font-bold text-white">Taskbot Hierarchy Tree</h3>
          </div>

          <div className="space-y-2">
            {tasks.map((task) => {
              const isSelected = selectedTask?.id === task.id;
              return (
                <div
                  key={task.id}
                  onClick={() => setSelectedTask(task)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-primary-500/15 border-primary-500 text-white shadow-sm'
                      : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/80'
                  } ${task.parentTask ? 'ml-6' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileCode className={`w-4 h-4 ${task.isMain ? 'text-blue-400' : 'text-purple-400'}`} />
                      <span className="font-semibold text-xs font-mono">{task.name}</span>
                    </div>
                    {task.isMain && (
                      <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                        Main Taskbot
                      </span>
                    )}
                  </div>

                  <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-400">
                    <span>{task.stepsCount} steps</span>
                    <span className="capitalize">{task.cloudOrDesktop}</span>
                  </div>

                  {task.subtasks.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500 flex items-center gap-1">
                      <span>Calls:</span>
                      <span className="text-slate-300 font-mono">{task.subtasks.join(', ')}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Selected Task Details */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-850 border border-slate-800 shadow-sm space-y-4">
          <div className="pb-3 border-b border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs font-mono font-bold text-slate-400">
                {selectedTask?.isMain ? 'Main Taskbot' : 'Modular Subtask'}
              </span>
              <h3 className="text-base font-bold text-white mt-0.5">{selectedTask?.name}</h3>
            </div>
            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-200 border border-slate-700">
              {selectedTask?.cloudOrDesktop}
            </span>
          </div>

          {selectedTask && (
            <div className="space-y-4 text-xs">
              <div>
                <span className="font-semibold text-slate-400 uppercase tracking-wider text-[11px] block mb-1">
                  Business Purpose
                </span>
                <p className="text-slate-200 leading-relaxed p-3 rounded-xl bg-slate-900 border border-slate-800">
                  {selectedTask.purpose}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="font-semibold text-slate-400 uppercase tracking-wider text-[11px] block mb-1">
                    Migration Target
                  </span>
                  <p className="text-emerald-400 font-semibold">{selectedTask.migrationStrategy}</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="font-semibold text-slate-400 uppercase tracking-wider text-[11px] block mb-1">
                    Action Volume
                  </span>
                  <p className="text-slate-200 font-bold">{selectedTask.stepsCount} RPA Steps</p>
                </div>
              </div>

              {selectedTask.subtasks.length > 0 && (
                <div>
                  <span className="font-semibold text-slate-400 uppercase tracking-wider text-[11px] block mb-2">
                    Child Subtasks Dispatched
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {selectedTask.subtasks.map((sub, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 font-mono"
                      >
                        <ArrowRight className="w-3.5 h-3.5 text-primary-400" />
                        <span>{sub}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* External Dependencies Section */}
      <div className="p-5 rounded-2xl bg-slate-850 border border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            <h3 className="text-sm font-bold text-white">External System Dependencies ({dependencies.length})</h3>
          </div>
          <p className="text-xs text-slate-400">Prerequisites required on Power Automate runners and cloud tenant</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dependencies.map((dep, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-slate-800 border border-slate-700">
                    {getDepIcon(dep.type)}
                  </div>
                  <span className="font-bold text-xs text-white">{dep.name}</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  {dep.type}
                </span>
              </div>

              <p className="text-xs text-slate-400 leading-normal">{dep.description}</p>

              <div className="pt-2 border-t border-slate-800/80">
                <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                  Power Automate Solution
                </span>
                <p className="text-[11px] font-medium text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                  <span>{dep.suggestedPAMechanism}</span>
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
