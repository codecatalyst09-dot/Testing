from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.models.action import ActionModel, DisabledActionModel
from backend.models.variable import VariableModel

class WorkflowInfo(BaseModel):
    id: str
    name: str
    source: str = "Automation Anywhere A360"
    description: Optional[str] = None
    createdDate: Optional[str] = None
    author: Optional[str] = None

class TaskModel(BaseModel):
    id: str
    name: str
    purpose: str = "Automated Task"
    isMain: bool = False
    filePath: str = ""
    stepsCount: int = 0
    variablesCount: int = 0
    subtasks: List[str] = Field(default_factory=list)
    parentTask: Optional[str] = None
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    cloudOrDesktop: str = "Desktop"
    migrationStrategy: str = "Direct Mapping"
    centricity: str = "Desktop-Centric"

class DependencyModel(BaseModel):
    name: str
    type: str  # Application, API, Database, File, Credential, Browser, Desktop Software
    requiredByTasks: List[str] = Field(default_factory=list)
    requiredBySteps: List[int] = Field(default_factory=list)
    description: str = ""
    suggestedPAMechanism: str = ""

class StatisticsModel(BaseModel):
    totalWorkflows: int = 1
    totalTasks: int = 0
    totalActions: int = 0
    totalStepsEvaluated: int = 0
    migrationComplexity: str = "Easy"
    cloudActions: int = 0
    desktopActions: int = 0
    hybridActions: int = 0
    manualReviewActions: int = 0
    totalVariables: int = 0
    totalSubtasks: int = 0
    totalDisabledActions: int = 0
    platformDistribution: Dict[str, float] = Field(default_factory=dict)
    complexityDistribution: Dict[str, float] = Field(default_factory=dict)

class SubBotDetail(BaseModel):
    name: str
    purpose: str = "Subtask Automation"
    steps: int = 0
    platform: str = "Power Automate Desktop"
    called_by: Optional[str] = None
    target_action: Optional[str] = None

class WorkflowExplanation(BaseModel):
    rough_idea: str
    has_sub_bots: bool = False
    sub_bot_count: int = 0
    main_bot_name: str = "MainTask"
    sub_bots: List[SubBotDetail] = Field(default_factory=list)
    architecture_recommendation: str = ""
    ai_enhanced: bool = False
    model_used: Optional[str] = None

class WorkflowModel(BaseModel):
    workflow: WorkflowInfo
    tasks: List[TaskModel] = Field(default_factory=list)
    actions: List[ActionModel] = Field(default_factory=list)
    variables: List[VariableModel] = Field(default_factory=list)
    dependencies: List[DependencyModel] = Field(default_factory=list)
    disabledActions: List[DisabledActionModel] = Field(default_factory=list)
    statistics: StatisticsModel = Field(default_factory=StatisticsModel)
    explanation: Optional[WorkflowExplanation] = None
    botCentricity: str = "Desktop-Centric"  # "Desktop-Centric" | "Cloud-Centric" | "Hybrid"
    botCentricityReason: str = ""
    centricityMetrics: Dict[str, Any] = Field(default_factory=dict)

