import json
from fastapi import APIRouter, HTTPException
from backend.services.pipeline_orchestrator import PipelineOrchestrator
from backend.models.migration import MigrationPlanModel

router = APIRouter(prefix="/api", tags=["Migration"])

@router.get("/jobs/{job_id}/migration", response_model=MigrationPlanModel)
def get_migration_plan(job_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    plan_file = job_dir / "migration" / "migration_plan.json"

    if not plan_file.exists():
        raise HTTPException(status_code=404, detail="Migration plan not generated yet.")

    with open(plan_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return MigrationPlanModel(**data)
