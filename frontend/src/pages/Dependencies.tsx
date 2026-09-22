import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { TaskModel, DependencyModel } from '../types/workflow';
import { DependencyTree } from '../components/DependencyTree';
import { FolderTree } from 'lucide-react';

export const Dependencies: React.FC = () => {
  const { currentJobId } = useJob();
  const [tasks, setTasks] = useState<TaskModel[]>([]);
  const [dependencies, setDependencies] = useState<DependencyModel[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!currentJobId) return;
    setLoading(true);
    Promise.all([api.getTasks(currentJobId), api.getWorkflow(currentJobId)])
      .then(([tasksData, wfData]) => {
        setTasks(tasksData);
        setDependencies(wfData.dependencies);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [currentJobId]);

  return (
    <div className="space-y-4">
      <div className="p-4 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-purple-500/15 text-purple-400 border border-purple-500/30">
            <FolderTree className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Dependencies & Subtask Hierarchy</h1>
            <p className="text-xs text-slate-400">
              Taskbot call trees, modular Run Task relationships, and external infrastructure prerequisites.
            </p>
          </div>
        </div>

        <div className="text-xs text-slate-400 font-mono">
          <strong className="text-white">{tasks.length}</strong> Taskbot(s) • <strong className="text-white">{dependencies.length}</strong> System Dependencies
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading dependencies...</div>
      ) : (
        <DependencyTree tasks={tasks} dependencies={dependencies} />
      )}
    </div>
  );
};
