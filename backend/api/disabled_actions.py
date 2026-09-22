import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from backend.services.pipeline_orchestrator import PipelineOrchestrator
from backend.models.action import DisabledActionModel

router = APIRouter(prefix="/api", tags=["Disabled Actions"])

@router.get("/jobs/{job_id}/disabled-actions", response_model=List[DisabledActionModel])
def get_disabled_actions(job_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    disabled_file = job_dir / "analysis" / "disabled_actions.json"

    if not disabled_file.exists():
        raise HTTPException(status_code=404, detail="Disabled actions analysis not ready.")

    with open(disabled_file, "r", encoding="utf-8") as f:
        raw_disabled = json.load(f)

    return [DisabledActionModel(**da) for da in raw_disabled]
