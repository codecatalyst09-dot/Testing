from typing import List, Optional, Any
from pydantic import BaseModel, Field

class VariableModel(BaseModel):
    name: str
    type: str = "String"
    scope: str = "Task"
    task: str = "MainTask"
    initialValue: Optional[Any] = None
    usage: str = "Read/Write"  # Read, Write, Read/Write, Unused
    isInput: bool = False
    isOutput: bool = False
    expression: Optional[str] = None
    powerAutomateEquivalent: str = "String variable"
    usedInSteps: List[int] = Field(default_factory=list)
    createdInStep: Optional[int] = None
    dependencies: List[str] = Field(default_factory=list)
    description: Optional[str] = None

class VariableAnalysisResponse(BaseModel):
    total_variables: int
    variables: List[VariableModel]
    summary_by_type: dict = Field(default_factory=dict)
