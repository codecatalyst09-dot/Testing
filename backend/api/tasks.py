import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from backend.services.pipeline_orchestrator import PipelineOrchestrator
from backend.models.workflow import TaskModel

router = APIRouter(prefix="/api", tags=["Tasks"])

@router.get("/jobs/{job_id}/tasks", response_model=List[TaskModel])
def get_tasks(job_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    task_file = job_dir / "analysis" / "task_dependency.json"

    if not task_file.exists():
        raise HTTPException(status_code=404, detail="Task analysis not ready.")

    with open(task_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    tasks_raw = data.get("tasks", [])
    return [TaskModel(**t) for t in tasks_raw]
