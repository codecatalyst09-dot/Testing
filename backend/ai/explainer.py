import os
from typing import Dict, Any, Optional
from backend.models.workflow import WorkflowModel
from backend.models.migration import MigrationPlanModel
from backend.models.action import ActionModel
from backend.utils.logger import logger

class AIWorkflowExplainer:
    """
    Pluggable AI Analysis interface using OpenAI (supports gpt-4.1).
    Operates downstream of the deterministic parser and rule engine.
    Works seamlessly in offline/deterministic mode if no external LLM API key is configured.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1")
        self.client = None

        if self.api_key and self.api_key.strip() and not self.api_key.startswith("your_openai_api_key"):
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning("AI_INIT", f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def explain_workflow(self, workflow: WorkflowModel, plan: MigrationPlanModel) -> Dict[str, Any]:
        """
        Generates business process summary and migration reasoning.
        Uses OpenAI LLM when key is present, falls back gracefully to deterministic logic.
        """
        total_steps = workflow.statistics.totalActions
        cloud_pct = workflow.statistics.platformDistribution.get("Power Automate Cloud", 0)
        desktop_pct = workflow.statistics.platformDistribution.get("Power Automate Desktop", 0)
        hybrid_pct = workflow.statistics.platformDistribution.get("Hybrid", 0)

        # Baseline deterministic summary
        deterministic_summary = (
            f"This automation '{workflow.workflow.name}' executes an enterprise business process comprising "
            f"{total_steps} sequential and nested RPA steps across {workflow.statistics.totalTasks} taskbot(s). "
            f"Based on deterministic analysis, {cloud_pct}% of steps can execute serverlessly in Power Automate Cloud, "
            f"while {desktop_pct}% require Power Automate Desktop for local UI/Excel interactions."
        )

        deterministic_advice = (
            f"Recommended strategy: Deploy a parent Cloud Flow to handle triggers, data preparation, and notifications, "
            f"orchestrating unattended Power Automate Desktop flows on dedicated virtual machines for local application tasks."
        )

        if not self.client:
            return {
                "business_purpose": deterministic_summary,
                "architecture_recommendation": deterministic_advice,
                "ai_enhanced": False,
                "model_used": None
            }

        try:
            sample_actions = [
                f"- Task: {a.task} | Action: {a.aaPackage} > {a.aaAction} -> Target: {a.powerAutomateAction} ({a.cloudOrDesktop})"
                for a in workflow.actions[:25]
            ]
            actions_summary_str = "\n".join(sample_actions)

            prompt = (
                f"You are an enterprise RPA Migration Architect evaluating an Automation Anywhere A360 automation "
                f"being migrated to Microsoft Power Automate.\n\n"
                f"Automation Name: {workflow.workflow.name}\n"
                f"Total Tasks: {workflow.statistics.totalTasks}\n"
                f"Total Steps: {total_steps}\n"
                f"Platform Breakdown: Cloud={cloud_pct}%, Desktop={desktop_pct}%, Hybrid={hybrid_pct}%\n\n"
                f"Sample Bot Workflow Actions:\n{actions_summary_str}\n\n"
                f"Please provide:\n"
                f"1. A concise 2-3 sentence executive business process summary explaining what this automation accomplishes.\n"
                f"2. A concise 2-3 sentence technical migration strategy recommendation for Power Automate (Cloud vs Desktop vs Hybrid)."
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional Enterprise RPA & Cloud Automation Architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )

            content = response.choices[0].message.content.strip()
            # Split if sections are separated or use content
            return {
                "business_purpose": content,
                "architecture_recommendation": deterministic_advice,
                "ai_enhanced": True,
                "model_used": self.model
            }
        except Exception as e:
            logger.error("AI_EXPLAINER", f"Error generating LLM workflow explanation with {self.model}: {e}")
            return {
                "business_purpose": deterministic_summary,
                "architecture_recommendation": deterministic_advice,
                "ai_enhanced": False,
                "model_used": None,
                "error": str(e)
            }

    def explain_action(self, action: ActionModel) -> str:
        """
        Generates migration notes for an individual action.
        """
        return (
            f"Action '{action.command}' (Step {action.step}) maps to '{action.powerAutomateAction}' "
            f"under strategy '{action.migrationStrategy}' with {int(action.confidence*100)}% rule confidence."
        )

    def resolve_manual_review_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses LLM to recommend replacement logic for an unknown/manual review action.
        """
        if not self.client:
            return {
                "resolved": False,
                "recommendation": "Configure OPENAI_API_KEY in .env to enable AI-powered action resolution."
            }

        try:
            prompt = (
                f"An A360 automation action was flagged for Manual Review because it lacks a standard 1:1 mapping.\n"
                f"Command: {action_data.get('command')}\n"
                f"Action: {action_data.get('action') or action_data.get('operation')}\n"
                f"Parameters: {action_data.get('attributes')}\n\n"
                f"Recommend the equivalent Microsoft Power Automate connector, PAD action, or script (Office Script / PowerShell)."
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Microsoft Power Automate Migration Architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )

            return {
                "resolved": True,
                "recommendation": response.choices[0].message.content.strip(),
                "model_used": self.model
            }
        except Exception as e:
            return {
                "resolved": False,
                "recommendation": f"AI resolution error: {e}"
            }
