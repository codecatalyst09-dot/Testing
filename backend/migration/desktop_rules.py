from typing import Dict, Any, Optional, Tuple

DESKTOP_COMMANDS = {
    # Excel
    "excel": ("Launch Excel / Read from Excel worksheet", "Local desktop Excel workbook manipulation", 0.94),
    "exceladvanced": ("Launch Excel / Attach to running Excel", "Advanced local Excel manipulation with COM/Interop", 0.96),
    "excelbasic": ("Launch Excel / Read from Excel worksheet", "Basic desktop Excel manipulation", 0.94),
    
    # Browser / Web UI
    "browser": ("Launch new Microsoft Edge / Google Chrome", "Desktop web browser automation via PAD extension", 0.95),
    "webautomation": ("Click UI element in window / Populate text field in web page", "Interactive web UI interaction", 0.95),
    "recorder": ("UI Automation / Populate text field", "Recorded desktop UI element interaction", 0.92),
    "capture": ("Click UI element / Extract data from window", "Object-cloned desktop or web UI interaction", 0.92),
    "window": ("Focus window / Set window state", "Desktop window management and focus handling", 0.95),
    
    # File System
    "file": ("Read text from file / Copy file / Write text to file", "Local file system operation on target machine", 0.95),
    "folder": ("Create folder / Get files in folder", "Local directory management", 0.95),
    "filesystem": ("File system actions", "Local OS file handling", 0.95),
    "csv": ("Read from CSV file", "Local CSV file processing into datatable", 0.95),
    
    # OS / Windows Applications
    "application": ("Run application / Close window", "Local Windows desktop software execution", 0.95),
    "process": ("Start process / Terminate process", "Local Windows process management", 0.95),
    "system": ("Run DOS command / Shutdown computer", "Local system operation", 0.95),
    "clipboard": ("Get clipboard text / Set clipboard text", "Desktop OS clipboard buffer interaction", 0.95),
    "mouse": ("Move mouse / Click", "Hardware-level mouse simulation on desktop display", 0.92),
    "keystroke": ("Send keys", "Simulate desktop keyboard input and shortcuts", 0.92),
    "simulatekeystrokes": ("Send keys", "Simulate desktop keyboard input and shortcuts", 0.92),
    "ocr": ("Extract text with OCR", "Desktop image/screen optical character recognition", 0.88),
    "screen": ("Capture screen to file", "Desktop display snapshot capture", 0.90),
    
    # Legacy & ERP
    "sap": ("SAP GUI Automation / Connect to SAP", "Desktop SAP GUI client transaction automation", 0.92),
    "sapgui": ("SAP GUI Automation / Connect to SAP", "Desktop SAP GUI client transaction automation", 0.95),
    "terminal": ("Open terminal connection / Send terminal command", "Legacy terminal emulation (3270 / 5250 / VT100)", 0.90),
    "mainframe": ("Open terminal connection", "IBM Mainframe terminal emulation", 0.90),
    "citrix": ("Image recognition / Surface automation", "Remote desktop / Citrix session automation", 0.85),
    
    # Scripts
    "vbs": ("Run VBScript", "Execute legacy VBScript script on desktop", 0.92),
    "vbscript": ("Run VBScript", "Execute legacy VBScript script on desktop", 0.92),
    "javascript": ("Run JavaScript", "Execute client-side JavaScript", 0.90),
    "python": ("Run Python script", "Execute local Python automation script", 0.92),
    "powershell": ("Run PowerShell script", "Execute administrative PowerShell script", 0.95),
    "doscommand": ("Run DOS command", "Execute local CMD/batch command", 0.95),
    "pdf": ("Extract text from PDF / Extract tables from PDF", "Local PDF parsing and table extraction", 0.92),
}

def match_desktop_rule(command: str, action: Optional[str], attributes: Dict[str, Any]) -> Optional[Tuple[str, str, float]]:
    """
    Check if an A360 action matches Desktop (PAD) rules.
    Returns (TargetAction, Reason, Confidence) or None.
    """
    cmd_lower = (command or "").lower().strip()
    
    if cmd_lower in DESKTOP_COMMANDS:
        target, reason, conf = DESKTOP_COMMANDS[cmd_lower]
        return target, reason, conf

    # Partial / substring matches for desktop operations
    if "excel" in cmd_lower:
        return "Launch Excel / Read from Excel worksheet", "Local Excel automation requires desktop execution.", 0.94
    if "browser" in cmd_lower:
        return "Launch new Microsoft Edge / UI Automation", "Web browser automation requires Power Automate Desktop browser extension.", 0.92
    if "window" in cmd_lower or "desktop" in cmd_lower:
        return "Focus window / UI Automation", "Desktop UI interaction requires Power Automate Desktop agent.", 0.90
    if "sap" in cmd_lower:
        return "SAP GUI Automation", "SAP GUI interaction requires desktop execution.", 0.92
    if "mouse" in cmd_lower or "key" in cmd_lower:
        return "Send keys / Move mouse", "Desktop peripheral simulation requires local execution.", 0.90

    return None
