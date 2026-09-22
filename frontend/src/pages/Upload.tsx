import React from 'react';
import { UploadZone } from '../components/UploadZone';
import { UploadCloud } from 'lucide-react';

export const Upload: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-primary-500/15 text-primary-400 border border-primary-500/30">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Upload A360 Automation Package</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Upload your Automation Anywhere A360 ZIP package or standalone JSON taskbot file.
            </p>
          </div>
        </div>
      </div>

      <UploadZone />
    </div>
  );
};
