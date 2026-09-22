export interface VariableModel {
  name: string;
  type: string;
  scope: string;
  task: string;
  initialValue?: any;
  usage: 'Read' | 'Write' | 'Read/Write' | 'Unused';
  isInput: boolean;
  isOutput: boolean;
  expression?: string | null;
  powerAutomateEquivalent: string;
  usedInSteps: number[];
  createdInStep?: number | null;
  dependencies: string[];
  description?: string | null;
}

export interface VariableAnalysisResponse {
  total_variables: number;
  variables: VariableModel[];
  summary_by_type: Record<string, number>;
}
