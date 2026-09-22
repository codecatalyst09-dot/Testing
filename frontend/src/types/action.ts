export type PlatformType =
  | 'Power Automate Cloud'
  | 'Power Automate Desktop'
  | 'Hybrid'
  | 'Manual Review';

export type ComplexityType = 'Low' | 'Medium' | 'High';

export type MigrationStrategyType =
  | 'Direct Mapping'
  | 'Equivalent Connector'
  | 'Cloud Replacement'
  | 'Desktop Replacement'
  | 'Hybrid Implementation'
  | 'Custom API'
  | 'Custom Script'
  | 'Manual Review'
  | 'Not Supported';

export interface ActionModel {
  id: string;
  step: number;
  task: string;
  parentActionId?: string | null;
  command: string;
  operation?: string | null;
  rawAction: Record<string, any>;
  attributes: Record<string, any>;
  variablesUsed: string[];
  variablesCreated: string[];
  inputs: string[];
  outputs: string[];
  children: string[];
  sourceFile: string;
  sourcePath: string;
  cloudOrDesktop: PlatformType;
  powerAutomateAction: string;
  migrationStrategy: MigrationStrategyType;
  migrationComplexity: ComplexityType;
  confidence: number;
  reason: string;
  manualSteps: string[];
  dependencies: string[];
  aaPackage?: string;
  aaAction?: string;
  aaDescription?: string;
  padCategory?: string;
  padAction?: string;
  cloudAction?: string;
  migrationNotes?: string;
  status?: 'ACTIVE' | 'DISABLED' | string;
  isDisabled?: boolean;
  disabledReason?: string | null;
}

export interface DisabledActionModel {
  task: string;
  file: string;
  originalStep: number;
  command: string;
  action: string;
  attributes: Record<string, any>;
  location?: string | null;
  parent?: string | null;
  reason: string;
  aaPackage?: string;
  aaAction?: string;
  aaDescription?: string;
  targetPlatform?: string;
  padCategory?: string;
  padAction?: string;
  cloudAction?: string;
  recommendedAction?: string;
  migrationNotes?: string;
}

export interface ActionAnalysisResponse {
  total_actions: number;
  actions: ActionModel[];
  summary_by_platform: Record<string, number>;
  summary_by_complexity: Record<string, number>;
}
