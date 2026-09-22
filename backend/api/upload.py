import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import JobRecord
from backend.models.job import JobSummary, JobStatus, PipelineStage, InventoryItem
from backend.utils.security import sanitize_filename, validate_file_extension, MAX_FILE_SIZE, SecurityException
from backend.services.zip_service import ZipService
from backend.services.pipeline_orchestrator import STORAGE_BASE, PipelineOrchestrator
from backend.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Upload"])

@router.post("/upload", response_model=JobSummary)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    clean_name = sanitize_filename(file.filename)
    try:
        file_ext = validate_file_extension(clean_name)
    except SecurityException as se:
        raise HTTPException(status_code=400, detail=str(se))

    job_id = str(uuid.uuid4())
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    original_dir = job_dir / "original"
    original_dir.mkdir(parents=True, exist_ok=True)

    dest_file = original_dir / clean_name

    # Read and enforce file size
    size = 0
    with open(dest_file, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1MB chunk
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                dest_file.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB.")
            buffer.write(chunk)

    inventory_items = []
    if file_ext == ".zip":
        try:
            # Generate preview inventory without full extraction yet
            preview_dir = job_dir / "preview_extracted"
            inventory_items, _ = ZipService.extract_and_inventory(dest_file, preview_dir)
        except SecurityException as se:
            dest_file.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=f"ZIP security validation failed: {str(se)}")
        except Exception as e:
            logger.warning("PREVIEW_INVENTORY", f"Initial preview parse issue: {e}")
    else:
        inventory_items = [
            InventoryItem(
                name=clean_name,
                path=clean_name,
                size=size,
                file_type="Taskbot",
                is_main_task=True
            )
        ]

    # Create job in database
    job_record = JobRecord(
        id=job_id,
        filename=clean_name,
        file_type=file_ext.replace(".", ""),
        file_size=size,
        status=JobStatus.PENDING.value,
        current_stage=PipelineStage.FILE_UPLOADED.value,
        progress_percentage=8
    )
    job_record.set_inventory([item.model_dump() for item in inventory_items])
    db.add(job_record)
    db.commit()
    db.refresh(job_record)

    logger.info("UPLOAD_SUCCESS", f"File '{clean_name}' ({size} bytes) registered for job {job_id}", job_id=job_id)

    return JobSummary(
        job_id=job_id,
        filename=clean_name,
        file_type=job_record.file_type,
        file_size=size,
        status=JobStatus.PENDING,
        current_stage=PipelineStage.FILE_UPLOADED,
        progress_percentage=8,
        created_at=job_record.created_at,
        updated_at=job_record.updated_at,
        inventory=inventory_items
    )
