import { ActionModel, DisabledActionModel } from './action';
import { VariableModel } from './variable';

export interface WorkflowInfo {
  id: string;
  name: string;
  source: string;
  description?: string | null;
  createdDate?: string | null;
  author?: string | null;
}

export interface TaskModel {
  id: string;
  name: string;
  purpose: string;
  isMain: boolean;
  filePath: string;
  stepsCount: number;
  variablesCount: number;
  subtasks: string[];
  parentTask?: string | null;
  inputs: string[];
  outputs: string[];
  cloudOrDesktop: string;
  migrationStrategy: string;
  centricity?: 'Desktop-Centric' | 'Cloud-Centric' | 'Hybrid' | string;
}

export interface DependencyModel {
  name: string;
  type: string;
  requiredByTasks: string[];
  requiredBySteps: number[];
  description: string;
  suggestedPAMechanism: string;
}

export interface StatisticsModel {
  totalWorkflows: number;
  totalTasks: number;
  totalActions: number;
  totalStepsEvaluated?: number;
  migrationComplexity?: 'Easy' | 'Medium' | 'Hard' | string;
  cloudActions: number;
  desktopActions: number;
  hybridActions: number;
  manualReviewActions: number;
  totalVariables: number;
  totalSubtasks: number;
  totalDisabledActions: number;
  platformDistribution: Record<string, number>;
  complexityDistribution: Record<string, number>;
}

export interface SubBotDetail {
  name: string;
  purpose: string;
  steps: number;
  platform: string;
  called_by?: string | null;
  target_action?: string | null;
}

export interface WorkflowExplanation {
  rough_idea: string;
  has_sub_bots: boolean;
  sub_bot_count: number;
  main_bot_name: string;
  sub_bots: SubBotDetail[];
  architecture_recommendation: string;
  ai_enhanced: boolean;
  model_used?: string | null;
}

export interface WorkflowModel {
  workflow: WorkflowInfo;
  tasks: TaskModel[];
  actions: ActionModel[];
  variables: VariableModel[];
  dependencies: DependencyModel[];
  disabledActions: DisabledActionModel[];
  statistics: StatisticsModel;
  explanation?: WorkflowExplanation | null;
  botCentricity?: 'Desktop-Centric' | 'Cloud-Centric' | 'Hybrid' | string;
  botCentricityReason?: string;
  centricityMetrics?: Record<string, any>;
}
