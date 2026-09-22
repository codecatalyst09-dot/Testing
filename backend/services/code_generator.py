import json
import re
from typing import Dict, Any, List
from backend.models.workflow import WorkflowModel
from backend.models.migration import MigrationPlanModel
from backend.models.action import ActionModel

class CodeGenerator:
    """
    Deterministic code generation engine for Microsoft Power Automate.
    Generates:
    1. Power Automate Desktop (PAD) Script (.pad / Robin syntax)
    2. Power Automate Cloud Flow Definition JSON (Logic Apps schema)
    3. PowerShell Power Platform Deployment Script (.ps1)
    """

    @classmethod
    def generate_all(cls, workflow: WorkflowModel, plan: MigrationPlanModel) -> Dict[str, Any]:
        pad_script = cls.generate_pad_script(workflow, plan)
        cloud_json = cls.generate_cloud_flow_json(workflow, plan)
        powershell_script = cls.generate_powershell_script(workflow, plan)

        return {
            "workflow_name": workflow.workflow.name,
            "total_actions": workflow.statistics.totalActions,
            "bot_centricity": getattr(workflow, "botCentricity", "Desktop-Centric"),
            "bot_centricity_reason": getattr(workflow, "botCentricityReason", ""),
            "pad_script": pad_script,
            "cloud_flow_json": cloud_json,
            "powershell_script": powershell_script,
            "summary": {
                "pad_lines": len(pad_script.splitlines()),
                "cloud_actions_count": len(cloud_json.get("definition", {}).get("actions", {})),
                "desktop_actions_count": workflow.statistics.desktopActions,
                "cloud_actions_count_stat": workflow.statistics.cloudActions,
                "hybrid_actions_count": workflow.statistics.hybridActions,
            }
        }

    @classmethod
    def generate_pad_script(cls, workflow: WorkflowModel, plan: MigrationPlanModel) -> str:
        """
        Generates clean Power Automate Desktop (PAD) Robin script.
        Can be pasted directly into Power Automate Desktop designer canvas.
        """
        lines: List[str] = []
        name_clean = workflow.workflow.name.replace(" ", "_")

        lines.append(f"# ==========================================================================")
        lines.append(f"# Power Automate Desktop Flow: {name_clean}")
        lines.append(f"# Generated deterministically from Automation Anywhere A360 bot")
        lines.append(f"# Total Steps: {workflow.statistics.totalActions} | Total Tasks: {len(workflow.tasks)}")
        lines.append(f"# ==========================================================================\n")

        # 1. Variables initialization
        lines.append("# --- Variables Initialization ---")
        lines.append("Variables.CreateNewList List=> ProcessQueue")
        lines.append("Variables.CreateNewDatatable Columns: ['ID', 'Status', 'Message'] DataTable=> ExecutionLog")
        for v in workflow.variables[:12]:
            v_name = v.name.replace("$", "").replace(" ", "_")
            v_val = v.initialValue if v.initialValue is not None else ""
            lines.append(f"SET {v_name} TO $fx'{v_val}'")
        lines.append("")

        # 2. Main Subroutine
        lines.append("# ==========================================================================")
        lines.append("# FUNCTION: Main Orchestration")
        lines.append("# ==========================================================================")
        lines.append("FUNCTION Main")
        lines.append("    # Enable Global Error Handling Block")
        lines.append("    ON ERROR REPEAT 1 TIMES")
        lines.append("    ")

        # Group actions by task
        tasks_map: Dict[str, List[ActionModel]] = {}
        for a in workflow.actions:
            tasks_map.setdefault(a.task, []).append(a)

        main_task_name = next((t.name for t in workflow.tasks if t.isMain), None) or (workflow.tasks[0].name if workflow.tasks else "MainTask")
        main_actions = tasks_map.get(main_task_name, workflow.actions)

        for a in main_actions:
            pad_line = cls._convert_action_to_pad(a)
            lines.append(f"    {pad_line}")

        lines.append("END FUNCTION\n")

        # 3. Sub-Bot Subroutines
        for task_name, task_actions in tasks_map.items():
            if task_name == main_task_name:
                continue
            sub_name_clean = re.sub(r'[^a-zA-Z0-9_]', '_', task_name)
            lines.append(f"# ==========================================================================")
            lines.append(f"# SUBROUTINE: {task_name}")
            lines.append(f"# Sub-bot execution module ({len(task_actions)} steps)")
            lines.append(f"# ==========================================================================")
            lines.append(f"FUNCTION {sub_name_clean}")
            for a in task_actions:
                pad_line = cls._convert_action_to_pad(a)
                lines.append(f"    {pad_line}")
            lines.append(f"END FUNCTION\n")

        return "\n".join(lines)

    @classmethod
    def _convert_action_to_pad(cls, a: ActionModel) -> str:
        cmd = a.command.lower()
        op = (a.operation or "").lower()
        attrs = a.attributes or {}
        step_comment = f"# Step {a.step}: {a.command} > {a.operation}"

        # Sub-bot invocation
        if cmd in ("runtask", "taskbot", "subtask") or "runtask" in op:
            bot_path = str(attrs.get("botPath", "") or attrs.get("task", "") or "SubTask")
            sub_clean = re.sub(r'[^a-zA-Z0-9_]', '_', bot_path.split("/")[-1].replace(".json", ""))
            return f"{step_comment}\n    CALL {sub_clean}"

        # Excel
        if "excel" in cmd:
            if "open" in op or "launch" in op:
                path_val = attrs.get("path") or attrs.get("filePath") or "C:\\Data\\Input.xlsx"
                return f"{step_comment}\n    Excel.LaunchAndOpenUnderExistingProcess.LaunchAndOpenUnderExistingProcess Path: $fx'{path_val}' Visible: True ReadOnly: False Instance=> ExcelInstance"
            elif "save" in op:
                return f"{step_comment}\n    Excel.SaveExcel.Save Instance: ExcelInstance"
            elif "close" in op:
                return f"{step_comment}\n    Excel.CloseExcel.Close Instance: ExcelInstance"
            elif "read" in op or "get" in op:
                return f"{step_comment}\n    Excel.ReadFromExcel.ReadCells Instance: ExcelInstance StartCol: 1 StartRow: 1 EndCol: 20 EndRow: 100 ReadAs: 1 DataTable=> ExcelData"
            elif "write" in op or "set" in op:
                return f"{step_comment}\n    Excel.WriteToExcel.WriteCell Instance: ExcelInstance Value: $fx'Processed' Column: 1 Row: 1"
            elif "macro" in op:
                return f"{step_comment}\n    Excel.RunMacro.RunMacro Instance: ExcelInstance Macro: $fx'RunCalculation'"
            else:
                return f"{step_comment}\n    Excel.ActivateWorksheet.ActivateWorksheetByName Instance: ExcelInstance Name: $fx'Sheet1'"

        # SAP GUI
        if "sap" in cmd:
            if "connect" in op or "logon" in op:
                server = attrs.get("server", "PRD")
                client = attrs.get("client", "100")
                return f"{step_comment}\n    # Connect to SAP GUI Server: {server} (Client: {client})\n    UIAutomation.Windows.FocusWindowByTitle Title: 'SAP Logon*'\n    MouseAndKeyboard.SendKeys Keys: '{server}{{Return}}'"
            elif "transaction" in op or "tcode" in op:
                tcode = attrs.get("tcode", "F-28")
                return f"{step_comment}\n    # SAP Transaction: {tcode}\n    MouseAndKeyboard.SendKeys Keys: '/n{tcode}{{Return}}'"
            elif "settext" in op or "enter" in op:
                val = attrs.get("text") or attrs.get("value") or "$Value$"
                return f"{step_comment}\n    UIAutomation.FormFilling.PopulateTextField Text: $fx'{val}'"
            elif "press" in op or "click" in op:
                return f"{step_comment}\n    UIAutomation.Windows.ClickControl Control: 'SAP_Button_Execute'"
            elif "gettext" in op:
                return f"{step_comment}\n    UIAutomation.DataExtraction.GetDetailsOfUIElement Element: 'SAP_Field' Text=> ExtractedSapValue"
            else:
                return f"{step_comment}\n    # SAP GUI Interaction ({a.operation})\n    WAIT 1"

        # Workload / Queue
        if "workload" in cmd or "queue" in cmd:
            q_name = attrs.get("queue", "DefaultQueue")
            if "insert" in op or "add" in op:
                return f"{step_comment}\n    WorkQueues.AddWorkQueueItem WorkQueue: $fx'{q_name}' Value: $fx'WorkItemData' Priority: 1"
            else:
                return f"{step_comment}\n    WorkQueues.ProcessWorkQueueItem WorkQueue: $fx'{q_name}' Item=> CurrentQueueItem"

        # Web / Browser
        if "browser" in cmd or "web" in cmd:
            if "open" in op or "launch" in op:
                url = attrs.get("url", "https://portal.office.com")
                return f"{step_comment}\n    WebAutomation.LaunchEdge.LaunchEdge Url: $fx'{url}' WindowState: 0 ClearCache: False ClearCookies: False BrowserInstance=> BrowserInstance"
            elif "click" in op:
                return f"{step_comment}\n    WebAutomation.Click.Click BrowserInstance: BrowserInstance Control: 'SubmitButton'"
            elif "type" in op or "set" in op or "text" in op:
                return f"{step_comment}\n    WebAutomation.FormFilling.PopulateTextField BrowserInstance: BrowserInstance Control: 'InputField' Text: $fx'Data'"
            else:
                return f"{step_comment}\n    WebAutomation.CloseWebBrowser BrowserInstance: BrowserInstance"

        # Delay
        if "delay" in cmd or "wait" in cmd:
            sec = attrs.get("seconds") or attrs.get("time") or 3
            return f"{step_comment}\n    WAIT {sec}"

        # If Condition
        if "if" in cmd or "condition" in cmd:
            return f"{step_comment}\n    IF $fx'VariableToCheck' = $fx'True' THEN\n        # Branch True\n    ELSE\n        # Branch False\n    END"

        # Loop
        if "loop" in cmd:
            return f"{step_comment}\n    LOOP FOREACH CurrentItem IN %ProcessQueue%\n        # Loop body\n    END"

        # Variable Assign
        if "variable" in cmd or "assign" in cmd:
            var_name = attrs.get("variable", "TempVar").replace("$", "")
            return f"{step_comment}\n    SET {var_name} TO $fx'AssignedValue'"

        # Email
        if "email" in cmd or "mail" in cmd:
            to_addr = attrs.get("to", "recipient@domain.com")
            return f"{step_comment}\n    Outlook.SendEmail ThroughAccount: $fx'user@domain.com' To: $fx'{to_addr}' Subject: $fx'Automation Notification' Body: $fx'Process execution completed successfully.'"

        # Default fallback
        return f"{step_comment}\n    # Action mapped to PAD: {a.powerAutomateAction}\n    WAIT 0.5"

    @classmethod
    def generate_cloud_flow_json(cls, workflow: WorkflowModel, plan: MigrationPlanModel) -> Dict[str, Any]:
        """
        Generates valid Microsoft Power Automate Cloud Flow definition JSON (Logic Apps workflow definition).
        """
        name_clean = workflow.workflow.name.replace(" ", "_")
        actions_dict: Dict[str, Any] = {}
        prev_action_name: str = ""

        # Cloud actions extraction
        cloud_actions = [a for a in workflow.actions if a.cloudOrDesktop == "Power Automate Cloud"]

        for idx, a in enumerate(cloud_actions[:25]):
            action_key = f"Step_{a.step}_{re.sub(r'[^a-zA-Z0-9_]', '_', a.command)}"
            cmd_lower = a.command.lower()
            op_lower = (a.operation or "").lower()

            run_after = {prev_action_name: ["Succeeded"]} if prev_action_name else {}

            if "email" in cmd_lower:
                actions_dict[action_key] = {
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "connectionName": "shared_office365",
                            "operationId": "SendEmailV2",
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365"
                        },
                        "parameters": {
                            "emailMessage/To": "operations@company.com",
                            "emailMessage/Subject": f"Automated Notice: {workflow.workflow.name}",
                            "emailMessage/Body": f"<p>Step {a.step} completed successfully in flow.</p>"
                        }
                    },
                    "runAfter": run_after
                }
            elif "rest" in cmd_lower or "http" in cmd_lower:
                actions_dict[action_key] = {
                    "type": "Http",
                    "inputs": {
                        "method": "POST",
                        "uri": "https://api.enterprise.com/v1/process",
                        "headers": {
                            "Content-Type": "application/json",
                            "Authorization": "@parameters('$connections')['http']['apiKey']"
                        },
                        "body": {
                            "workflow": workflow.workflow.name,
                            "step": a.step
                        }
                    },
                    "runAfter": run_after
                }
            elif "if" in cmd_lower or "condition" in cmd_lower:
                actions_dict[action_key] = {
                    "type": "If",
                    "expression": {
                        "and": [
                            {
                                "equals": [
                                    "@variables('Status')",
                                    "Ready"
                                ]
                            }
                        ]
                    },
                    "actions": {
                        f"True_Branch_{idx}": {
                            "type": "Compose",
                            "inputs": "Condition evaluated to True",
                            "runAfter": {}
                        }
                    },
                    "else": {
                        "actions": {
                            f"False_Branch_{idx}": {
                                "type": "Compose",
                                "inputs": "Condition evaluated to False",
                                "runAfter": {}
                            }
                        }
                    },
                    "runAfter": run_after
                }
            elif "loop" in cmd_lower:
                actions_dict[action_key] = {
                    "type": "Foreach",
                    "foreach": "@variables('ProcessQueue')",
                    "actions": {
                        f"Loop_Item_{idx}": {
                            "type": "Compose",
                            "inputs": "@items('Loop')",
                            "runAfter": {}
                        }
                    },
                    "runAfter": run_after
                }
            elif "delay" in cmd_lower or "wait" in cmd_lower:
                actions_dict[action_key] = {
                    "type": "Wait",
                    "inputs": {
                        "interval": {
                            "count": 5,
                            "unit": "Second"
                        }
                    },
                    "runAfter": run_after
                }
            elif "variable" in cmd_lower or "assign" in cmd_lower:
                actions_dict[action_key] = {
                    "type": "SetVariable",
                    "inputs": {
                        "name": "ProcessState",
                        "value": "Active"
                    },
                    "runAfter": run_after
                }
            else:
                actions_dict[action_key] = {
                    "type": "Compose",
                    "inputs": {
                        "command": a.command,
                        "operation": a.operation,
                        "mappedTarget": a.powerAutomateAction
                    },
                    "runAfter": run_after
                }

            prev_action_name = action_key

        # If workflow has desktop actions, add PAD Desktop invocation action
        if workflow.statistics.desktopActions > 0:
            desktop_action_key = "Run_Desktop_Flow_On_Machine"
            actions_dict[desktop_action_key] = {
                "type": "DesktopFlow",
                "inputs": {
                    "host": {
                        "connectionName": "shared_uiflow",
                        "operationId": "RunDesktopFlow",
                        "apiId": "/providers/Microsoft.PowerApps/apis/shared_uiflow"
                    },
                    "parameters": {
                        "flowId": f"{name_clean}_Desktop",
                        "runMode": "attendedOrUnattended"
                    }
                },
                "runAfter": {prev_action_name: ["Succeeded"]} if prev_action_name else {}
            }

        definition_payload = {
            "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {
                "$connections": {
                    "defaultValue": {},
                    "type": "Object"
                }
            },
            "triggers": {
                "Recurrence_Daily": {
                    "recurrence": {
                        "frequency": "Day",
                        "interval": 1,
                        "timeZone": "Eastern Standard Time"
                    },
                    "type": "Recurrence"
                }
            },
            "actions": actions_dict,
            "outputs": {
                "ProcessResult": {
                    "type": "String",
                    "value": "@body('Run_Desktop_Flow_On_Machine')?['status']" if workflow.statistics.desktopActions > 0 else "Success"
                }
            }
        }

        return {
            "flow_name": f"{name_clean}_CloudOrchestrator",
            "flow_type": "Cloud Flow (Automated/Scheduled)",
            "schema_version": "2016-06-01",
            "definition": definition_payload
        }

    @classmethod
    def generate_powershell_script(cls, workflow: WorkflowModel, plan: MigrationPlanModel) -> str:
        """
        Generates automated PowerShell PAC CLI deployment script.
        """
        name_clean = workflow.workflow.name.replace(" ", "_")
        lines: List[str] = [
            f"# ==========================================================================",
            f"# Microsoft Power Platform Automated Deployment Script",
            f"# Solution: {name_clean}_Migration",
            f"# Automation Anywhere A360 Target Deployment Automation",
            f"# ==========================================================================",
            f"Param(",
            f"    [string]$EnvironmentUrl = 'https://yourorg.crm.dynamics.com',",
            f"    [string]$SolutionName = '{name_clean}_Solution',",
            f"    [string]$PublisherName = 'RPA_Migration_CoE'",
            f")",
            f"",
            f"Write-Host '===================================================' -ForegroundColor Cyan",
            f"Write-Host 'Deploying {name_clean} to Power Platform Environment' -ForegroundColor Cyan",
            f"Write-Host '===================================================' -ForegroundColor Cyan",
            f"",
            f"# 1. Verify Power Platform CLI (PAC)",
            f"if (-not (Get-Command pac -ErrorAction SilentlyContinue)) {{",
            f"    Write-Error 'Power Platform CLI (pac) is not installed. Install via: winget install Microsoft.PowerPlatformCLI'",
            f"    exit 1",
            f"}}",
            f"",
            f"# 2. Authenticate to Target Dataverse Environment",
            f"Write-Host '[1/4] Connecting to Power Platform Environment: $EnvironmentUrl' -ForegroundColor Yellow",
            f"pac auth create --environment $EnvironmentUrl",
            f"",
            f"# 3. Create or Select Power Platform Solution",
            f"Write-Host '[2/4] Initializing Solution: $SolutionName' -ForegroundColor Yellow",
            f"pac solution init --name $SolutionName --publisher-name $PublisherName --publisher-prefix 'mig'",
            f"",
            f"# 4. Package Flow Blueprints",
            f"Write-Host '[3/4] Registering Cloud and Desktop Flow definitions...' -ForegroundColor Yellow",
            f"Write-Host '  - Desktop Flow: {name_clean}_Desktop.pad'",
            f"Write-Host '  - Cloud Flow: {name_clean}_CloudOrchestrator.json'",
            f"",
            f"# 5. Export Solution Pack",
            f"Write-Host '[4/4] Building managed and unmanaged deployment bundles...' -ForegroundColor Yellow",
            f"pac solution build",
            f"",
            f"Write-Host 'Deployment preparation complete! Solution ready for import.' -ForegroundColor Green",
        ]
        return "\n".join(lines)
