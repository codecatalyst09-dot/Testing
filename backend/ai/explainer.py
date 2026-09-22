from typing import Dict, Any, Optional
from backend.models.workflow import WorkflowModel
from backend.models.migration import MigrationPlanModel
from backend.models.action import ActionModel

class AIWorkflowExplainer:
    """
    Pluggable AI Analysis interface.
    Operates downstream of the deterministic parser and rule engine.
    Works seamlessly in offline/deterministic mode if no external LLM API key is configured.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def explain_workflow(self, workflow: WorkflowModel, plan: MigrationPlanModel) -> Dict[str, str]:
        """
        Generates business process summary and migration reasoning.
        """
        total_steps = workflow.statistics.totalActions
        cloud_pct = workflow.statistics.platformDistribution.get("Power Automate Cloud", 0)
        desktop_pct = workflow.statistics.platformDistribution.get("Power Automate Desktop", 0)

        summary = (
            f"This automation '{workflow.workflow.name}' executes an enterprise business process comprising "
            f"{total_steps} sequential and nested RPA steps across {workflow.statistics.totalTasks} taskbot(s). "
            f"Based on deterministic analysis, {cloud_pct}% of steps can execute serverlessly in Power Automate Cloud, "
            f"while {desktop_pct}% require Power Automate Desktop for local UI/Excel interactions."
        )

        architecture_advice = (
            f"Recommended strategy: Deploy a parent Cloud Flow to handle triggers, data preparation, and email notifications, "
            f"orchestrating an unattended Power Automate Desktop flow on a dedicated virtual machine for local application tasks."
        )

        return {
            "business_purpose": summary,
            "architecture_recommendation": architecture_advice,
            "ai_enhanced": False
        }

    def explain_action(self, action: ActionModel) -> str:
        """
        Generates migration notes for an individual action.
        """
        return (
            f"Action '{action.command}' (Step {action.step}) maps to '{action.powerAutomateAction}' "
            f"under strategy '{action.migrationStrategy}' with {int(action.confidence*100)}% rule confidence."
        )
