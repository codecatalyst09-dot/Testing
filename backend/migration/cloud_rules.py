from typing import Dict, Any, Optional, Tuple

CLOUD_COMMANDS: Dict[str, Tuple[str, str, float]] = {
    # Flow Control & Logic (Cloud First)
    "if": ("Condition", "Cloud conditional branching control", 0.98),
    "condition": ("Condition", "Cloud conditional branching control", 0.98),
    "loop": ("Apply to each / Do until", "Cloud iteration loop control", 0.98),
    "while": ("Do until", "Cloud loop until condition met", 0.98),
    "delay": ("Delay", "Cloud delay action in seconds/minutes", 0.98),
    "wait": ("Delay", "Cloud delay action in seconds/minutes", 0.98),
    "pause": ("Delay", "Cloud pause execution", 0.98),
    "errorhandler": ("Scope (Try-Catch-Finally)", "Cloud Scope action with Configure Run After failure handling", 0.96),
    "error handling": ("Scope (Try-Catch-Finally)", "Cloud Scope action with Configure Run After failure handling", 0.96),
    "try": ("Scope (Try)", "Cloud Scope container for try block", 0.96),
    "catch": ("Scope (Catch)", "Cloud Scope container configured to run on has failed / timed out", 0.96),
    "finally": ("Scope (Finally)", "Cloud Scope container configured to run always", 0.96),
    "throw": ("Terminate (Failed)", "Cloud Terminate action with custom error message", 0.96),
    "step": ("Scope", "Cloud Scope action to group and organize sequential steps", 0.96),
    "comment": ("Note / Annotation", "Action comment/note in Power Automate", 0.98),

    # Data Types, Variables & Expressions (Cloud First)
    "assign": ("Set variable / Initialize variable", "Cloud variable initialization or assignment", 0.98),
    "variable": ("Initialize variable", "Cloud variable definition", 0.98),
    "variables": ("Initialize variable", "Cloud variable definition", 0.98),
    "string": ("Compose / String functions", "Cloud string expressions (concat, substring, replace, split, trim, length, toUpper, toLower)", 0.96),
    "number": ("Compose / Math expressions", "Cloud math expressions (add, sub, mul, div, mod, round, rand, formatNumber)", 0.96),
    "datetime": ("Convert time zone / Format DateTime", "Cloud datetime manipulation functions and timezone conversion", 0.96),
    "date": ("Convert time zone / Format DateTime", "Cloud datetime manipulation functions", 0.96),
    "boolean": ("Initialize variable (Boolean)", "Cloud boolean variable initialization", 0.96),
    "list": ("Initialize variable (Array) / Append to array variable", "Cloud array collection management", 0.95),
    "array": ("Initialize variable (Array) / Append to array variable", "Cloud array collection management", 0.95),
    "dictionary": ("Initialize variable (Object) / Compose", "Cloud key-value dictionary management", 0.95),
    "map": ("Initialize variable (Object) / Compose", "Cloud key-value dictionary management", 0.95),
    "json": ("Parse JSON / Compose", "In-memory cloud JSON parsing and schema validation", 0.96),
    "xml": ("XPath / Compose", "Cloud XML content transformation and XPath query", 0.92),
    "datatable": ("Filter array / Select / Create HTML table", "Cloud in-memory table operations", 0.92),
    "table": ("Filter array / Select / Create HTML table", "Cloud in-memory table operations", 0.92),

    # APIs, Web Services & HTTP (Cloud First)
    "rest": ("HTTP", "Invoke REST API / HTTP Web Service via Cloud HTTP connector", 0.97),
    "restapi": ("HTTP", "Invoke REST API / HTTP Web Service via Cloud HTTP connector", 0.97),
    "restwebservice": ("HTTP", "Invoke REST API / HTTP Web Service via Cloud HTTP connector", 0.97),
    "http": ("HTTP", "Send HTTP Request via Cloud HTTP connector", 0.97),
    "webapi": ("HTTP", "Invoke web API via Cloud HTTP connector", 0.97),
    "soap": ("HTTP (SOAP envelope)", "Cloud HTTP request with SOAP XML envelope", 0.93),
    "soapwebservice": ("HTTP (SOAP envelope)", "Cloud HTTP request with SOAP XML envelope", 0.93),
    "webhook": ("When a HTTP request is received / HTTP", "Cloud webhook trigger or HTTP callback", 0.95),

    # Communication & Collaboration (Cloud First)
    "email": ("Office 365 Outlook - Send an email (V2) / Get emails (V3)", "Send, retrieve, or manage emails via Office 365 Outlook cloud connector", 0.96),
    "mail": ("Office 365 Outlook - Send an email (V2) / Get emails (V3)", "Send, retrieve, or manage emails via Office 365 Outlook cloud connector", 0.96),
    "sendemail": ("Office 365 Outlook - Send an email (V2)", "Cloud email notification via Office 365", 0.97),
    "outlook": ("Office 365 Outlook", "Cloud mailbox operations", 0.95),
    "exchange": ("Office 365 Outlook", "Cloud Exchange email operations", 0.95),
    "teams": ("Microsoft Teams Connector", "Post message or adaptive card to Teams channel/chat", 0.96),
    "slack": ("Slack Connector", "Cloud messaging connector for Slack channels", 0.92),
    "approval": ("Start and wait for an approval", "Cloud human-in-the-loop approval workflow", 0.96),
    "approvals": ("Start and wait for an approval", "Cloud human-in-the-loop approval workflow", 0.96),

    # Cloud Storage & SaaS (Cloud First)
    "sharepoint": ("SharePoint Online Connector", "Access cloud SharePoint lists, document libraries, and files", 0.96),
    "onedrive": ("OneDrive for Business Connector", "Cloud file storage access and sync", 0.96),
    "googledrive": ("Google Drive Connector", "Cloud file operations on Google Drive", 0.94),
    "googlesheets": ("Google Sheets Connector", "Cloud row operations on Google Sheets", 0.94),
    "dataverse": ("Microsoft Dataverse", "CRUD operations on Dataverse entities", 0.96),
    "salesforce": ("Salesforce Connector", "Cloud CRM operations via Salesforce connector", 0.94),
    "servicenow": ("ServiceNow Connector", "Cloud ITSM record creation and updates", 0.94),
    "jira": ("Jira Connector", "Cloud issue tracking and ticket management", 0.94),
    "sftp": ("SFTP - SSH Connector", "Cloud SFTP file transfer connector", 0.93),
    "ftp": ("SFTP - SSH Connector", "Cloud SFTP file transfer connector", 0.93),
    "ftpsftp": ("SFTP - SSH Connector", "Cloud SFTP file transfer connector", 0.93),
    "credential": ("Azure Key Vault Connector", "Retrieve credentials/secrets from Azure Key Vault", 0.94),
    "activedirectory": ("Azure AD / Microsoft Entra ID", "Cloud directory services and user management", 0.94),
}

