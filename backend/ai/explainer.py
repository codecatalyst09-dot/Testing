from typing import Dict, Any, Optional
from backend.models.workflow import WorkflowModel
from backend.models.migration import MigrationPlanModel
from backend.models.action import ActionModel
from backend.utils.logger import logger

class WorkflowExplainer:
    """
    Deterministic Architecture Analysis Engine.
    Operates 100% offline with zero external LLM dependency.
    Extracts multi-bot hierarchies, business process summaries,
    and migration recommendations using deterministic rule analysis.
    """

    def __init__(self, api_key: Optional[str] = None):
        pass

    def explain_workflow(self, workflow: WorkflowModel, plan: MigrationPlanModel) -> Dict[str, Any]:
        """
        Generates business process summary (rough idea) and multi-bot architecture breakdown deterministically.
        """
        total_steps = workflow.statistics.totalActions
        cloud_pct = workflow.statistics.platformDistribution.get("Power Automate Cloud", 0)
        desktop_pct = workflow.statistics.platformDistribution.get("Power Automate Desktop", 0)
        hybrid_pct = workflow.statistics.platformDistribution.get("Hybrid", 0)

        # Identify Main Bot and Sub-Bots
        main_task = next((t for t in workflow.tasks if t.isMain), None) or (workflow.tasks[0] if workflow.tasks else None)
        main_bot_name = main_task.name if main_task else "MainTask"
        sub_tasks = [t for t in workflow.tasks if t != main_task]
        has_sub_bots = len(sub_tasks) > 0
        sub_bot_count = len(sub_tasks)

        sub_bots_data = [
            {
                "name": t.name,
                "purpose": t.purpose,
                "steps": t.stepsCount,
                "platform": (
                    "Power Automate Desktop" if t.cloudOrDesktop in ("Desktop", "Power Automate Desktop")
                    else "Power Automate Cloud" if t.cloudOrDesktop in ("Cloud", "Power Automate Cloud")
                    else "Hybrid"
                ),
                "called_by": t.parentTask or main_bot_name,
                "target_action": t.migrationStrategy
            }
            for t in sub_tasks
        ]

        # Deterministic Process Explanation
        if has_sub_bots:
            sub_summary_list = [f"'{t.name}' ({t.purpose})" for t in sub_tasks[:4]]
            sub_text = ", ".join(sub_summary_list)
            if sub_bot_count > 4:
                sub_text += f" and {sub_bot_count - 4} other sub-tasks"

            rough_idea_text = (
                f"Multi-Bot Process: The main orchestrator '{main_bot_name}' executes an enterprise workflow comprising "
                f"{total_steps} steps by coordinating {sub_bot_count} dedicated sub-bot(s): {sub_text}. "
                f"The main task initiates processing, establishes data context, and invokes child flows to handle document extraction, queue management, and application updates."
            )
            deterministic_advice = (
                f"Recommended strategy: Deploy '{main_bot_name}' as an orchestrating Cloud Flow (or Master Desktop Flow), "
                f"coordinating the {sub_bot_count} child sub-bots as modular Power Automate Desktop subflows or Cloud Child Flows."
            )
        else:
            rough_idea_text = (
                f"Standalone Automation: This bot '{main_bot_name}' operates as an independent single taskbot executing {total_steps} sequential steps. "
                f"All business logic, document manipulation, and user interface actions are self-contained without delegating to child sub-bots."
            )
            deterministic_advice = (
                f"Recommended strategy: Migrate '{main_bot_name}' as a single consolidated Power Automate Flow based on its action distribution."
            )

        return {
            "rough_idea": rough_idea_text,
            "has_sub_bots": has_sub_bots,
            "sub_bot_count": sub_bot_count,
            "main_bot_name": main_bot_name,
            "sub_bots": sub_bots_data,
            "architecture_recommendation": deterministic_advice,
            "ai_enhanced": False,
            "model_used": "Deterministic Rule Engine"
        }

    def explain_action(self, action: ActionModel) -> str:
        """
        Generates migration notes for an individual action deterministically.
        """
        return (
            f"Action '{action.command}' (Step {action.step}) maps to '{action.powerAutomateAction}' "
            f"under strategy '{action.migrationStrategy}' with {int(action.confidence*100)}% rule confidence."
        )

    def resolve_manual_review_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic recommendation for unknown or manual review actions.
        """
        cmd = str(action_data.get("command") or "").lower()
        if any(w in cmd for w in ("api", "http", "rest", "soap", "webhook")):
            rec = "Implement custom connector in Power Automate or use standard HTTP action with Azure Key Vault credentials."
        elif any(w in cmd for w in ("script", "powershell", "python", "vbs", "batch", "cmd")):
            rec = "Execute via Power Automate Desktop 'Run script' action (PowerShell / Python / VBScript) or Azure Function."
        elif any(w in cmd for w in ("db", "sql", "oracle", "database")):
            rec = "Connect via Power Automate SQL Server connector with On-Premises Data Gateway or PAD 'Open SQL connection'."
        else:
            rec = "Inspect original bot logic and implement equivalent Power Automate action or Office Script."

        return {
            "resolved": True,
            "recommendation": rec,
            "model_used": "Deterministic Rule Engine"
        }

# Alias for backwards compatibility with any existing imports
AIWorkflowExplainer = WorkflowExplainer
