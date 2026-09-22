import io
import json
import zipfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from backend.services.pipeline_orchestrator import PipelineOrchestrator
from backend.models.workflow import WorkflowModel
from backend.models.migration import MigrationPlanModel
from backend.services.code_generator import CodeGenerator

router = APIRouter(prefix="/api", tags=["Code Generation"])

@router.get("/jobs/{job_id}/code")
def get_generated_code(job_id: str):
    """
    Generates Power Automate code for a parsed job:
    1. Power Automate Desktop (PAD) Script (.pad / Robin syntax)
    2. Power Automate Cloud Flow Definition JSON (Logic Apps schema)
    3. PowerShell Deployment Automation Script (.ps1)
    """
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    wf_file = job_dir / "parsed" / "parsed_workflow.json"
    plan_file = job_dir / "migration" / "migration_plan.json"

    if not wf_file.exists():
        raise HTTPException(status_code=404, detail="Workflow analysis not found or not yet parsed.")

    with open(wf_file, "r", encoding="utf-8") as f:
        wf_data = json.load(f)
    workflow_model = WorkflowModel(**wf_data)

    if not getattr(workflow_model, "botCentricityReason", None):
        from backend.migration.centricity_analyzer import CentricityAnalyzer
        workflow_model = CentricityAnalyzer.analyze_and_harmonize(workflow_model)

    if plan_file.exists():
        with open(plan_file, "r", encoding="utf-8") as f:
            plan_data = json.load(f)
        migration_plan = MigrationPlanModel(**plan_data)
    else:
        from backend.migration.migration_plan import MigrationPlanBuilder
        migration_plan = MigrationPlanBuilder.build_plan(
            job_id=job_id,
            workflow_name=workflow_model.workflow.name,
            actions=workflow_model.actions,
            variables=workflow_model.variables,
            dependencies=workflow_model.dependencies
        )

    code_payload = CodeGenerator.generate_all(workflow_model, migration_plan)
    return code_payload

@router.get("/jobs/{job_id}/code/download/{file_type}")
def download_code_file(job_id: str, file_type: str):
    """
    Downloads generated code file:
    - 'pad': Power Automate Desktop script (.pad)
    - 'cloud': Power Automate Cloud Flow JSON (.json)
    - 'ps1': PowerShell Deployment script (.ps1)
    - 'all': Zip package containing all code files
    """
    code_data = get_generated_code(job_id)
    bot_name = code_data["workflow_name"].replace(" ", "_")

    if file_type == "pad":
        return Response(
            content=code_data["pad_script"],
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={bot_name}_Desktop.pad"}
        )
    elif file_type == "cloud":
        return Response(
            content=json.dumps(code_data["cloud_flow_json"], indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={bot_name}_CloudFlow.json"}
        )
    elif file_type == "ps1":
        return Response(
            content=code_data["powershell_script"],
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=Deploy_{bot_name}.ps1"}
        )
    elif file_type == "all":
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{bot_name}_Desktop.pad", code_data["pad_script"])
            zf.writestr(f"{bot_name}_CloudFlow.json", json.dumps(code_data["cloud_flow_json"], indent=2))
            zf.writestr(f"Deploy_{bot_name}.ps1", code_data["powershell_script"])
            readme = (
                f"# Power Automate Migration Code Bundle for {bot_name}\n\n"
                f"Contains:\n"
                f"1. {bot_name}_Desktop.pad: Power Automate Desktop flow script (copy/paste into PAD designer)\n"
                f"2. {bot_name}_CloudFlow.json: Power Automate Cloud Flow definition (import into Power Platform solution)\n"
                f"3. Deploy_{bot_name}.ps1: Power Platform CLI automated solution deployment script\n"
            )
            zf.writestr("README.txt", readme)

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={bot_name}_PowerAutomate_Code.zip"}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Choose from: pad, cloud, ps1, all")
