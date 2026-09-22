from typing import Dict, Any, Optional, Tuple

def match_hybrid_rule(
    command: str,
    action: Optional[str],
    attributes: Dict[str, Any],
    has_cloud_actions: bool = False,
    has_desktop_actions: bool = False
) -> Optional[Tuple[str, str, float]]:
    """
    Check if an action represents a hybrid integration bridge between Cloud and Desktop.
    """
    cmd_lower = (command or "").lower().strip()

    if cmd_lower in ("runtask", "subtask", "taskbot"):
        target_task = ""
        if isinstance(attributes, dict):
            target_task = str(attributes.get("taskbot", attributes.get("file", attributes.get("task", ""))))

        if has_desktop_actions:
            return (
                "Run a flow built with Power Automate for desktop",
                "Invokes a desktop flow from cloud flow orchestrator, passing input parameters and waiting for completion.",
                0.93
            )
        else:
            return (
                "Run Child Flow (Power Automate Cloud)",
                "Invokes reusable modular subflow with structured inputs/outputs.",
                0.91
            )

    # If the workflow is a mix of cloud services and desktop interactions
    if cmd_lower in ("database", "sql") and has_desktop_actions:
        return (
            "SQL Connector (Cloud) or Execute SQL statement (Desktop)",
            "Database action can be executed in Cloud via On-Premises Data Gateway or locally in Desktop Flow.",
            0.85
        )

    return None
