from typing import Dict, Any, Optional, List
from backend.migration.classifier import ActionClassifier
from backend.migration.excel_mapping_db import ExcelMappingDB

class MappingEngine:
    """
    RPA Migration Mapping Engine mapping A360 actions to Power Automate specifications.
    Authoritatively backed by Mapping/AA_to_PowerAutomate_Action_Mapping.xlsx.
    """

    @classmethod
    def map_action(
        cls,
        command: str,
        operation: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        context_has_cloud: bool = False,
        context_has_desktop: bool = False
    ) -> Dict[str, Any]:
        attrs = attributes or {}
        cmd = (command or "").strip()
        cmd_lower = cmd.lower()
        op_lower = (operation or "").lower().strip()

        # Step 0: Consult official Excel Mapping Database
        db_mapping = ExcelMappingDB.get_instance().find_mapping(cmd, operation)

        # Step 1: Classify Platform
        platform, reason, confidence = ActionClassifier.classify_action(
            cmd, operation, attrs, context_has_cloud, context_has_desktop
        )
        if db_mapping.get("platform") and db_mapping["platform"] != "Manual Review" and platform != "Hybrid":
            platform = db_mapping["platform"]

        target_action = "Manual Review Required"
        strategy = "Manual Review"
        complexity = "Medium"
        manual_steps: List[str] = []
        dependencies: List[str] = []

        if platform == "Manual Review":
            target_action = f"Manual Review ({cmd})"
            strategy = "Manual Review"
            complexity = "High"
            confidence = 0.25
            reason = f"Unknown or proprietary A360 command '{cmd}'. Requires manual architecture review to select equivalent connector or custom script."
            manual_steps = [
                f"Inspect original A360 package implementation for step '{cmd}'",
                "Evaluate if custom Power Automate Connector, Azure Function, or PowerShell script is required",
                "Implement unit test for replacement logic"
            ]
            dependencies = ["Manual Architecture Review"]

        elif platform == "Power Automate Desktop":
            strategy = "Desktop Replacement"
            if "excel" in cmd_lower:
                dependencies = ["Microsoft Excel (Desktop)", "Power Automate Desktop Agent"]
                if "open" in op_lower or "launch" in op_lower or "open" in str(attrs).lower():
                    target_action = "Launch Excel"
                    strategy = "Direct Mapping"
                    complexity = "Low"
                    confidence = 0.96
                    reason = "The action requires local desktop Excel interaction. Directly maps to PAD 'Launch Excel'."
                    manual_steps = ["Configure document path and instance variable in PAD Launch Excel action."]
                elif "save" in op_lower or "close" in op_lower:
                    target_action = "Close Excel"
                    strategy = "Direct Mapping"
                    complexity = "Low"
                    confidence = 0.96
                    reason = "Direct mapping to PAD 'Close Excel' action."
                elif "read" in op_lower or "cell" in op_lower or "get" in op_lower:
                    target_action = "Read from Excel worksheet"
                    strategy = "Direct Mapping"
                    complexity = "Low"
                    confidence = 0.94
                    reason = "Direct mapping to PAD 'Read from Excel worksheet' to extract data table."
                elif "write" in op_lower or "set" in op_lower:
                    target_action = "Write to Excel worksheet"
                    strategy = "Direct Mapping"
                    complexity = "Low"
                    confidence = 0.94
                    reason = "Direct mapping to PAD 'Write to Excel worksheet'."
                else:
                    target_action = "Launch Excel / Excel Operations"
                    strategy = "Direct Mapping"
                    complexity = "Low"
                    confidence = 0.92
                    reason = "Local desktop Excel manipulation mapped to PAD Excel action group."

            elif "browser" in cmd_lower or "web" in cmd_lower or "recorder" in cmd_lower or "capture" in cmd_lower:
                dependencies = ["Microsoft Edge or Google Chrome", "Power Automate Desktop Browser Extension"]
                if "open" in op_lower or "launch" in op_lower or "navigate" in op_lower:
                    target_action = "Launch new Microsoft Edge"
                    strategy = "Direct Mapping"
                    complexity = "Low"
                    confidence = 0.95
                    reason = "Web browser automation requires PAD 'Launch new Microsoft Edge' or 'Launch new Chrome'."
                    manual_steps = ["Verify browser extension is enabled and URL parameter is passed."]
                elif "click" in op_lower:
                    target_action = "Click UI element in window"
                    strategy = "Equivalent Connector"
                    complexity = "Medium"
                    confidence = 0.90
                    reason = "Web UI click maps to PAD UI element selector."
                    manual_steps = ["Re-record UI element selector using PAD UI element picker."]
                elif "set" in op_lower or "text" in op_lower or "type" in op_lower:
                    target_action = "Populate text field in web page"
                    strategy = "Equivalent Connector"
                    complexity = "Medium"
                    confidence = 0.90
                    reason = "Input field population maps to PAD 'Populate text field in web page'."
                    manual_steps = ["Re-capture target input field selector in PAD."]
                else:
                    target_action = "PAD Web Automation"
                    strategy = "Equivalent Connector"
                    complexity = "Medium"
                    confidence = 0.88
                    reason = "Interactive web automation requiring PAD browser extension."

            elif "sap" in cmd_lower:
                dependencies = ["SAP GUI Client", "SAP Scripting enabled on SAP Server"]
                manual_steps = [
                    "Ensure SAP GUI Scripting is enabled server-side (rz11 sapgui/user_scripting)",
                    "Configure PAD SAP logon session"
                ]
                strategy = "Desktop Replacement"
                complexity = "High"
                confidence = 0.92
                if "connect" in op_lower or "logon" in op_lower:
                    target_action = "SAP GUI Automation / Connect to SAP"
                    reason = "Connect to SAP session using PAD SAP GUI Automation."
                elif "runtransaction" in op_lower or "transaction" in op_lower:
                    target_action = "SAP GUI Automation (Execute Transaction)"
                    reason = "Execute SAP transaction code (e.g. F-28) via PAD SAP GUI."
                elif "settext" in op_lower or "enter" in op_lower:
                    target_action = "Populate text field in SAP window"
                    reason = "Set SAP field value via PAD SAP element interaction."
                elif "press" in op_lower or "click" in op_lower:
                    target_action = "Press button in SAP window"
                    reason = "Trigger SAP button click in active SAP GUI window."
                elif "gettext" in op_lower or "read" in op_lower:
                    target_action = "Get details of element on SAP window"
                    reason = "Extract SAP UI text field into flow variable."
                else:
                    target_action = "SAP GUI Automation"
                    reason = "A360 SAP actions map to Power Automate Desktop SAP GUI action group."

            elif "workload" in cmd_lower or "queue" in cmd_lower:
                dependencies = ["Power Automate Desktop Work Queues / Dataverse"]
                strategy = "Direct Mapping"
                complexity = "Low"
                confidence = 0.94
                if "insert" in op_lower or "add" in op_lower:
                    target_action = "Add work queue item"
                    reason = "Directly maps to PAD Work queues 'Add work queue item' action."
                elif "process" in op_lower or "get" in op_lower:
                    target_action = "Process work queue items"
                    reason = "Directly maps to PAD Work queues 'Process work queue items' action."
                else:
                    target_action = "Manage work queue items"
                    reason = "Directly maps to PAD Work queues module."

            elif "file" in cmd_lower or "folder" in cmd_lower or "filesystem" in cmd_lower:
                target_action = "PAD File & Folder actions (Read/Write/Copy/Delete)"
                strategy = "Direct Mapping"
                complexity = "Low"
                confidence = 0.95
                dependencies = ["Local File System Access"]
                reason = "Local disk access requires Power Automate Desktop File System module."

            elif "script" in cmd_lower or "vbs" in cmd_lower or "python" in cmd_lower or "powershell" in cmd_lower:
                target_action = "Run PowerShell script / Run VBScript / Run Python script"
                strategy = "Custom Script"
                complexity = "Medium"
                confidence = 0.92
                dependencies = ["PowerShell/VBScript/Python Runtime"]
                reason = "Local script execution maps to PAD scripting actions."
                manual_steps = ["Port script parameters into PAD variable syntax."]

            else:
                target_action = f"PAD Desktop Action ({cmd})"
                strategy = "Desktop Replacement"
                complexity = "Medium"
                confidence = 0.85
                dependencies = ["Power Automate Desktop Agent"]
                reason = "Requires desktop agent on target host."

        elif platform == "Power Automate Cloud":
            if "rest" in cmd_lower or "http" in cmd_lower or "api" in cmd_lower:
                target_action = "HTTP"
                strategy = "Direct Mapping"
                complexity = "Low"
                confidence = 0.96
                dependencies = ["Power Automate Premium (HTTP Connector)"]
                reason = "A360 REST/HTTP web service calls map cleanly to the Cloud Flow HTTP action."
                manual_steps = ["Review authentication headers and API endpoint URL."]

            elif "email" in cmd_lower or "mail" in cmd_lower:
                target_action = "Office 365 Outlook - Send an email (V2)"
                strategy = "Equivalent Connector"
                complexity = "Low"
                confidence = 0.95
                dependencies = ["Office 365 Outlook Connection"]
                reason = "A360 email sending replaces legacy SMTP with native Office 365 Outlook connector."
                manual_steps = ["Connect service account to Office 365 Outlook connector."]

            elif "sharepoint" in cmd_lower:
                target_action = "SharePoint Online Connector"
                strategy = "Equivalent Connector"
                complexity = "Low"
                confidence = 0.95
                dependencies = ["SharePoint Connection"]
                reason = "Native cloud integration for SharePoint lists and document libraries."

            elif "if" in cmd_lower or "condition" in cmd_lower:
                target_action = "Condition"
                strategy = "Direct Mapping"
                complexity = "Low"
                confidence = 0.97
                reason = "A360 conditional logic directly maps to Power Automate Cloud Condition branching."

            elif "loop" in cmd_lower:
                target_action = "Apply to each / Do until"
                strategy = "Direct Mapping"
                complexity = "Low"
                confidence = 0.95
                reason = "A360 loop blocks directly map to Cloud 'Apply to each' iteration or 'Do until' loops."

            elif "assign" in cmd_lower or "variable" in cmd_lower:
                target_action = "Set variable / Initialize variable"
                strategy = "Direct Mapping"
                complexity = "Low"
                confidence = 0.97
                reason = "Variable definition and assignment directly maps to standard Cloud Flow variable actions."

            elif "delay" in cmd_lower:
                target_action = "Delay"
                strategy = "Direct Mapping"
                complexity = "Low"
                confidence = 0.98
                reason = "Direct 1-to-1 equivalent Delay action in Cloud Flows."

            else:
                target_action = f"Cloud Flow ({cmd})"
                strategy = "Cloud Replacement"
                complexity = "Medium"
                confidence = 0.90
                reason = "Can be executed natively in Power Automate Cloud without on-premises desktop infrastructure."

        elif platform == "Hybrid":
            target_action = "Run a flow built with Power Automate for desktop"
            strategy = "Hybrid Implementation"
            complexity = "Medium"
            confidence = 0.93
            dependencies = ["On-Premises Data Gateway or Direct-to-Machine Connectivity", "PAD Attended/Unattended License"]
            reason = "Orchestrates across cloud and on-premises boundaries: Cloud Flow triggers, invokes Desktop Flow via machine connection, and processes results."
            manual_steps = [
                "Register target machine in Power Automate Machine Management",
                "Pass input variables to desktop flow and configure output variable capture"
            ]

        # If target action wasn't resolved by custom rule, use official database recommendation
        if target_action in ("Manual Review Required", f"Cloud Flow ({cmd})", f"PAD Desktop Action ({cmd})") and db_mapping.get("recommended_action"):
            target_action = db_mapping["recommended_action"]
            if db_mapping.get("migration_notes"):
                reason = db_mapping["migration_notes"]

        # Ensure consistent PAD category and migration notes if platform was resolved
        pad_category = db_mapping.get("pad_category") or ""
        migration_notes = db_mapping.get("migration_notes") or ""

        if platform == "Power Automate Desktop":
            if not pad_category or pad_category == "Manual Review Required":
                if "sap" in cmd_lower:
                    pad_category = "SAP GUI Automation"
                elif "workload" in cmd_lower or "queue" in cmd_lower:
                    pad_category = "Work queues"
                else:
                    pad_category = "Desktop Flow"
            if not migration_notes or "Action not found" in migration_notes:
                migration_notes = reason
        elif platform in ("Power Automate Cloud", "Hybrid"):
            if not migration_notes or "Action not found" in migration_notes:
                migration_notes = reason

        return {
            "source": "A360",
            "targetPlatform": platform,
            "targetAction": target_action,
            "strategy": strategy,
            "complexity": complexity,
            "confidence": round(confidence, 2),
            "reason": reason,
            "manualSteps": manual_steps,
            "dependencies": dependencies,
            # Official Excel mapping fields
            "aaPackage": db_mapping.get("aa_package") or cmd,
            "aaAction": db_mapping.get("aa_action") or (operation or "Execute"),
            "aaDescription": db_mapping.get("aa_description") or "",
            "padCategory": pad_category,
            "padAction": db_mapping.get("pad_action") or (target_action if platform == "Power Automate Desktop" else ""),
            "cloudAction": db_mapping.get("cloud_action") or (target_action if platform == "Power Automate Cloud" else ""),
            "migrationNotes": migration_notes
        }
