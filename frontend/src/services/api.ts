import { JobSummary, JobStatusResponse } from '../types/job';
import { ActionAnalysisResponse, ActionModel, DisabledActionModel } from '../types/action';
import { VariableAnalysisResponse } from '../types/variable';
import { WorkflowModel, TaskModel } from '../types/workflow';
import { MigrationPlanModel } from '../types/migration';

const API_BASE = '/api';

export interface ActionFilters {
  platform?: string;
  complexity?: string;
  task?: string;
  command?: string;
  search?: string;
}

export interface VariableFilters {
  type?: string;
  scope?: string;
  usage?: string;
  search?: string;
}

export const api = {
  async uploadFile(file: File): Promise<JobSummary> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async startAnalysis(jobId: string): Promise<{ message: string; job_id: string; status: string }> {
    const res = await fetch(`${API_BASE}/analyze/${jobId}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to start analysis' }));
      throw new Error(err.detail || 'Failed to start analysis');
    }
    return res.json();
  },

  async getJobDetails(jobId: string): Promise<JobSummary> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}`);
    if (!res.ok) throw new Error('Failed to get job details');
    return res.json();
  },

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/status`);
    if (!res.ok) throw new Error('Failed to get job status');
    return res.json();
  },

  async listJobs(): Promise<JobSummary[]> {
    const res = await fetch(`${API_BASE}/jobs`);
    if (!res.ok) throw new Error('Failed to list jobs');
    return res.json();
  },

  async getWorkflow(jobId: string): Promise<WorkflowModel> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/workflows`);
    if (!res.ok) throw new Error('Failed to get workflow data');
    return res.json();
  },

  async getActions(jobId: string, filters?: ActionFilters): Promise<ActionAnalysisResponse> {
    const params = new URLSearchParams();
    if (filters?.platform) params.append('platform', filters.platform);
    if (filters?.complexity) params.append('complexity', filters.complexity);
    if (filters?.task) params.append('task', filters.task);
    if (filters?.command) params.append('command', filters.command);
    if (filters?.search) params.append('search', filters.search);

    const res = await fetch(`${API_BASE}/jobs/${jobId}/actions?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to get actions');
    return res.json();
  },

  async getActionDetail(jobId: string, actionId: string): Promise<ActionModel> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/actions/${actionId}`);
    if (!res.ok) throw new Error('Failed to get action detail');
    return res.json();
  },

  async getVariables(jobId: string, filters?: VariableFilters): Promise<VariableAnalysisResponse> {
    const params = new URLSearchParams();
    if (filters?.type) params.append('type', filters.type);
    if (filters?.scope) params.append('scope', filters.scope);
    if (filters?.usage) params.append('usage', filters.usage);
    if (filters?.search) params.append('search', filters.search);

    const res = await fetch(`${API_BASE}/jobs/${jobId}/variables?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to get variables');
    return res.json();
  },

  async getDisabledActions(jobId: string): Promise<DisabledActionModel[]> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/disabled-actions`);
    if (!res.ok) throw new Error('Failed to get disabled actions');
    return res.json();
  },

  async getTasks(jobId: string): Promise<TaskModel[]> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/tasks`);
    if (!res.ok) throw new Error('Failed to get tasks');
    return res.json();
  },

  async getMigrationPlan(jobId: string): Promise<MigrationPlanModel> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/migration`);
    if (!res.ok) throw new Error('Failed to get migration plan');
    return res.json();
  },

  async getReportData(jobId: string): Promise<{ job_id: string; markdown: string; html: string; summary: any }> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/report`);
    if (!res.ok) throw new Error('Failed to get report data');
    return res.json();
  },

  async listOutputs(jobId: string): Promise<{ job_id: string; files: { filename: string; size: number; description: string }[] }> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/outputs`);
    if (!res.ok) throw new Error('Failed to list outputs');
    return res.json();
  },

  getDownloadBundleUrl(jobId: string): string {
    return `${API_BASE}/jobs/${jobId}/download`;
  },

  getDownloadExcelUrl(jobId: string): string {
    return `${API_BASE}/jobs/${jobId}/download-excel`;
  },

  getDownloadPreprocessedUrl(jobId: string): string {
    return `${API_BASE}/jobs/${jobId}/download-preprocessed`;
  },

  getSingleOutputUrl(jobId: string, filename: string): string {
    return `${API_BASE}/jobs/${jobId}/outputs/${filename}`;
  },

  async getGeneratedCode(jobId: string): Promise<{
    workflow_name: string;
    total_actions: number;
    bot_centricity?: string;
    bot_centricity_reason?: string;
    pad_script: string;
    cloud_flow_json: any;
    powershell_script: string;
    summary: {
      pad_lines: number;
      cloud_actions_count: number;
      desktop_actions_count: number;
      cloud_actions_count_stat: number;
      hybrid_actions_count: number;
    };
  }> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/code`);
    if (!res.ok) throw new Error('Failed to generate Power Automate code');
    return res.json();
  },

  getDownloadCodeUrl(jobId: string, fileType: 'pad' | 'cloud' | 'ps1' | 'all'): string {
    return `${API_BASE}/jobs/${jobId}/code/download/${fileType}`;
  },

  async globalSearch(jobId: string, query: string): Promise<any> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to execute search');
    return res.json();
  }
};
