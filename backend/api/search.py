import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from backend.services.pipeline_orchestrator import PipelineOrchestrator

router = APIRouter(prefix="/api", tags=["Search"])

@router.get("/jobs/{job_id}/search")
def global_search(job_id: str, q: str = Query(..., min_length=1, description="Global search term")):
    job_dir = PipelineOrchestrator.get_job_dir(job_id)
    parsed_file = job_dir / "parsed" / "parsed_workflow.json"

    if not parsed_file.exists():
        raise HTTPException(status_code=404, detail="Analysis data not available for search.")

    with open(parsed_file, "r", encoding="utf-8") as f:
        wf_data = json.load(f)

    term = q.lower().strip()
    results = {
        "query": q,
        "actions": [],
        "variables": [],
        "tasks": [],
        "disabled_actions": [],
        "total_matches": 0
    }

    # 1. Search Actions
    for a in wf_data.get("actions", []):
        matches = False
        step_str = str(a.get("step", ""))
        cmd = a.get("command", "").lower()
        pa_act = a.get("powerAutomateAction", "").lower()
        reason = a.get("reason", "").lower()
        task = a.get("task", "").lower()
        variables_used = [v.lower() for v in a.get("variablesUsed", [])]
        attr_str = str(a.get("attributes", {})).lower()

        if (term in step_str or term in cmd or term in pa_act or term in reason or
            term in task or any(term in v for v in variables_used) or term in attr_str):
            matches = True

        if matches:
            results["actions"].append({
                "step": a.get("step"),
                "task": a.get("task"),
                "command": a.get("command"),
                "powerAutomateAction": a.get("powerAutomateAction"),
                "platform": a.get("cloudOrDesktop"),
                "snippet": a.get("reason")
            })

    # 2. Search Variables
    for v in wf_data.get("variables", []):
        v_name = v.get("name", "").lower()
        v_type = v.get("type", "").lower()
        v_scope = v.get("scope", "").lower()
        v_pa = v.get("powerAutomateEquivalent", "").lower()

        if term in v_name or term in v_type or term in v_scope or term in v_pa:
            results["variables"].append({
                "name": v.get("name"),
                "type": v.get("type"),
                "scope": v.get("scope"),
                "powerAutomateEquivalent": v.get("powerAutomateEquivalent"),
                "usedInSteps": v.get("usedInSteps", [])
            })

    # 3. Search Tasks
    for t in wf_data.get("tasks", []):
        t_name = t.get("name", "").lower()
        t_purp = t.get("purpose", "").lower()
        if term in t_name or term in t_purp:
            results["tasks"].append({
                "name": t.get("name"),
                "purpose": t.get("purpose"),
                "stepsCount": t.get("stepsCount"),
                "cloudOrDesktop": t.get("cloudOrDesktop")
            })

    # 4. Search Disabled Actions
    for da in wf_data.get("disabledActions", []):
        da_cmd = da.get("command", "").lower()
        da_act = str(da.get("action", "")).lower()
        da_reason = da.get("reason", "").lower()
        da_task = da.get("task", "").lower()
        if term in da_cmd or term in da_act or term in da_reason or term in da_task:
            results["disabled_actions"].append(da)

    results["total_matches"] = (
        len(results["actions"]) +
        len(results["variables"]) +
        len(results["tasks"]) +
        len(results["disabled_actions"])
    )

    return results
