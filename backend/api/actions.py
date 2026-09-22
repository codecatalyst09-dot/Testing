import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from backend.services.pipeline_orchestrator import PipelineOrchestrator
from backend.models.action import ActionModel, ActionAnalysisResponse

router = APIRouter(prefix="/api", tags=["Actions"])

@router.get("/jobs/{job_id}/actions", response_model=ActionAnalysisResponse)
def get_actions(
    job_id: str,
    platform: Optional[str] = Query(None, description="Filter by platform: Power Automate Cloud, Power Automate Desktop, Hybrid, Manual Review"),
    complexity: Optional[str] = Query(None, description="Filter by complexity: Low, Medium, High"),
    task: Optional[str] = Query(None, description="Filter by taskbot name"),
    command: Optional[str] = Query(None, description="Filter by A360 command"),
    search: Optional[str] = Query(None, description="Search keyword across command, PA action, and notes")
):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    actions_file = job_dir / "analysis" / "action_analysis.json"

    if not actions_file.exists():
        raise HTTPException(status_code=404, detail="Action analysis not ready for this job.")

    with open(actions_file, "r", encoding="utf-8") as f:
        raw_actions = json.load(f)

    actions = [ActionModel(**a) for a in raw_actions]

    # Filtering
    if platform:
        p_lower = platform.lower()
        actions = [a for a in actions if p_lower in a.cloudOrDesktop.lower()]

    if complexity:
        c_lower = complexity.lower()
        actions = [a for a in actions if a.migrationComplexity.lower() == c_lower]

    if task:
        t_lower = task.lower()
        actions = [a for a in actions if a.task.lower() == t_lower]

    if command:
        cmd_lower = command.lower()
        actions = [a for a in actions if cmd_lower in a.command.lower()]

    if search:
        s_lower = search.lower()
        actions = [
            a for a in actions
            if s_lower in a.command.lower()
            or s_lower in a.powerAutomateAction.lower()
            or s_lower in a.reason.lower()
            or s_lower in str(a.attributes).lower()
            or s_lower in str(a.step)
            or any(s_lower in v.lower() for v in a.variablesUsed)
        ]

    platform_counts: Dict[str, int] = {}
    complexity_counts: Dict[str, int] = {}
    for a in actions:
        platform_counts[a.cloudOrDesktop] = platform_counts.get(a.cloudOrDesktop, 0) + 1
        complexity_counts[a.migrationComplexity] = complexity_counts.get(a.migrationComplexity, 0) + 1

    return ActionAnalysisResponse(
        total_actions=len(actions),
        actions=actions,
        summary_by_platform=platform_counts,
        summary_by_complexity=complexity_counts
    )

@router.get("/jobs/{job_id}/actions/{action_id}", response_model=ActionModel)
def get_action_detail(job_id: str, action_id: str):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    actions_file = job_dir / "analysis" / "action_analysis.json"

    if not actions_file.exists():
        raise HTTPException(status_code=404, detail="Action analysis not ready.")

    with open(actions_file, "r", encoding="utf-8") as f:
        raw_actions = json.load(f)

    for item in raw_actions:
        if item.get("id") == action_id or str(item.get("step")) == action_id:
            return ActionModel(**item)

    raise HTTPException(status_code=404, detail="Action not found.")
