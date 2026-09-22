import React, { useState } from 'react';
import { FileText, Code, Download, Printer, ExternalLink } from 'lucide-react';
import { api } from '../services/api';

interface ReportViewerProps {
  jobId: string;
  markdown: string;
  html: string;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({ jobId, markdown, html }) => {
  const [viewMode, setViewMode] = useState<'html' | 'markdown'>('html');

  const printReport = () => {
    window.open(`/api/jobs/${jobId}/report/html`, '_blank');
  };

  return (
    <div className="space-y-4">
      {/* Header bar */}
      <div className="p-4 rounded-xl bg-slate-850 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('html')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              viewMode === 'html'
                ? 'bg-primary-600 text-white'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Styled HTML View</span>
          </button>
          <button
            onClick={() => setViewMode('markdown')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              viewMode === 'markdown'
                ? 'bg-primary-600 text-white'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Code className="w-4 h-4" />
            <span>Markdown Source</span>
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={printReport}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 border border-slate-700 text-xs font-medium transition-colors"
          >
            <Printer className="w-4 h-4" />
            <span>Print / Export PDF</span>
          </button>
          <a
            href={`/api/jobs/${jobId}/outputs/migration_report.md`}
            download="migration_report.md"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download .MD</span>
          </a>
        </div>
      </div>

      {/* Main View Area */}
      <div className="rounded-2xl border border-slate-800 bg-slate-850 overflow-hidden shadow-sm">
        {viewMode === 'html' ? (
          <iframe
            srcDoc={html}
            title="Migration Report"
            className="w-full h-[800px] border-0 bg-white"
          />
        ) : (
          <div className="p-6 max-h-[800px] overflow-y-auto">
            <pre className="font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
              {markdown}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
