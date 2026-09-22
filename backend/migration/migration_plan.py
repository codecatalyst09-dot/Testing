from typing import List, Dict, Any
from backend.models.migration import (
    MigrationPlanModel,
    TargetArchitecture,
    TargetCloudFlow,
    TargetCloudFlowAction,
    TargetDesktopFlow,
    TargetDesktopFlowAction
)
from backend.models.action import ActionModel
from backend.models.variable import VariableModel
from backend.models.workflow import DependencyModel

class MigrationPlanBuilder:
    @staticmethod
    def build_plan(
        job_id: str,
        workflow_name: str,
        actions: List[ActionModel],
        variables: List[VariableModel],
        dependencies: List[DependencyModel]
    ) -> MigrationPlanModel:
        cloud_actions = [a for a in actions if a.cloudOrDesktop == "Power Automate Cloud"]
        desktop_actions = [a for a in actions if a.cloudOrDesktop == "Power Automate Desktop"]
        hybrid_actions = [a for a in actions if a.cloudOrDesktop == "Hybrid"]
        manual_actions = [a for a in actions if a.cloudOrDesktop == "Manual Review"]

        # Determine overall architecture type
        if len(desktop_actions) > 0 and len(cloud_actions) > 0:
            arch_type = "Hybrid (Cloud Orchestrated Desktop)"
            summary = (
                f"The automation combines cloud operations ({len(cloud_actions)} actions) "
                f"with desktop interactions ({len(desktop_actions)} actions). Recommended target is a "
                f"Power Automate Cloud Flow triggering on schedule/event, invoking a Power Automate Desktop "
                f"Flow on a registered VM/machine, and handling downstream cloud reporting and notifications."
            )
            orchestration = (
                "Cloud Flow (Trigger & Data Prep) → 'Run a flow built with Power Automate for desktop' "
                "→ Desktop Flow (Excel/UI Automation) → Return Results → Cloud Flow (Email / DB Update)"
            )
        elif len(desktop_actions) > 0:
            arch_type = "Desktop Only"
            summary = (
                f"The workflow is primarily composed of desktop-bound actions ({len(desktop_actions)} actions) "
                f"such as Excel, Windows UI, or local file automation. Recommended target is Power Automate Desktop (PAD)."
            )
            orchestration = "Power Automate Desktop Flow scheduled locally or triggered via unattended bot pool."
        else:
            arch_type = "Cloud Only"
            summary = (
                f"The entire automation consists of cloud-compatible connectors and operations ({len(cloud_actions)} actions). "
                f"Can be 100% migrated to serverless Power Automate Cloud Flows without requiring virtual machines."
            )
            orchestration = "Single Power Automate Cloud Flow running serverlessly in Microsoft Power Platform."

        # Build Target Cloud Flow Blueprint
        cloud_flow_actions: List[TargetCloudFlowAction] = []
        for a in cloud_actions:
            cloud_flow_actions.append(TargetCloudFlowAction(
                id=f"step_{a.step}",
                name=f"{a.command}_{a.step}",
                type="OpenApiConnection" if "Connector" in a.powerAutomateAction else "Action",
                connector="Office365Outlook" if "email" in a.command.lower() else "HTTP" if "http" in a.command.lower() else "Standard",
                operationId=a.powerAutomateAction,
                parameters=a.attributes,
                runAfter={}
            ))

        if len(desktop_actions) > 0:
            # Add invocation step
            cloud_flow_actions.append(TargetCloudFlowAction(
                id="run_desktop_flow_step",
                name="Run_Desktop_Automation",
                type="DesktopFlow",
                connector="PowerAutomateDesktop",
                operationId="RunDesktopFlow",
                parameters={"runMode": "attendedOrUnattended", "flowId": f"{workflow_name}_Desktop"},
                runAfter={}
            ))

        cloud_flows = [
            TargetCloudFlow(
                name=f"{workflow_name}_CloudOrchestrator",
                description="Parent orchestrator managing execution, notifications, and cloud connections.",
                trigger={"type": "Recurrence", "frequency": "Day", "interval": 1},
                actions=cloud_flow_actions,
                connectionsNeeded=["Office 365 Outlook", "SharePoint", "HTTP Premium"] if len(cloud_actions) > 0 else [],
                environmentVariables=[f"ENV_{v.name}" for v in variables if v.isInput]
            )
        ]

        # Build Target Desktop Flow Blueprint
        desktop_flow_actions: List[TargetDesktopFlowAction] = []
        for a in desktop_actions:
            desktop_flow_actions.append(TargetDesktopFlowAction(
                id=f"pad_step_{a.step}",
                name=a.powerAutomateAction,
                module="Excel" if "excel" in a.command.lower() else "WebAutomation" if "browser" in a.command.lower() else "UIAutomation",
                statement=f"CALL {a.powerAutomateAction}",
                parameters=a.attributes
            ))

        desktop_flows = []
        if len(desktop_actions) > 0:
            desktop_flows.append(TargetDesktopFlow(
                name=f"{workflow_name}_Desktop",
                description="Power Automate Desktop flow executing UI and local document interactions.",
                subroutines=["Main", "ExceptionHandling"],
                inputVariables=[v.name for v in variables if v.isInput],
                outputVariables=[v.name for v in variables if v.isOutput],
                actions=desktop_flow_actions,
                prerequisites=[d.name for d in dependencies if d.type in ("Application", "Desktop Software", "Browser")]
            ))

        # Recommended Connections
        conn_set = set()
        for a in actions:
            for dep in a.dependencies:
                conn_set.add(dep)
        recommended_connections = sorted(list(conn_set))

        # Migration Risks
        risks = []
        if len(manual_actions) > 0:
            risks.append({
                "severity": "High",
                "title": f"{len(manual_actions)} Actions Require Manual Review",
                "description": "Actions with proprietary or unknown A360 logic must be manually converted.",
                "mitigation": "Review action details in Action Explorer and provide custom Power Automate equivalents."
            })
        if any("credential" in d.name.lower() or "password" in d.name.lower() for d in dependencies):
            risks.append({
                "severity": "Medium",
                "title": "Credential and Credential Vault Migration",
                "description": "A360 Credential Locker variables cannot be exported in plain text.",
                "mitigation": "Configure Azure Key Vault or Power Automate Environment Variables (Secret type)."
            })
        if any("sap" in a.command.lower() for a in actions):
            risks.append({
                "severity": "High",
                "title": "SAP GUI Scripting Prerequisite",
                "description": "SAP GUI automation requires server-side and client-side scripting authorization.",
                "mitigation": "Verify 'sapgui/user_scripting = TRUE' on SAP server before deploying Desktop Flow."
            })
        if len(desktop_actions) > 0:
            risks.append({
                "severity": "Medium",
                "title": "Desktop Runtime & Browser Extensions",
                "description": "Power Automate Desktop requires machine registration and browser extensions.",
                "mitigation": "Install PAD and Chrome/Edge extension on target bot runner machines."
            })

        # Manual Review items
        manual_review_items = [
            {
                "step": a.step,
                "command": a.command,
                "task": a.task,
                "file": a.sourceFile,
                "raw": a.rawAction,
                "reason": a.reason,
                "suggestedAction": "Inspect A360 bot logic and replace with custom connector or script."
            }
            for a in manual_actions
        ]

        # Estimated effort hours based on complexity
        hours = 8  # base setup
        for a in actions:
            if a.migrationComplexity == "Low":
                hours += 1
            elif a.migrationComplexity == "Medium":
                hours += 3
            else:
                hours += 6
        hours += len(manual_actions) * 4

        target_arch = TargetArchitecture(
            architectureType=arch_type,
            summary=summary,
            orchestrationPattern=orchestration,
            cloudFlows=cloud_flows,
            desktopFlows=desktop_flows,
            recommendedConnections=recommended_connections,
            securityAndCredentialsGuidance=(
                "Store sensitive passwords, API keys, and service credentials in Azure Key Vault or "
                "Power Automate encrypted environment variables. Do NOT hardcode credentials into flow parameters."
            ),
            migrationRoadmapPhases=[
                {"phase": "Phase 1: Environment Setup", "durationDays": 2, "tasks": ["Provision Power Platform environment", "Register bot runner machines in Machine Management", "Install PAD runtime and browser extensions"]},
                {"phase": "Phase 2: Flow Implementation", "durationDays": max(3, hours // 8), "tasks": ["Create Cloud Flow triggers & connectors", "Implement PAD desktop subroutines", "Configure input/output parameters"]},
                {"phase": "Phase 3: Integration & UAT", "durationDays": 4, "tasks": ["End-to-end integration testing", "User acceptance validation", "Exception handling and retry testing"]},
                {"phase": "Phase 4: Cutover & Hypercare", "durationDays": 2, "tasks": ["Decommission A360 schedules", "Enable Power Automate production triggers", "Monitor run history"]}
            ]
        )

        return MigrationPlanModel(
            job_id=job_id,
            workflow_name=workflow_name,
            architecture=target_arch,
            action_plans=[a.model_dump() for a in actions],
            migration_risks=risks,
            manual_review_items=manual_review_items,
            estimated_effort_hours=hours
        )
