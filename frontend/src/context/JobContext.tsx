import React, { createContext, useContext, useState, useEffect } from 'react';
import { JobSummary } from '../types/job';
import { api } from '../services/api';

interface JobContextType {
  currentJobId: string | null;
  setCurrentJobId: (id: string | null) => void;
  currentJob: JobSummary | null;
  jobsList: JobSummary[];
  activeTab: string;
  setActiveTab: (tab: string) => void;
  searchModalOpen: boolean;
  setSearchModalOpen: (open: boolean) => void;
  inspectingActionId: string | null;
  setInspectingActionId: (id: string | null) => void;
  refreshJobs: () => Promise<void>;
}

const JobContext = createContext<JobContextType | undefined>(undefined);

export const JobProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [currentJob, setCurrentJob] = useState<JobSummary | null>(null);
  const [jobsList, setJobsList] = useState<JobSummary[]>([]);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [searchModalOpen, setSearchModalOpen] = useState<boolean>(false);
  const [inspectingActionId, setInspectingActionId] = useState<string | null>(null);

  const refreshJobs = async () => {
    try {
      const list = await api.listJobs();
      setJobsList(list);
      if (!currentJobId && list.length > 0) {
        setCurrentJobId(list[0].job_id);
      } else if (list.length === 0) {
        setCurrentJobId(null);
        setCurrentJob(null);
        setActiveTab('upload');
      }
    } catch (e) {
      console.error('Failed to load jobs list', e);
    }
  };

  useEffect(() => {
    refreshJobs();
  }, []);

  useEffect(() => {
    if (currentJobId) {
      api.getJobDetails(currentJobId)
        .then(setCurrentJob)
        .catch(() => setCurrentJob(null));
    } else {
      setCurrentJob(null);
    }
  }, [currentJobId]);

  return (
    <JobContext.Provider
      value={{
        currentJobId,
        setCurrentJobId,
        currentJob,
        jobsList,
        activeTab,
        setActiveTab,
        searchModalOpen,
        setSearchModalOpen,
        inspectingActionId,
        setInspectingActionId,
        refreshJobs,
      }}
    >
      {children}
    </JobContext.Provider>
  );
};

export const useJob = () => {
  const context = useContext(JobContext);
  if (!context) {
    throw new Error('useJob must be used within a JobProvider');
  }
  return context;
};
