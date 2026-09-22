import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { ReportViewer } from '../components/ReportViewer';
import { FileText } from 'lucide-react';

export const Reports: React.FC = () => {
  const { currentJobId } = useJob();
  const [reportData, setReportData] = useState<{ markdown: string; html: string; summary: any } | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!currentJobId) return;
    setLoading(true);
    api.getReportData(currentJobId)
      .then(setReportData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [currentJobId]);

  return (
    <div className="space-y-4">
      <div className="p-4 rounded-2xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Migration Blueprint & Executive Report</h1>
            <p className="text-xs text-slate-400">
              Comprehensive report detailing executive metrics, action mapping, variable conversion, and technical risks.
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading report preview...</div>
      ) : reportData && currentJobId ? (
        <ReportViewer jobId={currentJobId} markdown={reportData.markdown} html={reportData.html} />
      ) : (
        <div className="p-8 text-center text-slate-500 text-xs">Report not generated yet.</div>
      )}
    </div>
  );
};
