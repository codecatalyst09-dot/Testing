import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { JobProvider, useJob } from './context/JobContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { GlobalSearchModal } from './components/GlobalSearchModal';

// Pages
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';
import { Analysis } from './pages/Analysis';
import { Workflow } from './pages/Workflow';
import { Actions } from './pages/Actions';
import { Variables } from './pages/Variables';
import { DisabledActionsPage } from './pages/DisabledActionsPage';
import { Dependencies } from './pages/Dependencies';
import { Migration } from './pages/Migration';
import { Reports } from './pages/Reports';
import { Downloads } from './pages/Downloads';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 30, // 30 seconds
    },
  },
});

const MainContent: React.FC = () => {
  const { activeTab } = useJob();

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'upload':
        return <Upload />;
      case 'analysis':
        return <Analysis />;
      case 'workflow':
        return <Workflow />;
      case 'actions':
        return <Actions />;
      case 'variables':
        return <Variables />;
      case 'disabled':
        return <DisabledActionsPage />;
      case 'dependencies':
        return <Dependencies />;
      case 'migration':
        return <Migration />;
      case 'reports':
        return <Reports />;
      case 'downloads':
        return <Downloads />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <main className="flex-1 overflow-y-auto p-6 bg-slate-900">
      {renderActivePage()}
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
            <Sidebar />
            <MainContent />
          </div>
          <GlobalSearchModal />
        </div>
      </JobProvider>
    </QueryClientProvider>
  );
};

export default App;
