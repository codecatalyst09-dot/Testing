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
        Generates business process summary (rough idea) and multi-bot architecture breakdown.
        Uses OpenAI LLM (gpt-4.1) when key is present, falls back gracefully to deterministic logic.
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
                    "Power Automate Desktop" if t.cloudOrDesktop == "Desktop"
                    else "Power Automate Cloud" if t.cloudOrDesktop == "Cloud"
                    else "Hybrid"
                ),
                "called_by": t.parentTask or main_bot_name,
                "target_action": t.migrationStrategy
            }
            for t in sub_tasks
        ]

        # Deterministic Rough Idea
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
                f"Recommended strategy: Deploy '{main_bot_name}' as a parent Cloud Flow (or Master Desktop Flow) that manages process state, "
                f"orchestrating the {sub_bot_count} child sub-bots as modular Power Automate Desktop subflows or Cloud Child Flows."
            )
        else:
            rough_idea_text = (
                f"Standalone Automation: This bot '{main_bot_name}' operates as an independent single taskbot executing {total_steps} sequential steps. "
                f"All business logic, document manipulation, and user interface actions are self-contained without delegating to child sub-bots."
            )
            deterministic_advice = (
                f"Recommended strategy: Migrate '{main_bot_name}' as a single consolidated Power Automate Flow based on its action distribution."
            )

        if not self.client:
            return {
                "rough_idea": rough_idea_text,
                "has_sub_bots": has_sub_bots,
                "sub_bot_count": sub_bot_count,
                "main_bot_name": main_bot_name,
                "sub_bots": sub_bots_data,
                "architecture_recommendation": deterministic_advice,
                "ai_enhanced": False,
                "model_used": None
            }

        try:
            sub_bots_info_str = "\n".join([f"- Sub-Bot: {s['name']} | Role: {s['purpose']} | Steps: {s['steps']} | Target: {s['platform']}" for s in sub_bots_data])
            prompt = (
                f"You are an enterprise RPA Migration Architect evaluating an Automation Anywhere A360 automation.\n\n"
                f"Automation Name: {workflow.workflow.name}\n"
                f"Main Bot: {main_bot_name}\n"
                f"Has Sub-Bots: {has_sub_bots} (Total Sub-Bots: {sub_bot_count})\n"
                f"Sub-Bots Details:\n{sub_bots_info_str if has_sub_bots else 'No child sub-bots.'}\n\n"
                f"Total Steps: {total_steps}\n"
                f"Platform Breakdown: Cloud={cloud_pct}%, Desktop={desktop_pct}%, Hybrid={hybrid_pct}%\n\n"
                f"Please provide:\n"
                f"1. A concise 2-3 sentence 'rough idea' of what this automation accomplishes, explicitly mentioning the main bot and describing what each sub-bot is responsible for.\n"
                f"2. A 2-sentence architecture recommendation on how the main bot and sub-bots should be structured in Power Automate."
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
            return {
                "rough_idea": content,
                "has_sub_bots": has_sub_bots,
                "sub_bot_count": sub_bot_count,
                "main_bot_name": main_bot_name,
                "sub_bots": sub_bots_data,
                "architecture_recommendation": deterministic_advice,
                "ai_enhanced": True,
                "model_used": self.model
            }
        except Exception as e:
            logger.error("AI_EXPLAINER", f"Error generating LLM workflow explanation with {self.model}: {e}")
            return {
                "rough_idea": rough_idea_text,
                "has_sub_bots": has_sub_bots,
                "sub_bot_count": sub_bot_count,
                "main_bot_name": main_bot_name,
                "sub_bots": sub_bots_data,
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
