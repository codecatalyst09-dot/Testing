import json
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query
from backend.services.pipeline_orchestrator import PipelineOrchestrator
from backend.models.variable import VariableModel, VariableAnalysisResponse

router = APIRouter(prefix="/api", tags=["Variables"])

@router.get("/jobs/{job_id}/variables", response_model=VariableAnalysisResponse)
def get_variables(
    job_id: str,
    type: Optional[str] = Query(None, description="Filter by variable type (String, Number, List, etc.)"),
    scope: Optional[str] = Query(None, description="Filter by variable scope/task"),
    usage: Optional[str] = Query(None, description="Filter by usage (Read, Write, Read/Write)"),
    search: Optional[str] = Query(None, description="Search by variable name")
):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    vars_file = job_dir / "analysis" / "variable_analysis.json"

    if not vars_file.exists():
        raise HTTPException(status_code=404, detail="Variable analysis not ready for this job.")

    with open(vars_file, "r", encoding="utf-8") as f:
        raw_vars = json.load(f)

    variables = [VariableModel(**v) for v in raw_vars]

    if type:
        t_lower = type.lower()
        variables = [v for v in variables if v.type.lower() == t_lower]

    if scope:
        s_lower = scope.lower()
        variables = [v for v in variables if v.scope.lower() == s_lower]

    if usage:
        u_lower = usage.lower()
        variables = [v for v in variables if u_lower in v.usage.lower()]

    if search:
        search_lower = search.lower()
        variables = [v for v in variables if search_lower in v.name.lower() or search_lower in v.powerAutomateEquivalent.lower()]

    summary_by_type: Dict[str, int] = {}
    for v in variables:
        summary_by_type[v.type] = summary_by_type.get(v.type, 0) + 1

    return VariableAnalysisResponse(
        total_variables=len(variables),
        variables=variables,
        summary_by_type=summary_by_type
    )
