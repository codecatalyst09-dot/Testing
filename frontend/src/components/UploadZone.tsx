import React, { useState, useRef } from 'react';
import { UploadCloud, FileCode, CheckCircle, AlertCircle, Play, FileArchive } from 'lucide-react';
import { api } from '../services/api';
import { JobSummary } from '../types/job';
import { useJob } from '../context/JobContext';

export const UploadZone: React.FC = () => {
  const { setCurrentJobId, setActiveTab, refreshJobs } = useJob();
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [uploadedJob, setUploadedJob] = useState<JobSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = async (file: File) => {
    setError(null);
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'zip' && ext !== 'json') {
      setError('Unsupported file type. Please upload an Automation Anywhere A360 .zip package or .json taskbot.');
      return;
    }

    if (file.size > 100 * 1024 * 1024) {
      setError('File size exceeds the 100MB limit.');
      return;
    }

    setSelectedFile(file);
    setUploading(true);

    try {
      const job = await api.uploadFile(file);
      setUploadedJob(job);
      setCurrentJobId(job.job_id);
      await refreshJobs();
    } catch (err: any) {
      setError(err.message || 'Failed to upload package');
    } finally {
      setUploading(false);
    }
  };

  const startAnalysis = async () => {
    if (!uploadedJob) return;
    setAnalyzing(true);
    setError(null);

    try {
      await api.startAnalysis(uploadedJob.job_id);
      await refreshJobs();
      setActiveTab('analysis');
    } catch (err: any) {
      setError(err.message || 'Failed to start analysis');
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Upload Dropzone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all ${
          dragActive
            ? 'border-primary-500 bg-primary-500/10'
            : 'border-slate-800 hover:border-slate-700 bg-slate-850/50 hover:bg-slate-850'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".zip,.json"
          onChange={(e) => e.target.files && handleFileSelected(e.target.files[0])}
          className="hidden"
        />

        <div className="w-16 h-16 rounded-2xl bg-primary-500/15 border border-primary-500/30 flex items-center justify-center mb-4 text-primary-400">
          <UploadCloud className="w-8 h-8" />
        </div>

        <h3 className="text-base font-semibold text-slate-200">
          {uploading ? 'Validating and Uploading...' : 'Drop A360 ZIP / JSON here'}
        </h3>
        <p className="text-xs text-slate-400 mt-1.5 text-center max-w-sm">
          Supports Automation Anywhere A360 multi-bot .zip packages or standalone taskbot .json files.
        </p>
        <div className="mt-4 flex items-center gap-2">
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            .zip
          </span>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            .json
          </span>
          <span className="text-xs text-slate-500">Max 100MB</span>
        </div>
      </div>

      {/* Error alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Uploaded Package Inventory Summary */}
      {uploadedJob && (
        <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                <CheckCircle className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-200">{uploadedJob.filename}</h4>
                <p className="text-xs text-slate-400">
                  {(uploadedJob.file_size / 1024).toFixed(1)} KB • {uploadedJob.file_type.toUpperCase()} Archive
                </p>
              </div>
            </div>

            <button
              onClick={startAnalysis}
              disabled={analyzing}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white font-semibold text-xs shadow-lg shadow-primary-500/25 transition-all disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{analyzing ? 'Starting Pipeline...' : 'Start Analysis'}</span>
            </button>
          </div>

          {/* Inventory Breakdown */}
          <div>
            <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Discovered Package Inventory ({uploadedJob.inventory.length} items)
            </h5>
            <div className="max-h-48 overflow-y-auto space-y-1.5 pr-2">
              {uploadedJob.inventory.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs"
                >
                  <div className="flex items-center gap-2">
                    {item.file_type === 'Taskbot' ? (
                      <FileCode className="w-4 h-4 text-blue-400" />
                    ) : (
                      <FileArchive className="w-4 h-4 text-slate-400" />
                    )}
                    <span className="font-mono text-slate-200">{item.name}</span>
                    {item.is_main_task && (
                      <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-primary-500/20 text-primary-400 border border-primary-500/30">
                        Main Taskbot
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-slate-400">
                    <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800">{item.file_type}</span>
                    <span className="text-[11px] font-mono">{(item.size / 1024).toFixed(1)} KB</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
