import React, { useState } from 'react';
import { MigrationPlanModel } from '../types/migration';
import { Compass, Cloud, Monitor, ShieldAlert, Calendar, Code, CheckCircle, ArrowRight } from 'lucide-react';

interface TargetArchitectureViewProps {
  plan: MigrationPlanModel;
}

export const TargetArchitectureView: React.FC<TargetArchitectureViewProps> = ({ plan }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'cloud' | 'desktop' | 'risks' | 'roadmap'>('overview');
  const arch = plan.architecture;

  return (
    <div className="space-y-6">
      {/* Top Banner with Architecture Type */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-850 to-slate-900 border border-slate-800 shadow-md">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-primary-500/15 border border-primary-500/30 flex items-center justify-center text-primary-400">
              <Compass className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-bold text-primary-400 uppercase tracking-wider">
                Target Solution Architecture
              </span>
              <h2 className="text-xl font-black text-white tracking-tight">{arch.architectureType}</h2>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Estimated Effort</span>
              <span className="font-mono font-bold text-primary-400 text-base">~{plan.estimated_effort_hours}h</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Identified Risks</span>
              <span className="font-mono font-bold text-amber-400 text-base">{plan.migration_risks.length}</span>
            </div>
          </div>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed mt-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800/80">
          {arch.summary}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'overview'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
          }`}
        >
          <Compass className="w-4 h-4" />
          <span>Orchestration Diagram</span>
        </button>
        <button
          onClick={() => setActiveTab('cloud')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'cloud'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
          }`}
        >
          <Cloud className="w-4 h-4" />
          <span>Cloud Flow Design ({arch.cloudFlows.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('desktop')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'desktop'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
          }`}
        >
          <Monitor className="w-4 h-4" />
          <span>Desktop Flow Design ({arch.desktopFlows.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('risks')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'risks'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          <span>Risks & Mitigations ({plan.migration_risks.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('roadmap')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'roadmap'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>Roadmap</span>
        </button>
      </div>

      {/* Tab Content: Overview Orchestration */}
      {activeTab === 'overview' && (
        <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-6">
          <h3 className="text-sm font-bold text-white">Target Orchestration Flow</h3>
          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-300 w-full md:w-64 space-y-2">
              <div className="flex items-center gap-2 font-bold text-blue-400">
                <Cloud className="w-4 h-4" />
                <span>Power Automate Cloud</span>
              </div>
              <p className="text-[11px] text-slate-300">
                • Recurrence or Webhook Trigger<br />
                • Initialize Parameters & Secrets<br />
                • Outlook / SharePoint Connectors
              </p>
            </div>

            <ArrowRight className="w-6 h-6 text-slate-600 shrink-0 rotate-90 md:rotate-0" />

            <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-300 w-full md:w-64 space-y-2">
              <div className="flex items-center gap-2 font-bold text-purple-400">
                <Monitor className="w-4 h-4" />
                <span>Power Automate Desktop</span>
              </div>
              <p className="text-[11px] text-slate-300">
                • Launch Excel & Parse Master<br />
                • Web Automation with Edge Extension<br />
                • Return extracted records
              </p>
            </div>

            <ArrowRight className="w-6 h-6 text-slate-600 shrink-0 rotate-90 md:rotate-0" />

            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 w-full md:w-64 space-y-2">
              <div className="flex items-center gap-2 font-bold text-emerald-400">
                <CheckCircle className="w-4 h-4" />
                <span>Completion & Audit</span>
              </div>
              <p className="text-[11px] text-slate-300">
                • Send confirmation emails<br />
                • Post Adaptive Card to Teams<br />
                • Update Dataverse / SQL record
              </p>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Security & Credential Architecture
            </h4>
            <p className="text-xs text-slate-300 p-4 rounded-xl bg-slate-900 border border-slate-800 leading-relaxed">
              {arch.securityAndCredentialsGuidance}
            </p>
          </div>
        </div>
      )}

      {/* Tab Content: Cloud Flow Blueprint */}
      {activeTab === 'cloud' && (
        <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Cloud className="w-4 h-4 text-blue-400" />
              <span>Generated Cloud Flow Schema</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">
              {arch.cloudFlows.length} Flow Blueprint
            </span>
          </div>

          {arch.cloudFlows.map((cf, idx) => (
            <div key={idx} className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-200 font-mono">{cf.name}</span>
                <span className="text-slate-400">{cf.description}</span>
              </div>
              <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-blue-300 overflow-x-auto max-h-96">
                {JSON.stringify(cf, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}

      {/* Tab Content: Desktop Flow Blueprint */}
      {activeTab === 'desktop' && (
        <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Monitor className="w-4 h-4 text-purple-400" />
              <span>Generated Desktop Flow Schema (PAD)</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">
              {arch.desktopFlows.length} Desktop Blueprint
            </span>
          </div>

          {arch.desktopFlows.map((df, idx) => (
            <div key={idx} className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-200 font-mono">{df.name}</span>
                <span className="text-slate-400">{df.description}</span>
              </div>
              <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-purple-300 overflow-x-auto max-h-96">
                {JSON.stringify(df, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}

      {/* Tab Content: Risks & Mitigations */}
      {activeTab === 'risks' && (
        <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>Technical Migration Risks & Considerations</span>
          </h3>

          <div className="space-y-3">
            {plan.migration_risks.map((r, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white flex items-center gap-2">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        r.severity === 'High' ? 'bg-rose-400' : 'bg-amber-400'
                      }`}
                    />
                    {r.title}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      r.severity === 'High'
                        ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                        : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {r.severity} Severity
                  </span>
                </div>
                <p className="text-xs text-slate-300">{r.description}</p>
                <div className="pt-2 border-t border-slate-800 text-xs">
                  <strong className="text-emerald-400 font-semibold">Mitigation Strategy: </strong>
                  <span className="text-slate-400">{r.mitigation}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab Content: Roadmap */}
      {activeTab === 'roadmap' && (
        <div className="p-6 rounded-2xl bg-slate-850 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Calendar className="w-4 h-4 text-primary-400" />
            <span>Recommended Phased Migration Roadmap</span>
          </h3>

          <div className="space-y-4">
            {arch.migrationRoadmapPhases.map((phase, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-primary-400">{phase.phase}</span>
                  <span className="text-xs font-mono text-slate-400">~{phase.durationDays} Days</span>
                </div>
                <ul className="space-y-1 text-xs text-slate-300">
                  {phase.tasks.map((task, tIdx) => (
                    <li key={tIdx} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-slate-600" />
                      <span>{task}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
