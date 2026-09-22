import React, { useEffect, useState } from 'react';
import { useJob } from '../context/JobContext';
import { api } from '../services/api';
import { DownloadCloud, FileArchive, FileCode, FileText, Download, CheckCircle2 } from 'lucide-react';

export const Downloads: React.FC = () => {
  const { currentJobId } = useJob();
  const [files, setFiles] = useState<{ filename: string; size: number; description: string }[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!currentJobId) return;
    setLoading(true);
    api.listOutputs(currentJobId)
      .then((res) => setFiles(res.files))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [currentJobId]);

  const getFileIcon = (name: string) => {
    if (name.endsWith('.zip')) return <FileArchive className="w-5 h-5 text-purple-400" />;
    if (name.endsWith('.md') || name.endsWith('.html')) return <FileText className="w-5 h-5 text-emerald-400" />;
    return <FileCode className="w-5 h-5 text-blue-400" />;
  };

  return (
    <div className="space-y-6">
      {/* Download Bundle Primary Card */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-850 via-slate-900 to-slate-850 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-primary-500/15 text-primary-400 border border-primary-500/30">
            <DownloadCloud className="w-8 h-8" />
          </div>
          <div>
            <span className="text-xs font-bold text-primary-400 uppercase tracking-wider">
              Complete Migration Bundle
            </span>
            <h2 className="text-xl font-bold text-white mt-0.5">
              A360 Migration Analysis Package (.ZIP)
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Includes all 10 normalized JSON artifacts, Markdown report, standalone HTML executive report, and task dependency models.
            </p>
          </div>
        </div>

        {currentJobId && (
          <a
            href={api.getDownloadBundleUrl(currentJobId)}
            download
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-bold shadow-lg shadow-primary-500/25 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download Complete ZIP</span>
          </a>
        )}
      </div>

      {/* 10 Individual Artifacts Table */}
      <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-sm font-bold text-white">Generated Individual Output Artifacts</h3>
            <p className="text-xs text-slate-400">Export specific analysis datasets and preprocessed files</p>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {files.length} Available Files
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs">Loading output files...</div>
        ) : files.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {files.map((f) => (
              <div
                key={f.filename}
                className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {getFileIcon(f.filename)}
                  <div>
                    <span className="font-mono text-xs font-bold text-slate-200 block">
                      {f.filename}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      {(f.size / 1024).toFixed(1)} KB • {f.description}
                    </span>
                  </div>
                </div>

                {currentJobId && (
                  <a
                    href={api.getSingleOutputUrl(currentJobId, f.filename)}
                    download={f.filename}
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                    title={`Download ${f.filename}`}
                  >
                    <Download className="w-4 h-4" />
                  </a>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-slate-500 text-xs">
            Outputs not ready. Please run the analysis pipeline first.
          </div>
        )}
      </div>
    </div>
  );
};
