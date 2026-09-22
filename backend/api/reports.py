import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from backend.services.pipeline_orchestrator import PipelineOrchestrator

router = APIRouter(prefix="/api", tags=["Reports & Downloads"])

@router.get("/jobs/{job_id}/report")
def get_report_data(job_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    md_file = job_dir / "reports" / "migration_report.md"
    html_file = job_dir / "reports" / "migration_report.html"
    summary_file = job_dir / "reports" / "migration_summary.json"

    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Reports have not been generated yet.")

    md_content = md_file.read_text(encoding="utf-8")
    html_content = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
    summary_data = json.loads(summary_file.read_text(encoding="utf-8")) if summary_file.exists() else {}

    return {
        "job_id": job_id,
        "markdown": md_content,
        "html": html_content,
        "summary": summary_data
    }

@router.get("/jobs/{job_id}/report/html", response_class=HTMLResponse)
def get_report_html(job_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    html_file = job_dir / "reports" / "migration_report.html"

    if not html_file.exists():
        raise HTTPException(status_code=404, detail="HTML report not found.")

    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))

@router.get("/jobs/{job_id}/download")
def download_analysis_bundle(job_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    zips = list(job_dir.glob("A360_Migration_Analysis_*.zip"))

    if not zips:
        raise HTTPException(status_code=404, detail="Analysis ZIP package not found.")

    latest_zip = sorted(zips, key=lambda x: x.stat().st_mtime, reverse=True)[0]
    return FileResponse(
        path=latest_zip,
        filename=latest_zip.name,
        media_type="application/zip"
    )

@router.get("/jobs/{job_id}/outputs")
def list_outputs(job_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    outputs_dir = job_dir / "outputs"

    if not outputs_dir.exists():
        raise HTTPException(status_code=404, detail="Outputs not generated.")

    files = []
    for f in outputs_dir.iterdir():
        if f.is_file():
            files.append({
                "filename": f.name,
                "size": f.stat().st_size,
                "description": f"Output artifact: {f.name}"
            })

    return {"job_id": job_id, "files": sorted(files, key=lambda x: x["filename"])}

@router.get("/jobs/{job_id}/outputs/{filename}")
def download_single_output(job_id: str, filename: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    outputs_dir = job_dir / "outputs"
    target_file = (outputs_dir / filename).resolve()

    # Path traversal check
    try:
        target_file.relative_to(outputs_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename or path.")

    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail="File not found in outputs.")

    media_type = "application/json"
    if target_file.suffix == ".md":
        media_type = "text/markdown"
    elif target_file.suffix == ".html":
        media_type = "text/html"
    elif target_file.suffix == ".xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(path=target_file, filename=target_file.name, media_type=media_type)

@router.get("/jobs/{job_id}/download-excel")
def download_migration_excel(job_id: str):
    """
    Directly downloads the definitive step-by-step Excel migration blueprint.
    """
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    excel_file = job_dir / "outputs" / "AA_to_PowerAutomate_Migration_Plan.xlsx"
    if not excel_file.exists():
        excel_file = job_dir / "reports" / "AA_to_PowerAutomate_Migration_Plan.xlsx"

    if not excel_file.exists():
        raise HTTPException(status_code=404, detail="Migration Excel blueprint not found or not yet generated.")

    return FileResponse(
        path=excel_file,
        filename="AA_to_PowerAutomate_Migration_Plan.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
