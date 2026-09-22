export type JobStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export type PipelineStage =
  | 'FILE_UPLOADED'
  | 'ZIP_EXTRACTED'
  | 'A360_FILES_DISCOVERED'
  | 'ORIGINAL_ACTIONS_CAPTURED'
  | 'DISABLED_ACTIONS_DETECTED'
  | 'JSON_CLEANED'
  | 'WORKFLOW_PARSED'
  | 'VARIABLES_EXTRACTED'
  | 'SUBTASKS_IDENTIFIED'
  | 'ACTIONS_ANALYZED'
  | 'CLASSIFICATION_COMPLETE'
  | 'MAPPING_COMPLETE'
  | 'REPORT_GENERATED';

export interface InventoryItem {
  name: string;
  path: string;
  size: number;
  file_type: 'Taskbot' | 'Manifest' | 'Asset' | 'Config' | 'Other';
  is_main_task: boolean;
}

export interface JobSummary {
  job_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: JobStatus;
  current_stage: PipelineStage;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  error_message?: string | null;
  inventory: InventoryItem[];
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  current_stage: PipelineStage;
  stage_description: string;
  progress_percentage: number;
  error_message?: string | null;
  updated_at: string;
}
