export interface TargetCloudFlowAction {
  id: string;
  name: string;
  type: string;
  connector?: string;
  operationId?: string;
  parameters: Record<string, any>;
  runAfter: Record<string, string[]>;
}

export interface TargetCloudFlow {
  name: string;
  description: string;
  trigger: Record<string, any>;
  actions: TargetCloudFlowAction[];
  connectionsNeeded: string[];
  environmentVariables: string[];
}

export interface TargetDesktopFlowAction {
  id: string;
  name: string;
  module: string;
  statement: string;
  parameters: Record<string, any>;
}

export interface TargetDesktopFlow {
  name: string;
  description: string;
  subroutines: string[];
  inputVariables: string[];
  outputVariables: string[];
  actions: TargetDesktopFlowAction[];
  prerequisites: string[];
}

export interface MigrationRoadmapPhase {
  phase: string;
  durationDays: number;
  tasks: string[];
}

export interface TargetArchitecture {
  architectureType: string;
  summary: string;
  orchestrationPattern: string;
  cloudFlows: TargetCloudFlow[];
  desktopFlows: TargetDesktopFlow[];
  recommendedConnections: string[];
  securityAndCredentialsGuidance: string;
  migrationRoadmapPhases: MigrationRoadmapPhase[];
}

export interface MigrationRisk {
  severity: 'Low' | 'Medium' | 'High';
  title: string;
  description: string;
  mitigation: string;
}

export interface ManualReviewItem {
  step: number;
  command: string;
  task: string;
  file: string;
  raw: Record<string, any>;
  reason: string;
  suggestedAction: string;
}

export interface MigrationPlanModel {
  job_id: string;
  workflow_name: string;
  architecture: TargetArchitecture;
  action_plans: Record<string, any>[];
  migration_risks: MigrationRisk[];
  manual_review_items: ManualReviewItem[];
  estimated_effort_hours: number;
}
