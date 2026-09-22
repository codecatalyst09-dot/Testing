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

export interface WorkflowModel {
  workflow: WorkflowInfo;
  tasks: TaskModel[];
  actions: ActionModel[];
  variables: VariableModel[];
  dependencies: DependencyModel[];
  disabledActions: DisabledActionModel[];
  statistics: StatisticsModel;
}
