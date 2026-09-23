import re
from typing import Dict, Any, List, Optional, Tuple, Set
from backend.models.workflow import WorkflowModel, TaskModel
from backend.models.action import ActionModel
from backend.migration.excel_mapping_db import ExcelMappingDB

class CentricityAnalyzer:
    """
    Two-pass context-aware architecture compiler:
    1. Analyzes whether the automation (overall and per task/sub-bot) is Desktop-Centric, Cloud-Centric, or Hybrid.
    2. Harmonizes actions according to the target runtime centricity:
       - If Desktop-Centric: maps all compatible actions to native Power Automate Desktop actions.
       - If Cloud-Centric: maps all compatible actions to native Power Automate Cloud connectors/expressions.
       - If Hybrid: optimizes each task according to its specific task-level centricity.
    """

    # Packages/Commands that strictly require on-premises desktop client software, local OS access, or desktop peripherals
    DESKTOP_MANDATORY_PACKAGES = {
        "sap", "sapgui", "application", "browser", "recorder", "capture", "objectcloning",
        "window", "mouse", "keystroke", "keystrokes", "simulatekeystrokes", "clipboard",
        "terminalemulator", "terminal", "mainframe", "citrix", "pythonscript", "vbscript",
        "powershell", "system", "process", "printer", "dll", "service", "registry",
        "workload", "queue", "exceladvanced", "excelbasic", "word", "screencapture", "ocr"
    }

    # Packages/Connectors that are strictly Cloud-native in Power Automate
    CLOUD_MANDATORY_PACKAGES = {
        "approvals", "cloudapprovals", "dataverse", "commondataservice"
    }

    # Universal / Dual-compatible packages that exist natively in both Cloud and Desktop
    DUAL_COMPATIBLE_PACKAGES = {
        "if", "loop", "string", "number", "datetime", "delay", "errorhandler",
        "variable", "variables", "list", "dictionary", "record", "table", "file",
        "folder", "filesystem", "email", "restwebservice", "rest", "http",
        "json", "xml", "csv", "log", "logtofile", "logfile", "write", "messagebox",
        "prompt", "database", "sql", "excel", "excelbasic"
    }

    @classmethod
    def analyze_and_harmonize(cls, workflow: WorkflowModel) -> WorkflowModel:
        """
        Main entrypoint: analyzes workflow and task centricities, then harmonizes actions and updates statistics.
        """
        if not workflow.actions:
            return workflow

        # Step 1: Analyze Centricity per Task
        task_centricities: Dict[str, Dict[str, Any]] = {}
        for task in workflow.tasks:
            task_centricities[task.name] = cls._analyze_task_centricity(task.name, workflow.actions)
            task.centricity = task_centricities[task.name]["centricity"]
            task.cloudOrDesktop = (
                "Power Automate Desktop" if task.centricity == "Desktop-Centric"
                else "Power Automate Cloud" if task.centricity == "Cloud-Centric"
                else "Hybrid"
            )

        # Step 2: Determine Workflow-Level Bot Centricity
        workflow_centricity, reason, metrics = cls._determine_overall_centricity(task_centricities, workflow.actions)
        workflow.botCentricity = workflow_centricity
        workflow.botCentricityReason = reason
        workflow.centricityMetrics = metrics

        # Step 3: Harmonize Actions According to Centricity
        mapping_db = ExcelMappingDB.get_instance()
        for action in workflow.actions:
            task_info = task_centricities.get(action.task, {"centricity": workflow_centricity})
            if workflow_centricity == "Cloud-Centric":
                effective_centricity = "Cloud-Centric"
            elif workflow_centricity == "Desktop-Centric":
                effective_centricity = "Desktop-Centric"
            else:
                effective_centricity = task_info.get("centricity", workflow_centricity)

            cls._harmonize_single_action(action, effective_centricity, mapping_db)

        # Step 4: Recalculate Statistics
        cls._recalculate_statistics(workflow)

        return workflow

    @classmethod
    def _analyze_task_centricity(cls, task_name: str, actions: List[ActionModel]) -> Dict[str, Any]:
        """
        Analyzes a single task's actions to determine if it is Desktop-Centric or Cloud-Centric.
        """
        task_actions = [a for a in actions if a.task == task_name and not a.isDisabled]
        if not task_actions:
            # Fallback to all actions for this task including disabled
            task_actions = [a for a in actions if a.task == task_name]

        desktop_mandatory = []
        cloud_mandatory = []
        dual_compatible = []
        hybrid_calls = []

        for a in task_actions:
            cmd_norm = a.command.lower().replace(" ", "").replace("_", "")
            op_norm = (a.operation or "").lower().replace(" ", "").replace("_", "")

            # Child bot invocation check
            if cmd_norm in ("runtask", "taskbot", "subtask") or op_norm in ("run", "runtask"):
                hybrid_calls.append(a)
                continue

            # Check if desktop mandatory
            if any(dm in cmd_norm for dm in cls.DESKTOP_MANDATORY_PACKAGES):
                # Distinguish REST Web Service from generic "service"
                if "webservice" in cmd_norm or "rest" in cmd_norm or "soap" in cmd_norm:
                    dual_compatible.append(a)
                else:
                    desktop_mandatory.append(a)
            elif any(cm in cmd_norm for cm in cls.CLOUD_MANDATORY_PACKAGES):
                cloud_mandatory.append(a)
            else:
                dual_compatible.append(a)

        # Centricity Decision:
        # If the task requires ANY desktop-mandatory action, it MUST execute in Power Automate Desktop.
        if len(desktop_mandatory) > 0:
            centricity = "Desktop-Centric"
            reasons = list({a.command for a in desktop_mandatory[:4]})
            reason = f"Requires local desktop client execution ({', '.join(reasons)})."
        elif len(cloud_mandatory) > 0:
            centricity = "Cloud-Centric"
            reason = "Serverless cloud execution with Cloud connectors."
        elif len(hybrid_calls) > 0 and len(dual_compatible) == 0:
            centricity = "Hybrid"
            reason = "Pure orchestrator invoking child sub-bots."
        else:
            # Only dual-compatible and logical actions: Pure cloud-eligible execution
            has_local_paths = False
            for a in dual_compatible:
                attr_str = str(a.attributes).lower()
                if re.search(r'[c-zC-Z]:\\', attr_str) or "\\\\" in attr_str:
                    has_local_paths = True
                    break

            centricity = "Cloud-Centric"
            if has_local_paths:
                reason = "Cloud-native flow with SharePoint/OneDrive cloud modernization for local file/log paths."
            else:
                reason = "Pure logical, API, & cloud notification processing without desktop dependencies."

        return {
            "centricity": centricity,
            "reason": reason,
            "desktop_mandatory_count": len(desktop_mandatory),
            "cloud_mandatory_count": len(cloud_mandatory),
            "dual_compatible_count": len(dual_compatible),
            "hybrid_calls_count": len(hybrid_calls),
            "total_actions": len(task_actions),
            "desktop_examples": [a.command for a in desktop_mandatory[:3]]
        }

    @classmethod
    def _determine_overall_centricity(
        cls,
        task_centricities: Dict[str, Dict[str, Any]],
        actions: List[ActionModel]
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Determines overall bot architecture affinity across all tasks.
        """
        total_desktop_mand = sum(t["desktop_mandatory_count"] for t in task_centricities.values())
        total_cloud_mand = sum(t["cloud_mandatory_count"] for t in task_centricities.values())
        total_dual = sum(t["dual_compatible_count"] for t in task_centricities.values())
        total_hybrid = sum(t["hybrid_calls_count"] for t in task_centricities.values())

        desktop_tasks = [t for t, data in task_centricities.items() if data["centricity"] == "Desktop-Centric"]
        cloud_tasks = [t for t, data in task_centricities.items() if data["centricity"] == "Cloud-Centric"]

        all_desktop_examples = []
        for t in task_centricities.values():
            all_desktop_examples.extend(t.get("desktop_examples", []))
        unique_desktop_examples = list(dict.fromkeys(all_desktop_examples))[:4]

        metrics = {
            "desktop_mandatory_actions": total_desktop_mand,
            "cloud_mandatory_actions": total_cloud_mand,
            "dual_compatible_actions": total_dual,
            "hybrid_calls": total_hybrid,
            "desktop_tasks_count": len(desktop_tasks),
            "cloud_tasks_count": len(cloud_tasks),
            "total_tasks": len(task_centricities),
        }

        # Case 1: Pure Desktop-Centric (all tasks or single bot with desktop mandatory dependencies)
        if len(cloud_tasks) == 0 and total_desktop_mand > 0:
            examples_str = f" ({', '.join(unique_desktop_examples)})" if unique_desktop_examples else ""
            reason = (
                f"Desktop-Centric Architecture: The automation contains {total_desktop_mand} action(s) requiring "
                f"local desktop application access{examples_str}. All {total_dual} compatible control flows and expressions "
                f"are harmonized to native Power Automate Desktop actions."
            )
            return "Desktop-Centric", reason, metrics

        # Case 2: Pure Cloud-Centric (zero desktop dependencies across all tasks)
        if total_desktop_mand == 0:
            reason = (
                f"Cloud-Centric Architecture: 100% serverless automation with zero on-premises desktop dependencies. "
                f"All {total_dual + total_cloud_mand} actions are harmonized to native Power Automate Cloud connectors and expressions."
            )
            return "Cloud-Centric", reason, metrics

        # Case 3: Hybrid Architecture (Multi-bot solution with mixed Cloud & Desktop tasks)
        reason = (
            f"Hybrid Architecture: Multi-bot solution combines {len(cloud_tasks)} Cloud-Centric task(s) "
            f"with {len(desktop_tasks)} Desktop-Centric worker bot(s). Actions are optimized per task."
        )
        return "Hybrid", reason, metrics

    @classmethod
    def _harmonize_single_action(
        cls,
        action: ActionModel,
        effective_centricity: str,
        mapping_db: ExcelMappingDB
    ):
        """
        Harmonizes a single action based on the effective centricity of its containing task/bot:
        - If Desktop-Centric and action has a Desktop equivalent -> maps to Power Automate Desktop.
        - If Cloud-Centric and action has a Cloud equivalent -> maps to Power Automate Cloud.
        """
        cmd_clean = action.command.strip()
        cmd_norm = cmd_clean.lower().replace(" ", "").replace("_", "")
        op_clean = (action.operation or "").strip()
        op_norm = op_clean.lower().replace(" ", "").replace("_", "")

        # 1. Preserve child bot orchestration calls
        if cmd_norm in ("runtask", "taskbot", "subtask") or op_norm in ("run", "runtask"):
            action.cloudOrDesktop = "Hybrid"
            if effective_centricity == "Desktop-Centric":
                action.powerAutomateAction = "Run Desktop Flow (or Subroutine)"
                action.padAction = "Run Desktop Flow"
                action.padCategory = "Flow control"
            else:
                action.powerAutomateAction = "Run a flow built with Power Automate for desktop"
            action.migrationStrategy = "Subflow Call"
            action.reason = "Hierarchical sub-bot execution."
            return

        # 2. Preserve Manual Review if action was completely unrecognized or proprietary
        if action.cloudOrDesktop == "Manual Review" and (not action.padAction or "Manual Review" in action.padAction):
            return

        # Lookup both PAD and Cloud actions from mapping DB
        db_entry = mapping_db.find_mapping(cmd_clean, op_clean)
        pad_action_candidate = action.padAction or db_entry.get("pad_action", "")
        cloud_action_candidate = action.cloudAction or db_entry.get("cloud_action", "")
        pad_cat = action.padCategory or db_entry.get("pad_category", "Custom")

        # -------------------------------------------------------------
        # BRANCH A: DESKTOP-CENTRIC HARMONIZATION
        # -------------------------------------------------------------
        if effective_centricity == "Desktop-Centric":
            # Check if this action can run in Power Automate Desktop
            can_run_on_desktop = cls._is_valid_pad_action(pad_action_candidate, cmd_norm)

            if can_run_on_desktop:
                refined_pad_action = cls._refine_pad_action(cmd_norm, op_norm, pad_action_candidate)
                refined_pad_cat = cls._refine_pad_category(cmd_norm, pad_cat)

                action.cloudOrDesktop = "Power Automate Desktop"
                action.powerAutomateAction = refined_pad_action
                action.padAction = refined_pad_action
                action.padCategory = refined_pad_cat
                action.migrationStrategy = "Desktop Native"
                action.reason = (
                    f"Desktop-Centric Optimization: Task '{action.task}' executes in Power Automate Desktop. "
                    f"Using native PAD action '{refined_pad_action}' to maintain flow cohesion without cloud round-trips."
                )
            else:
                # Cannot run on desktop (pure cloud connector)
                action.cloudOrDesktop = "Power Automate Cloud"
                action.powerAutomateAction = cloud_action_candidate or action.powerAutomateAction
                action.reason = f"Cloud connector retained: '{cmd_clean}' has no native desktop runtime equivalent."

        # -------------------------------------------------------------
        # BRANCH B: CLOUD-CENTRIC HARMONIZATION
        # -------------------------------------------------------------
        elif effective_centricity == "Cloud-Centric":
            # Check if this action can run in Power Automate Cloud
            can_run_on_cloud = cls._is_valid_cloud_action(cloud_action_candidate, cmd_norm)

            if can_run_on_cloud:
                refined_cloud_action = cls._refine_cloud_action(cmd_norm, op_norm, cloud_action_candidate)

                action.cloudOrDesktop = "Power Automate Cloud"
                action.powerAutomateAction = refined_cloud_action
                action.cloudAction = refined_cloud_action
                action.migrationStrategy = "Cloud Native"
                action.reason = (
                    f"Cloud-Centric Optimization: Task '{action.task}' executes serverless in Power Automate Cloud. "
                    f"Using native Cloud action/expression '{refined_cloud_action}'."
                )
            else:
                # Strictly requires Desktop, but task is supposedly Cloud-Centric!
                action.cloudOrDesktop = "Power Automate Desktop"
                action.powerAutomateAction = pad_action_candidate or action.powerAutomateAction
                action.migrationStrategy = "Desktop Requirement"
                action.reason = (
                    f"Desktop dependency in Cloud Flow: '{cmd_clean}' requires on-premises Power Automate Desktop runtime."
                )

    @classmethod
    def _is_valid_pad_action(cls, pad_action: str, cmd_norm: str) -> bool:
        """Determines if a candidate PAD action is valid and executable in Power Automate Desktop."""
        if not pad_action:
            return any(d in cmd_norm for d in cls.DUAL_COMPATIBLE_PACKAGES) or any(d in cmd_norm for d in cls.DESKTOP_MANDATORY_PACKAGES)

        p_lower = pad_action.lower()
        if "no direct" in p_lower or "no native" in p_lower or p_lower in ("none", "n/a", "not supported"):
            return False
        if "manual review" in p_lower:
            return False
        return True

    @classmethod
    def _is_valid_cloud_action(cls, cloud_action: str, cmd_norm: str) -> bool:
        """Determines if a candidate Cloud action is valid and executable in Power Automate Cloud."""
        # Dual compatible packages (logic, data, email, files, logs, queues) can always run in cloud
        if any(d in cmd_norm for d in cls.DUAL_COMPATIBLE_PACKAGES) or any(c in cmd_norm for c in cls.CLOUD_MANDATORY_PACKAGES):
            return True

        if not cloud_action:
            return False

        c_lower = cloud_action.lower()
        if "no direct" in c_lower or "no native" in c_lower or c_lower in ("none", "n/a", "not supported"):
            return False
        if "manual review" in c_lower:
            return False
        return True

    @classmethod
    def _refine_pad_action(cls, cmd_norm: str, op_norm: str, default_action: str) -> str:
        """Produces precise, idiomatic Power Automate Desktop action names."""
        if "if" in cmd_norm or cmd_norm == "condition":
            return "If / If variable"
        if "loop" in cmd_norm:
            if "while" in op_norm or "condition" in op_norm:
                return "Loop condition"
            elif "foreach" in op_norm or "each" in op_norm or "row" in op_norm or "table" in op_norm:
                return "For each"
            return "Loop / For each"
        if "string" in cmd_norm:
            if "substring" in op_norm or "subtext" in op_norm:
                return "Get subtext"
            elif "replace" in op_norm:
                return "Replace text"
            elif "split" in op_norm:
                return "Split text"
            elif "trim" in op_norm:
                return "Trim text"
            elif "length" in op_norm:
                return "Get text length"
            elif "case" in op_norm or "upper" in op_norm or "lower" in op_norm:
                return "Change text case"
            return "Text manipulation (Get subtext / Replace text / Trim text)"
        if "number" in cmd_norm:
            if "add" in op_norm or "increase" in op_norm:
                return "Increase variable"
            elif "sub" in op_norm or "decrease" in op_norm:
                return "Decrease variable"
            elif "calc" in op_norm or "round" in op_norm:
                return "Calculate mathematical expression"
            return "Increase variable / Calculate"
        if "datetime" in cmd_norm:
            if "now" in op_norm or "current" in op_norm:
                return "Get current date and time"
            elif "format" in op_norm or "convert" in op_norm:
                return "Convert datetime to text"
            elif "add" in op_norm or "sub" in op_norm:
                return "Add to datetime / Subtract from datetime"
            return "Convert datetime to text"
        if "delay" in cmd_norm:
            return "Wait"
        if "error" in cmd_norm or "try" in cmd_norm:
            return "On block error"
        if "variable" in cmd_norm or "assign" in cmd_norm:
            return "Set variable"
        if "list" in cmd_norm:
            return "Create new list / Add item to list"
        if "log" in cmd_norm:
            return "Write text to file"
        if "file" in cmd_norm:
            if "copy" in op_norm:
                return "Copy file"
            elif "delete" in op_norm:
                return "Delete file"
            elif "move" in op_norm or "rename" in op_norm:
                return "Move file / Rename file"
            elif "read" in op_norm:
                return "Read text from file"
            elif "write" in op_norm:
                return "Write text to file"
            return "Copy file / Delete file / Read text from file"
        if "folder" in cmd_norm:
            return "Create folder / Get files in folder"
        if "email" in cmd_norm:
            return "Send email / Retrieve email messages (Outlook / Exchange)"
        if "rest" in cmd_norm or "webservice" in cmd_norm or "http" in cmd_norm:
            return "Invoke web service"
        if "json" in cmd_norm:
            return "Convert JSON to custom object"
        if "xml" in cmd_norm:
            return "Execute XPath expression"
        if "messagebox" in cmd_norm:
            return "Display message"
        if "prompt" in cmd_norm:
            return "Display input dialog"
        if "workload" in cmd_norm or "queue" in cmd_norm:
            return "Add work queue item / Process work queue items"

        return default_action or f"PAD Action ({cmd_norm})"

    @classmethod
    def _refine_pad_category(cls, cmd_norm: str, default_cat: str) -> str:
        """Determines idiomatic PAD Category for the action."""
        if "if" in cmd_norm:
            return "Conditionals"
        if "loop" in cmd_norm:
            return "Loops"
        if "string" in cmd_norm:
            return "Text"
        if "number" in cmd_norm or "variable" in cmd_norm or "list" in cmd_norm or "json" in cmd_norm:
            return "Variables"
        if "datetime" in cmd_norm:
            return "DateTime"
        if "delay" in cmd_norm or "error" in cmd_norm:
            return "Flow control"
        if "log" in cmd_norm or "file" in cmd_norm:
            return "File"
        if "folder" in cmd_norm:
            return "Folder"
        if "email" in cmd_norm:
            return "Email / Outlook"
        if "rest" in cmd_norm or "webservice" in cmd_norm or "http" in cmd_norm:
            return "Web services"
        if "xml" in cmd_norm:
            return "XML"
        if "messagebox" in cmd_norm or "prompt" in cmd_norm:
            return "Message boxes"
        if "workload" in cmd_norm or "queue" in cmd_norm:
            return "Work queues"

        return default_cat or "Custom"

    @classmethod
    def _refine_cloud_action(cls, cmd_norm: str, op_norm: str, default_action: str) -> str:
        """Produces precise, idiomatic Power Automate Cloud action names."""
        if "if" in cmd_norm or cmd_norm == "condition":
            return "Condition"
        if "loop" in cmd_norm:
            if "while" in op_norm:
                return "Do until"
            return "Apply to each"
        if "string" in cmd_norm:
            if "substring" in op_norm or "subtext" in op_norm:
                return "substring() expression in Compose"
            elif "replace" in op_norm:
                return "replace() expression in Compose"
            elif "split" in op_norm:
                return "split() expression in Compose"
            elif "trim" in op_norm:
                return "trim() expression in Compose"
            return "String expressions in Compose (substring, replace, split)"
        if "number" in cmd_norm:
            return "Math expressions in Compose (add, sub, mul, div)"
        if "datetime" in cmd_norm:
            return "Convert time zone / formatDateTime() expression"
        if "delay" in cmd_norm:
            return "Delay"
        if "error" in cmd_norm or "try" in cmd_norm:
            return "Scope + 'Configure run after'"
        if "variable" in cmd_norm or "assign" in cmd_norm:
            return "Initialize variable / Set variable"
        if "email" in cmd_norm:
            return "Office 365 Outlook - Send an email (V2)"
        if "rest" in cmd_norm or "webservice" in cmd_norm or "http" in cmd_norm:
            return "HTTP"
        if "json" in cmd_norm:
            return "Parse JSON"
        if "xml" in cmd_norm:
            return "xpath() expression in Compose"
        if "log" in cmd_norm:
            return "OneDrive / SharePoint - Append to file (or Dataverse log)"
        if "file" in cmd_norm or "folder" in cmd_norm:
            return "SharePoint / OneDrive for Business Connector"
        if "messagebox" in cmd_norm:
            return "Microsoft Teams - Post message in chat or channel"
        if "prompt" in cmd_norm:
            return "Microsoft Teams - Post adaptive card and wait for response"
        if "workload" in cmd_norm or "queue" in cmd_norm:
            return "Microsoft Dataverse - Add a new row (Work Queue) / SharePoint list"
        if "excel" in cmd_norm:
            return "Excel Online (Business) Connector"
        if "word" in cmd_norm:
            return "Word Online (Business) Connector"
        if "csv" in cmd_norm:
            return "Compose - Parse CSV / Select"
        if "database" in cmd_norm or "sql" in cmd_norm:
            return "SQL Server Connector (Cloud via On-Premises Data Gateway)"

        return default_action or f"Cloud Action ({cmd_norm})"

    @classmethod
    def _recalculate_statistics(cls, workflow: WorkflowModel):
        """Recalculates workflow statistics after centricity harmonization."""
        active_actions = [a for a in workflow.actions if not a.isDisabled]
        total_active = len(active_actions)

        cloud_count = sum(1 for a in active_actions if a.cloudOrDesktop == "Power Automate Cloud")
        desktop_count = sum(1 for a in active_actions if a.cloudOrDesktop == "Power Automate Desktop")
        hybrid_count = sum(1 for a in active_actions if a.cloudOrDesktop == "Hybrid")
        manual_count = sum(1 for a in active_actions if a.cloudOrDesktop == "Manual Review")

        s = workflow.statistics
        s.totalActions = total_active
        s.cloudActions = cloud_count
        s.desktopActions = desktop_count
        s.hybridActions = hybrid_count
        s.manualReviewActions = manual_count

        if total_active > 0:
            s.platformDistribution = {
                "Power Automate Desktop": round((desktop_count / total_active) * 100, 1),
                "Power Automate Cloud": round((cloud_count / total_active) * 100, 1),
                "Hybrid": round((hybrid_count / total_active) * 100, 1),
                "Manual Review": round((manual_count / total_active) * 100, 1),
            }