def match_cloud_rule(command: str, action: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> Optional[Tuple[str, str, float]]:
    """
    Check if an A360 action matches Cloud-eligible rules under Cloud-First architecture.
    Returns (TargetAction, Reason, Confidence) or None.
    """
    attrs = attributes or {}
    cmd_clean = (command or "").strip()
    cmd_lower = cmd_clean.lower().replace(" ", "").replace("_", "")
    op_clean = (action or "").strip()
    op_lower = op_clean.lower()

    # Exclude actions that strictly require desktop environment
    desktop_only_markers = [
        "sap", "sapgui", "window", "mouse", "keystroke", "simulatekeystrokes",
        "recorder", "capture", "terminal", "mainframe", "citrix", "clipboard",
        "powershell", "python", "vbscript", "vbs", "doscommand", "application",
        "process", "printer", "service"
    ]
    if any(marker in cmd_lower for marker in desktop_only_markers):
        return None

    # Exclude local desktop Excel (files on local paths C:\, D:\, \\fs01, or Advanced COM/macros)
    if "excel" in cmd_lower:
        path_val = str(attrs.get("path", "") or attrs.get("filePath", "") or attrs.get("file", ""))
        # If it's explicitly a SharePoint or OneDrive URL, it can use Cloud Excel Online connector
        if path_val.startswith("http://") or path_val.startswith("https://") or "sharepoint.com" in path_val:
            return (
                "Excel Online (Business) Connector",
                "Cloud-hosted Excel file on SharePoint/OneDrive maps directly to Excel Online (Business) connector.",
                0.94
            )
        # Otherwise, local Excel belongs to Desktop
        return None

    # Exclude local file system actions unless targeting cloud storage
    if cmd_lower in ("file", "folder", "filesystem", "csv", "textfile"):
        path_val = str(attrs.get("path", "") or attrs.get("filePath", "") or attrs.get("file", ""))
        if "sharepoint.com" in path_val or "onedrive" in path_val or path_val.startswith("http"):
            return (
                "SharePoint / OneDrive File Connector",
                "Cloud file storage operation maps to native SharePoint/OneDrive connector.",
                0.94
            )
        return None

    # Direct match in CLOUD_COMMANDS
    if cmd_lower in CLOUD_COMMANDS:
        target, reason, conf = CLOUD_COMMANDS[cmd_lower]
        # Fine-tune target action if operation is known
        if op_lower:
            if cmd_lower in ("email", "mail", "sendemail"):
                if "get" in op_lower or "read" in op_lower or "latest" in op_lower:
                    return ("Office 365 Outlook - Get emails (V3)", "Retrieve emails via Office 365 Outlook connector.", 0.96)
                elif "send" in op_lower:
                    return ("Office 365 Outlook - Send an email (V2)", "Send email notification via Office 365 Outlook connector.", 0.97)
            elif cmd_lower in ("loop",):
                if "row" in op_lower or "each" in op_lower or "list" in op_lower:
                    return ("Apply to each", "Iterate over collection using Cloud 'Apply to each' action.", 0.98)
                elif "while" in op_lower or "condition" in op_lower:
                    return ("Do until", "Cloud loop until condition is satisfied.", 0.97)
            elif cmd_lower in ("number",):
                if "subtract" in op_lower or "sub" in op_lower:
                    return ("sub() expression in Compose", "Cloud math expression sub() to subtract values.", 0.97)
                elif "add" in op_lower:
                    return ("add() expression in Compose", "Cloud math expression add() to sum values.", 0.97)
                elif "round" in op_lower:
                    return ("round() expression in Compose", "Cloud math expression round() to round numeric values.", 0.97)
                elif "random" in op_lower:
                    return ("rand() expression in Compose", "Cloud expression rand(min,max) to generate random integer.", 0.97)
            elif cmd_lower in ("string",):
                if "substring" in op_lower:
                    return ("substring() expression in Compose", "Cloud expression substring() to extract part of text.", 0.97)
                elif "replace" in op_lower:
                    return ("replace() expression in Compose", "Cloud expression replace() to substitute text.", 0.97)
                elif "split" in op_lower:
                    return ("split() expression in Compose", "Cloud expression split() to divide text into array.", 0.97)
                elif "concat" in op_lower or "append" in op_lower:
                    return ("concat() expression in Compose", "Cloud expression concat() to join text strings.", 0.97)
        return target, reason, conf

    # Partial substring matches for cloud services
    if "api" in cmd_lower or "webhook" in cmd_lower or "http" in cmd_lower or "rest" in cmd_lower:
        return "HTTP", "Cloud HTTP / REST API action suitable for Power Automate Cloud connector.", 0.95
    if "mail" in cmd_lower or "email" in cmd_lower:
        return "Office 365 Outlook - Send an email (V2)", "Email operations migrate cleanly to cloud Outlook connector.", 0.95
    if "teams" in cmd_lower:
        return "Microsoft Teams - Post message", "Teams interaction maps directly to cloud connector.", 0.96
    if "sharepoint" in cmd_lower:
        return "SharePoint Online Connector", "SharePoint operations map directly to cloud connector.", 0.96
    if "onedrive" in cmd_lower:
        return "OneDrive for Business Connector", "OneDrive storage maps directly to cloud connector.", 0.96

    return None
