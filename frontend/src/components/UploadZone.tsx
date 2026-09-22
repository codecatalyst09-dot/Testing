import React, { useState, useRef } from 'react';
import { UploadCloud, FileCode, CheckCircle, AlertCircle, FileArchive, ArrowRight, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { useJob } from '../context/JobContext';

export const UploadZone: React.FC = () => {
  const { setCurrentJobId, setActiveTab, refreshJobs } = useJob();
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState<boolean>(false);
  const [statusText, setStatusText] = useState<string>('');
  const [progressPercent, setProgressPercent] = useState<number>(0);
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
      setError('Unsupported file format. Please upload an Automation Anywhere A360 .zip package or .json taskbot.');
      return;
    }

    if (file.size > 100 * 1024 * 1024) {
      setError('File size exceeds the 100MB limit.');
      return;
    }

    setSelectedFile(file);
    setProcessing(true);
    setStatusText('1/3: Uploading & Preprocessing file (cleaning noise, detecting disabled actions)...');
    setProgressPercent(25);

    try {
      // 1. Upload
      const job = await api.uploadFile(file);
      setProgressPercent(50);
      setStatusText('2/3: Parsing A360 actions & mapping to Power Automate reference...');

      // 2. Start analysis
      await api.startAnalysis(job.job_id);
      setProgressPercent(75);

      // 3. Poll until completed
      setStatusText('3/3: Evaluating migration complexity & generating detailed Excel blueprint...');
      let completed = false;
      for (let i = 0; i < 20; i++) {
        await new Promise((r) => setTimeout(r, 600));
        const statusData = await api.getJobStatus(job.job_id);
        if (statusData.status === 'COMPLETED') {
          completed = true;
          break;
        }
        if (statusData.status === 'FAILED') {
          throw new Error('Analysis pipeline encountered an issue processing the file.');
        }
      }

      setProgressPercent(100);
      setStatusText('Done! Loading migration blueprint...');
      await refreshJobs();
      setCurrentJobId(job.job_id);

      setTimeout(() => {
        setProcessing(false);
        setActiveTab('dashboard');
      }, 400);
    } catch (err: any) {
      setError(err.message || 'Failed to process file');
      setProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Upload Dropzone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !processing && inputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center transition-all ${
          processing
            ? 'border-primary-500/50 bg-slate-850/80 cursor-wait'
            : dragActive
            ? 'border-primary-500 bg-primary-500/10 cursor-pointer scale-[1.01]'
            : 'border-slate-800 hover:border-slate-700 bg-slate-850/60 hover:bg-slate-850 cursor-pointer'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".zip,.json"
          disabled={processing}
          onChange={(e) => e.target.files && handleFileSelected(e.target.files[0])}
          className="hidden"
        />

        {processing ? (
          <div className="text-center space-y-4 max-w-md w-full">
            <div className="w-14 h-14 rounded-2xl bg-primary-500/20 text-primary-400 border border-primary-500/30 flex items-center justify-center mx-auto animate-pulse">
              <Sparkles className="w-7 h-7 animate-spin" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Processing Automation Package</h3>
              <p className="text-xs text-slate-400 mt-1 font-mono">{statusText}</p>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden border border-slate-700">
              <div
                className="bg-gradient-to-r from-blue-500 to-teal-400 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        ) : (
          <>
            <div className="w-16 h-16 rounded-2xl bg-primary-500/15 text-primary-400 border border-primary-500/30 flex items-center justify-center mb-4">
              <UploadCloud className="w-8 h-8" />
            </div>

            <h3 className="text-base font-bold text-white mb-1">
              Select or Drop A360 File (.zip or .json)
            </h3>
            <p className="text-xs text-slate-400 text-center max-w-sm mb-4">
              Upload an Automation Anywhere A360 automation package (.zip) or taskbot (.json).
            </p>

            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                <FileArchive className="w-3.5 h-3.5 text-amber-400" />
                A360 Package (.zip)
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                <FileCode className="w-3.5 h-3.5 text-blue-400" />
                Taskbot (.json)
              </span>
            </div>

            <button
              type="button"
              className="mt-6 px-5 py-2 rounded-xl bg-primary-600 hover:bg-primary-500 text-white font-semibold text-xs shadow-md shadow-primary-500/20 transition-all"
            >
              Browse Files
            </button>
          </>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Clean Workflow Explanation */}
      <div className="p-5 rounded-xl bg-slate-850 border border-slate-800 space-y-3">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          How It Works
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <span className="font-bold text-white flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full bg-blue-500/20 text-blue-400 inline-flex items-center justify-center text-[10px]">1</span>
              Preprocess & Clean
            </span>
            <p className="text-slate-400 text-[11px]">
              Safely unzips, strips logging/comments, and preserves all disabled actions with step locations.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <span className="font-bold text-white flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full bg-purple-500/20 text-purple-400 inline-flex items-center justify-center text-[10px]">2</span>
              Parse & Map Actions
            </span>
            <p className="text-slate-400 text-[11px]">
              Maps all 274 actions to Power Automate (Desktop or Cloud) based on the official reference mapping workbook.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <span className="font-bold text-white flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 inline-flex items-center justify-center text-[10px]">3</span>
              Excel Blueprint
            </span>
            <p className="text-slate-400 text-[11px]">
              Calculates migration complexity (&lt;200 Easy, 200-400 Medium, &gt;400 Hard) and exports ready-to-use Excel.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
