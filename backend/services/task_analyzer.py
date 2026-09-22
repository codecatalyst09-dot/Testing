from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.models.workflow import TaskModel
from backend.models.action import ActionModel

class TaskAnalyzer:
    @staticmethod
    def analyze_tasks(
        task_inventory: List[Dict[str, Any]],
        all_actions: List[ActionModel]
    ) -> List[TaskModel]:
        tasks: List[TaskModel] = []
        action_map_by_task: Dict[str, List[ActionModel]] = {}

        for act in all_actions:
            action_map_by_task.setdefault(act.task, []).append(act)

        # If no tasks identified, create default MainTask
        if not task_inventory:
            task_inventory = [{"name": "MainTask", "path": "MainTask.json", "is_main": True}]

        task_names = [t["name"] for t in task_inventory]

        for t_info in task_inventory:
            t_name = t_info.get("name", "Task")
            t_path = t_info.get("path", "")
            is_main = t_info.get("is_main", False)

            task_actions = action_map_by_task.get(t_name, [])
            subtasks = []

            # Check actions in this task for runTask calls
            for a in task_actions:
                if a.command.lower() in ("runtask", "subtask"):
                    # Find target task
                    attrs = a.attributes or {}
                    target = (
                        attrs.get("taskbot")
                        or attrs.get("taskbotFile")
                        or attrs.get("task")
                        or attrs.get("name")
                        or "ChildTask"
                    )
                    clean_target = Path(str(target)).stem
                    if clean_target not in subtasks and clean_target != t_name:
                        subtasks.append(clean_target)

            # Determine task purpose
            has_excel = any("excel" in a.command.lower() for a in task_actions)
            has_browser = any("browser" in a.command.lower() for a in task_actions)
            has_email = any("email" in a.command.lower() for a in task_actions)
            has_api = any("http" in a.command.lower() or "rest" in a.command.lower() for a in task_actions)

            purpose_parts = []
            if has_excel:
                purpose_parts.append("Excel Document Processing")
            if has_browser:
                purpose_parts.append("Web Portal Automation")
            if has_api:
                purpose_parts.append("REST API Integration")
            if has_email:
                purpose_parts.append("Email Dispatch & Notifications")

            purpose = ", ".join(purpose_parts) if purpose_parts else ("Main Process Flow" if is_main else "Subtask Automation")

            # Determine classification of task
            has_desktop = any(a.cloudOrDesktop == "Power Automate Desktop" for a in task_actions)
            has_cloud = any(a.cloudOrDesktop == "Power Automate Cloud" for a in task_actions)
            if has_desktop and has_cloud:
                classification = "Hybrid"
                strategy = "Hybrid Cloud/Desktop Flow"
            elif has_desktop:
                classification = "Desktop"
                strategy = "Power Automate Desktop Subflow"
            else:
                classification = "Cloud"
                strategy = "Power Automate Cloud Child Flow"

            tasks.append(TaskModel(
                id=f"task_{t_name}",
                name=t_name,
                purpose=purpose,
                isMain=is_main,
                filePath=t_path,
                stepsCount=len(task_actions),
                variablesCount=len(set(v for a in task_actions for v in a.variablesUsed)),
                subtasks=subtasks,
                parentTask=None,  # Will be resolved below
                inputs=[],
                outputs=[],
                cloudOrDesktop=classification,
                migrationStrategy=strategy
            ))

        # Resolve parent relationships
        for parent_t in tasks:
            for child_name in parent_t.subtasks:
                for child_t in tasks:
                    if child_t.name == child_name:
                        child_t.parentTask = parent_t.name

        return tasks
