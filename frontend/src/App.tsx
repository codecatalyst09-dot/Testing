import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { JobProvider, useJob } from './context/JobContext';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 30,
    },
  },
});

const MainContent: React.FC = () => {
  const { activeTab, currentJobId } = useJob();

  if (activeTab === 'upload' || !currentJobId) {
    return (
      <main className="flex-1 overflow-y-auto p-6 md:p-10 max-w-5xl mx-auto w-full">
        <Upload />
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto p-6 md:p-8 max-w-7xl mx-auto w-full">
      <Dashboard />
    </main>
  );
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <JobProvider>
        <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-900 text-slate-100 font-sans">
          <Navbar />
          <div className="flex flex-1 overflow-hidden">
            <MainContent />
          </div>
        </div>
      </JobProvider>
    </QueryClientProvider>
  );
};

export default App;
