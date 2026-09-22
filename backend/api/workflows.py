import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.services.pipeline_orchestrator import PipelineOrchestrator
from backend.models.workflow import WorkflowModel

router = APIRouter(prefix="/api", tags=["Workflows"])

@router.get("/jobs/{job_id}/workflows", response_model=WorkflowModel)
def get_workflow(job_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    parsed_file = job_dir / "parsed" / "parsed_workflow.json"

    if not parsed_file.exists():
        raise HTTPException(status_code=404, detail="Workflow analysis has not completed for this job.")

    try:
        with open(parsed_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return WorkflowModel(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read workflow data: {str(e)}")
