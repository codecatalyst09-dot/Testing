from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DisabledActionModel(BaseModel):
    task: str
    file: str
    originalStep: int
    command: str
    action: Optional[str] = "Execute"
    attributes: Dict[str, Any] = Field(default_factory=dict)
    location: Optional[str] = None
    parent: Optional[str] = None
    reason: str = "Action was disabled in A360"
    aaPackage: Optional[str] = ""
    aaAction: Optional[str] = ""
    aaDescription: Optional[str] = ""
    targetPlatform: Optional[str] = "Power Automate Desktop"
    padCategory: Optional[str] = ""
    padAction: Optional[str] = ""
    cloudAction: Optional[str] = ""
    recommendedAction: Optional[str] = ""
    migrationNotes: Optional[str] = ""

class ActionModel(BaseModel):
    id: str
    step: int
    task: str
    parentActionId: Optional[str] = None
    command: str
    operation: Optional[str] = None
    rawAction: Dict[str, Any] = Field(default_factory=dict)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    variablesUsed: List[str] = Field(default_factory=list)
    variablesCreated: List[str] = Field(default_factory=list)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    children: List[str] = Field(default_factory=list)
    sourceFile: str = ""
    sourcePath: str = ""
    cloudOrDesktop: str = "Manual Review"  # Cloud, Desktop, Hybrid, Manual Review
    powerAutomateAction: str = "Manual Review Required"
    migrationStrategy: str = "Manual Review"
    migrationComplexity: str = "Medium"  # Low, Medium, High
    confidence: float = 0.50
    reason: str = ""
    manualSteps: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    # Reference workbook mapping fields
    aaPackage: Optional[str] = ""
    aaAction: Optional[str] = ""
    aaDescription: Optional[str] = ""
    padCategory: Optional[str] = ""
    padAction: Optional[str] = ""
    cloudAction: Optional[str] = ""
    migrationNotes: Optional[str] = ""
    status: str = "Active"  # Active or Disabled
    isDisabled: bool = False
    disabledReason: Optional[str] = None

class ActionAnalysisResponse(BaseModel):
    total_actions: int
    actions: List[ActionModel]
    summary_by_platform: Dict[str, int]
    summary_by_complexity: Dict[str, int]
