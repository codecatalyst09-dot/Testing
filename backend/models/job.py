from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class PipelineStage(str, Enum):
    FILE_UPLOADED = "FILE_UPLOADED"
    ZIP_EXTRACTED = "ZIP_EXTRACTED"
    A360_FILES_DISCOVERED = "A360_FILES_DISCOVERED"
    ORIGINAL_ACTIONS_CAPTURED = "ORIGINAL_ACTIONS_CAPTURED"
    DISABLED_ACTIONS_DETECTED = "DISABLED_ACTIONS_DETECTED"
    JSON_CLEANED = "JSON_CLEANED"
    WORKFLOW_PARSED = "WORKFLOW_PARSED"
    VARIABLES_EXTRACTED = "VARIABLES_EXTRACTED"
    SUBTASKS_IDENTIFIED = "SUBTASKS_IDENTIFIED"
    ACTIONS_ANALYZED = "ACTIONS_ANALYZED"
    CLASSIFICATION_COMPLETE = "CLASSIFICATION_COMPLETE"
    MAPPING_COMPLETE = "MAPPING_COMPLETE"
    REPORT_GENERATED = "REPORT_GENERATED"

PIPELINE_STAGE_ORDER = [
    PipelineStage.FILE_UPLOADED,
    PipelineStage.ZIP_EXTRACTED,
    PipelineStage.A360_FILES_DISCOVERED,
    PipelineStage.ORIGINAL_ACTIONS_CAPTURED,
    PipelineStage.DISABLED_ACTIONS_DETECTED,
    PipelineStage.JSON_CLEANED,
    PipelineStage.WORKFLOW_PARSED,
    PipelineStage.VARIABLES_EXTRACTED,
    PipelineStage.SUBTASKS_IDENTIFIED,
    PipelineStage.ACTIONS_ANALYZED,
    PipelineStage.CLASSIFICATION_COMPLETE,
    PipelineStage.MAPPING_COMPLETE,
    PipelineStage.REPORT_GENERATED,
]

STAGE_DESCRIPTIONS: Dict[PipelineStage, str] = {
    PipelineStage.FILE_UPLOADED: "File uploaded and validated",
    PipelineStage.ZIP_EXTRACTED: "ZIP package extracted safely",
    PipelineStage.A360_FILES_DISCOVERED: "A360 taskbots and manifests discovered",
    PipelineStage.ORIGINAL_ACTIONS_CAPTURED: "Original action inventory indexed",
    PipelineStage.DISABLED_ACTIONS_DETECTED: "Disabled actions recorded prior to removal",
    PipelineStage.JSON_CLEANED: "A360 JSON preprocessed and pruned",
    PipelineStage.WORKFLOW_PARSED: "Hierarchical workflow structure parsed",
    PipelineStage.VARIABLES_EXTRACTED: "Variable references, scopes, and types extracted",
    PipelineStage.SUBTASKS_IDENTIFIED: "Subtasks, Run Task calls, and dependency tree built",
    PipelineStage.ACTIONS_ANALYZED: "Step-by-step RPA actions analyzed",
    PipelineStage.CLASSIFICATION_COMPLETE: "Cloud vs Desktop vs Hybrid classification complete",
    PipelineStage.MAPPING_COMPLETE: "Power Automate action mapping and strategy completed",
    PipelineStage.REPORT_GENERATED: "Migration blueprint, reports, and downloadable bundle created",
}

class InventoryItem(BaseModel):
    name: str
    path: str
    size: int
    file_type: str  # "Taskbot", "Manifest", "Asset", "Other"
    is_main_task: bool = False

class JobProgress(BaseModel):
    current_stage: PipelineStage
    completed_stages: List[PipelineStage] = Field(default_factory=list)
    percentage: int = 0
    message: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class JobSummary(BaseModel):
    job_id: str
    filename: str
    file_type: str  # "zip" or "json"
    file_size: int
    status: JobStatus
    current_stage: PipelineStage
    progress_percentage: int
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    inventory: List[InventoryItem] = Field(default_factory=list)
