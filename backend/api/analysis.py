import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import JobRecord, AnalysisResultRecord
from backend.models.job import JobSummary, JobProgress, JobStatus, PipelineStage, STAGE_DESCRIPTIONS, InventoryItem
from backend.services.pipeline_orchestrator import PipelineOrchestrator
from backend.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Analysis"])

@router.post("/analyze/{job_id}")
async def start_analysis(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.status == JobStatus.PROCESSING.value:
        return {"message": "Job is already being processed", "job_id": job_id, "status": job.status}

    # Set status to processing
    job.status = JobStatus.PROCESSING.value
    db.commit()

    # Launch background task
    background_tasks.add_task(PipelineOrchestrator.run_analysis, job_id)

    logger.info("ANALYSIS_TRIGGERED", f"Dispatched background analysis for job {job_id}", job_id=job_id)
    return {"message": "Analysis initiated", "job_id": job_id, "status": JobStatus.PROCESSING.value}

@router.get("/jobs/{job_id}", response_model=JobSummary)
def get_job_details(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    inventory_data = job.get_inventory()
    inv_models = [InventoryItem(**item) for item in inventory_data]

    return JobSummary(
        job_id=job.id,
        filename=job.filename,
        file_type=job.file_type,
        file_size=job.file_size,
        status=JobStatus(job.status),
        current_stage=PipelineStage(job.current_stage),
        progress_percentage=job.progress_percentage,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error_message=job.error_message,
        inventory=inv_models
    )

@router.get("/jobs/{job_id}/status")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    curr_stage = PipelineStage(job.current_stage)
    description = STAGE_DESCRIPTIONS.get(curr_stage, "Processing")

    return {
        "job_id": job.id,
        "status": job.status,
        "current_stage": job.current_stage,
        "stage_description": description,
        "progress_percentage": job.progress_percentage,
        "error_message": job.error_message,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None
    }

@router.get("/jobs", response_model=List[JobSummary])
def list_jobs(db: Session = Depends(get_db)):
    records = db.query(JobRecord).order_by(JobRecord.created_at.desc()).limit(20).all()
    results = []
    for job in records:
        inventory_data = job.get_inventory()
        inv_models = [InventoryItem(**item) for item in inventory_data]
        results.append(JobSummary(
            job_id=job.id,
            filename=job.filename,
            file_type=job.file_type,
            file_size=job.file_size,
            status=JobStatus(job.status),
            current_stage=PipelineStage(job.current_stage),
            progress_percentage=job.progress_percentage,
            created_at=job.created_at,
            updated_at=job.updated_at,
            error_message=job.error_message,
            inventory=inv_models
        ))
    return results
