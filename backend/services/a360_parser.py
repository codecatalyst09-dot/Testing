import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from backend.models.workflow import WorkflowModel, WorkflowInfo, TaskModel, StatisticsModel
from backend.models.action import ActionModel, DisabledActionModel
from backend.migration.mapping_engine import MappingEngine
from backend.services.variable_analyzer import VariableAnalyzer
from backend.services.task_analyzer import TaskAnalyzer
from backend.services.dependency_analyzer import DependencyAnalyzer
from backend.utils.logger import logger

VARIABLE_REGEX = re.compile(r'\$([a-zA-Z0-9_]+)(?:\.[a-zA-Z0-9_]+)?\$')

class A360Parser:
    def __init__(self):
        self.actions: List[ActionModel] = []
        self.action_counter = 0

    def _extract_variables_from_attributes(self, attrs: Dict[str, Any]) -> List[str]:
        """Extract variable names referenced as $VarName$ in attributes."""
        found = set()
        s = str(attrs)
        for match in VARIABLE_REGEX.findall(s):
            found.add(match)
        return sorted(list(found))

    def _parse_action_node(
        self,
        node: Dict[str, Any],
        task_name: str,
        source_file: str,
        parent_action_id: Optional[str] = None
    ) -> Optional[ActionModel]:
        command = node.get("command") or node.get("commandName")
        if not command:
            return None

        self.action_counter += 1
        action_id = f"action-{self.action_counter:04d}"
        step = node.get("step", self.action_counter)

        # Extract attributes and operation
        attributes = {}
        for k, v in node.items():
            if k not in ("command", "commandName", "step", "children", "branches", "nodes", "rawAction"):
                attributes[k] = v

        operation = (
            attributes.get("action")
            or attributes.get("operation")
            or node.get("actionName")
            or node.get("action")
            or ""
        )

        variables_used = self._extract_variables_from_attributes(attributes)
        variables_created = []
        output_var = attributes.get("variable") or attributes.get("outputVariable")
        if output_var and isinstance(output_var, str):
            clean_var = output_var.replace("$", "").strip()
            if clean_var:
                variables_created.append(clean_var)

        # Map to Power Automate
        mapped = MappingEngine.map_action(
            command=command,
            operation=operation,
            attributes=attributes
        )

        action_obj = ActionModel(
            id=action_id,
            step=step,
            task=task_name,
            parentActionId=parent_action_id,
            command=command,
            operation=operation,
            rawAction=node,
            attributes=attributes,
            variablesUsed=variables_used,
            variablesCreated=variables_created,
            inputs=[str(v) for k, v in attributes.items() if "path" in k.lower() or "input" in k.lower() or "url" in k.lower()],
            outputs=[str(v) for v in variables_created],
            children=[],
            sourceFile=source_file,
            sourcePath=source_file,
            cloudOrDesktop=mapped["targetPlatform"],
            powerAutomateAction=mapped["targetAction"],
            migrationStrategy=mapped["strategy"],
            migrationComplexity=mapped["complexity"],
            confidence=mapped["confidence"],
            reason=mapped["reason"],
            manualSteps=mapped["manualSteps"],
            dependencies=mapped["dependencies"]
        )

        self.actions.append(action_obj)

        # Recursively parse nested blocks (children, branches, then, else, loop body)
        child_ids = []
        for child_key in ("children", "branches", "then", "else", "nodes", "actions"):
            child_content = node.get(child_key)
            if isinstance(child_content, list):
                for child_item in child_content:
                    if isinstance(child_item, dict):
                        child_action = self._parse_action_node(
                            child_item, task_name, source_file, parent_action_id=action_id
                        )
                        if child_action:
                            child_ids.append(child_action.id)
            elif isinstance(child_content, dict):
                child_action = self._parse_action_node(
                    child_content, task_name, source_file, parent_action_id=action_id
                )
                if child_action:
                    child_ids.append(child_action.id)

        action_obj.children = child_ids
        return action_obj

    def _traverse_and_parse(
        self,
        node: Any,
        task_name: str,
        source_file: str,
        parent_id: Optional[str] = None
    ):
        if isinstance(node, list):
            for item in node:
                self._traverse_and_parse(item, task_name, source_file, parent_id)
        elif isinstance(node, dict):
            if "command" in node or "commandName" in node:
                self._parse_action_node(node, task_name, source_file, parent_id)
            else:
                for k, v in node.items():
                    if isinstance(v, (dict, list)):
                        self._traverse_and_parse(v, task_name, source_file, parent_id)

    def parse(
        self,
        cleaned_taskbots_data: List[Tuple[str, str, Any]],  # List of (task_name, source_file, cleaned_json)
        raw_data_map: Dict[str, Any],  # task_name -> raw_json (for variable definitions)
        disabled_actions: List[Dict[str, Any]],
        workflow_id: str = "wf-001",
        workflow_name: str = "A360 Workflow"
    ) -> WorkflowModel:
        self.actions = []
        self.action_counter = 0

        # Parse actions for every taskbot
        for task_name, source_file, cleaned_data in cleaned_taskbots_data:
            self._traverse_and_parse(cleaned_data, task_name, source_file)

        # Contextual refinement: if workflow has both cloud and desktop actions, mark hybrid bridging
        has_cloud = any(a.cloudOrDesktop == "Power Automate Cloud" for a in self.actions)
        has_desktop = any(a.cloudOrDesktop == "Power Automate Desktop" for a in self.actions)
        if has_cloud and has_desktop:
            for a in self.actions:
                if a.command.lower() in ("runtask", "subtask"):
                    mapped = MappingEngine.map_action(
                        command=a.command,
                        operation=a.operation,
                        attributes=a.attributes,
                        context_has_cloud=True,
                        context_has_desktop=True
                    )
                    a.cloudOrDesktop = mapped["targetPlatform"]
                    a.powerAutomateAction = mapped["targetAction"]
                    a.migrationStrategy = mapped["strategy"]
                    a.reason = mapped["reason"]
                    a.dependencies = mapped["dependencies"]

        # Convert disabled actions to models
        disabled_models = [
            DisabledActionModel(
                task=da.get("task", "MainTask"),
                file=da.get("file", ""),
                originalStep=da.get("originalStep", 0),
                command=da.get("command", "Unknown"),
                action=da.get("action", "Execute"),
                attributes=da.get("attributes", {}),
                location=da.get("location"),
                parent=da.get("parent"),
                reason=da.get("reason", "Action was disabled in A360")
            )
            for da in disabled_actions
        ]

        # Extract variables across all tasks
        all_variables = []
        seen_var_names = set()
        for task_name, _, _ in cleaned_taskbots_data:
            raw_data = raw_data_map.get(task_name, {})
            task_actions_raw = [a.model_dump() for a in self.actions if a.task == task_name]
            v_list = VariableAnalyzer.extract_and_analyze_variables(raw_data, task_actions_raw, task_name)
            for v in v_list:
                key = f"{v.scope}_{v.name}"
                if key not in seen_var_names:
                    seen_var_names.add(key)
                    all_variables.append(v)

        # Build task models
        task_inventory = [
            {"name": t_name, "path": s_file, "is_main": idx == 0}
            for idx, (t_name, s_file, _) in enumerate(cleaned_taskbots_data)
        ]
        tasks = TaskAnalyzer.analyze_tasks(task_inventory, self.actions)

        # Extract dependencies
        dependencies = DependencyAnalyzer.extract_dependencies(self.actions)

        # Calculate statistics
        total_actions = len(self.actions)
        cloud_count = sum(1 for a in self.actions if a.cloudOrDesktop == "Power Automate Cloud")
        desktop_count = sum(1 for a in self.actions if a.cloudOrDesktop == "Power Automate Desktop")
        hybrid_count = sum(1 for a in self.actions if a.cloudOrDesktop == "Hybrid")
        manual_count = sum(1 for a in self.actions if a.cloudOrDesktop == "Manual Review")

        platform_dist = {}
        if total_actions > 0:
            platform_dist = {
                "Power Automate Cloud": round((cloud_count / total_actions) * 100, 1),
                "Power Automate Desktop": round((desktop_count / total_actions) * 100, 1),
                "Hybrid": round((hybrid_count / total_actions) * 100, 1),
                "Manual Review": round((manual_count / total_actions) * 100, 1),
            }

        complexity_dist = {}
        if total_actions > 0:
            low_c = sum(1 for a in self.actions if a.migrationComplexity == "Low")
            med_c = sum(1 for a in self.actions if a.migrationComplexity == "Medium")
            high_c = sum(1 for a in self.actions if a.migrationComplexity == "High")
            complexity_dist = {
                "Low": round((low_c / total_actions) * 100, 1),
                "Medium": round((med_c / total_actions) * 100, 1),
                "High": round((high_c / total_actions) * 100, 1),
            }

        stats = StatisticsModel(
            totalWorkflows=1,
            totalTasks=len(tasks),
            totalActions=total_actions,
            cloudActions=cloud_count,
            desktopActions=desktop_count,
            hybridActions=hybrid_count,
            manualReviewActions=manual_count,
            totalVariables=len(all_variables),
            totalSubtasks=max(0, len(tasks) - 1),
            totalDisabledActions=len(disabled_models),
            platformDistribution=platform_dist,
            complexityDistribution=complexity_dist
        )

        return WorkflowModel(
            workflow=WorkflowInfo(
                id=workflow_id,
                name=workflow_name,
                source="Automation Anywhere A360"
            ),
            tasks=tasks,
            actions=self.actions,
            variables=all_variables,
            dependencies=dependencies,
            disabledActions=disabled_models,
            statistics=stats
        )
