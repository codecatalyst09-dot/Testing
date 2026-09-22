from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TargetCloudFlowAction(BaseModel):
    id: str
    name: str
    type: str  # e.g., "OpenApiConnection", "Scope", "If", "Foreach", "DesktopFlow"
    connector: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    runAfter: Dict[str, List[str]] = Field(default_factory=dict)

class TargetCloudFlow(BaseModel):
    name: str
    description: str = ""
    trigger: Dict[str, Any] = Field(default_factory=lambda: {"type": "Recurrence", "recurrence": {"frequency": "Day", "interval": 1}})
    actions: List[TargetCloudFlowAction] = Field(default_factory=list)
    connectionsNeeded: List[str] = Field(default_factory=list)
    environmentVariables: List[str] = Field(default_factory=list)

class TargetDesktopFlowAction(BaseModel):
    id: str
    name: str
    module: str  # e.g., "Excel", "WebAutomation", "UIAutomation", "File"
    statement: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class TargetDesktopFlow(BaseModel):
    name: str
    description: str = ""
    subroutines: List[str] = Field(default_factory=list)
    inputVariables: List[str] = Field(default_factory=list)
    outputVariables: List[str] = Field(default_factory=list)
    actions: List[TargetDesktopFlowAction] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)

class TargetArchitecture(BaseModel):
    architectureType: str  # "Cloud Only", "Desktop Only", "Hybrid (Cloud Orchestrated Desktop)"
    summary: str
    orchestrationPattern: str
    cloudFlows: List[TargetCloudFlow] = Field(default_factory=list)
    desktopFlows: List[TargetDesktopFlow] = Field(default_factory=list)
    recommendedConnections: List[str] = Field(default_factory=list)
    securityAndCredentialsGuidance: str
    migrationRoadmapPhases: List[Dict[str, Any]] = Field(default_factory=list)

class MigrationPlanModel(BaseModel):
    job_id: str
    workflow_name: str
    architecture: TargetArchitecture
    action_plans: List[Dict[str, Any]] = Field(default_factory=list)
    migration_risks: List[Dict[str, Any]] = Field(default_factory=list)
    manual_review_items: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_effort_hours: int = 0
