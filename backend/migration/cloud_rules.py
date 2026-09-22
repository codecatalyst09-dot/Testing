from typing import Dict, Any, Optional, Tuple

CLOUD_COMMANDS = {
    "rest": ("HTTP", "Invoke REST API / HTTP Web Service", 0.95),
    "restapi": ("HTTP", "Invoke REST API / HTTP Web Service", 0.95),
    "http": ("HTTP", "Send HTTP Request", 0.95),
    "email": ("Send an email (V2) / Outlook Connector", "Send or receive emails via Office 365 Outlook connector", 0.92),
    "sendemail": ("Send an email (V2)", "Cloud email notification via Office 365", 0.95),
    "outlook": ("Office 365 Outlook", "Cloud mailbox operations", 0.90),
    "sharepoint": ("SharePoint Online Connector", "Access cloud documents and lists", 0.95),
    "onedrive": ("OneDrive for Business Connector", "Cloud file storage access", 0.95),
    "teams": ("Microsoft Teams Connector", "Post message or adaptive card to channel", 0.95),
    "slack": ("Slack Connector", "Cloud messaging connector", 0.90),
    "dataverse": ("Microsoft Dataverse", "CRUD operations on Dataverse entities", 0.95),
    "approval": ("Start and wait for an approval", "Cloud human-in-the-loop approval workflow", 0.95),
    "json": ("Parse JSON / Compose", "In-memory JSON parsing and manipulation", 0.92),
    "xml": ("XPath / Compose", "Cloud XML content transformation", 0.88),
    "delay": ("Delay", "Cloud delay action in seconds/minutes", 0.95),
    "string": ("Compose / String functions", "Cloud expression string operations (concat, replace, substring)", 0.95),
    "datetime": ("Convert time zone / Format DateTime", "Cloud datetime manipulation functions", 0.95),
    "number": ("Compose / Math expressions", "Cloud math expressions", 0.95),
    "list": ("Initialize variable (Array) / Append to array", "Cloud array collection management", 0.92),
    "dictionary": ("Initialize variable (Object)", "Cloud key-value dictionary management", 0.92),
    "if": ("Condition", "Cloud conditional branching control", 0.95),
    "loop": ("Apply to each / Do until", "Cloud iteration loop control", 0.95),
    "assign": ("Set variable", "Cloud variable assignment", 0.95),
    "variable": ("Initialize variable", "Cloud variable initialization", 0.95),
}

def match_cloud_rule(command: str, action: Optional[str], attributes: Dict[str, Any]) -> Optional[Tuple[str, str, float]]:
    """
    Check if an A360 action matches Cloud-eligible rules.
    Returns (TargetAction, Reason, Confidence) or None.
    """
    cmd_lower = (command or "").lower().strip()
    
    # Check direct command dictionary
    if cmd_lower in CLOUD_COMMANDS:
        target, reason, conf = CLOUD_COMMANDS[cmd_lower]
        return target, reason, conf

    # Partial match for cloud services
    if "api" in cmd_lower or "webhook" in cmd_lower:
        return "HTTP", "Cloud HTTP / REST API action suitable for Power Automate Cloud connector.", 0.90
    if "mail" in cmd_lower:
        return "Office 365 Outlook - Send an email (V2)", "Email operations should migrate to cloud Outlook connector.", 0.90
    if "teams" in cmd_lower:
        return "Microsoft Teams - Post message", "Teams interaction maps directly to cloud connector.", 0.95

    return None
