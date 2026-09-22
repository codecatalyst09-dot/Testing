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
    cloudActions: int = 0
    desktopActions: int = 0
    hybridActions: int = 0
    manualReviewActions: int = 0
    totalVariables: int = 0
    totalSubtasks: int = 0
    totalDisabledActions: int = 0
    platformDistribution: Dict[str, float] = Field(default_factory=dict)
    complexityDistribution: Dict[str, float] = Field(default_factory=dict)

class WorkflowModel(BaseModel):
    workflow: WorkflowInfo
    tasks: List[TaskModel] = Field(default_factory=list)
    actions: List[ActionModel] = Field(default_factory=list)
    variables: List[VariableModel] = Field(default_factory=list)
    dependencies: List[DependencyModel] = Field(default_factory=list)
    disabledActions: List[DisabledActionModel] = Field(default_factory=list)
    statistics: StatisticsModel = Field(default_factory=StatisticsModel)
