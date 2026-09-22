from typing import Dict, Any, Optional, Tuple

DESKTOP_COMMANDS: Dict[str, Tuple[str, str, float]] = {
    # Excel (Desktop)
    "excel": ("Launch Excel / Read from Excel worksheet", "Local desktop Excel workbook manipulation", 0.94),
    "exceladvanced": ("Launch Excel / Attach to running Excel", "Advanced local Excel manipulation with COM/Interop", 0.96),
    "excelbasic": ("Launch Excel / Read from Excel worksheet", "Basic desktop Excel manipulation", 0.94),
    "msexcel": ("Launch Excel / Read from Excel worksheet", "Desktop Microsoft Excel manipulation", 0.94),

    # Word (Desktop)
    "word": ("Launch Word / Read from Word document", "Desktop Microsoft Word document manipulation", 0.94),
    "msword": ("Launch Word / Read from Word document", "Desktop Microsoft Word document manipulation", 0.94),

    # Browser & Web UI (Desktop via PAD Browser Extension)
    "browser": ("Launch new Microsoft Edge / Google Chrome", "Desktop web browser automation via PAD extension", 0.95),
    "webautomation": ("Click UI element in window / Populate text field in web page", "Interactive web UI interaction", 0.95),
    "recorder": ("UI Automation / Populate text field", "Recorded desktop UI element interaction", 0.92),
    "capture": ("Click UI element / Extract data from window", "Object-cloned desktop or web UI interaction", 0.92),
    "objectcloning": ("Click UI element / Extract data from window", "Object-cloned desktop UI interaction", 0.92),
    "window": ("Focus window / Set window state", "Desktop window management and focus handling", 0.95),

    # File System & Storage (Local)
    "file": ("Read text from file / Copy file / Write text to file", "Local file system operation on target machine", 0.95),
    "folder": ("Create folder / Get files in folder", "Local directory management on target machine", 0.95),
    "filesystem": ("File system actions", "Local OS file handling", 0.95),
    "csv": ("Read from CSV file", "Local CSV file processing into datatable", 0.95),
    "textfile": ("Read text from file / Write text to file", "Local plain text file operations", 0.95),
    "zip": ("ZIP files / Unzip files", "Local archive compression and decompression", 0.95),
    "archive": ("ZIP files / Unzip files", "Local archive compression and decompression", 0.95),

    # OS, Peripherals & Windows Applications
    "application": ("Run application / Close window", "Local Windows desktop software execution", 0.95),
    "process": ("Start process / Terminate process", "Local Windows process management", 0.95),
    "system": ("Run DOS command / Shutdown computer", "Local system operation", 0.95),
    "clipboard": ("Get clipboard text / Set clipboard text", "Desktop OS clipboard buffer interaction", 0.95),
    "mouse": ("Move mouse / Click", "Hardware-level mouse simulation on desktop display", 0.92),
    "keystroke": ("Send keys", "Simulate desktop keyboard input and shortcuts", 0.92),
    "keystrokes": ("Send keys", "Simulate desktop keyboard input and shortcuts", 0.92),
    "simulatekeystrokes": ("Send keys", "Simulate desktop keyboard input and shortcuts", 0.92),
    "ocr": ("Extract text with OCR", "Desktop image/screen optical character recognition", 0.88),
    "screen": ("Capture screen to file", "Desktop display snapshot capture", 0.90),
    "printer": ("Print document", "Desktop printer spooler interaction", 0.92),
    "service": ("Start service / Stop service", "Local Windows Services management", 0.94),
    "registry": ("Read from Windows registry / Write to Windows registry", "Local Windows registry management", 0.94),
    "cryptography": ("Encrypt text with AES / Hash text", "Local cryptographic operations", 0.92),

    # Enterprise ERP & Legacy Systems
    "sap": ("SAP GUI Automation / Connect to SAP", "Desktop SAP GUI client transaction automation", 0.94),
    "sapgui": ("SAP GUI Automation / Connect to SAP", "Desktop SAP GUI client transaction automation", 0.95),
    "workload": ("Work queues (Add work queue item / Process work queue items)", "Power Automate Desktop Work Queues processing", 0.94),
    "queue": ("Work queues (Add work queue item / Process work queue items)", "Power Automate Desktop Work Queues processing", 0.94),
    "terminal": ("Open terminal connection / Send terminal command", "Legacy terminal emulation (3270 / 5250 / VT100)", 0.92),
    "terminalemulator": ("Open terminal connection / Send terminal command", "Legacy terminal emulation (3270 / 5250 / VT100)", 0.92),
    "mainframe": ("Open terminal connection", "IBM Mainframe terminal emulation", 0.92),
    "citrix": ("Image recognition / Surface automation", "Remote desktop / Citrix session automation", 0.85),

    # Local Script Execution
    "vbs": ("Run VBScript", "Execute legacy VBScript script on desktop", 0.92),
    "vbscript": ("Run VBScript", "Execute legacy VBScript script on desktop", 0.92),
    "javascript": ("Run JavaScript", "Execute client-side JavaScript on desktop", 0.90),
    "python": ("Run Python script", "Execute local Python automation script", 0.94),
    "pythonscript": ("Run Python script", "Execute local Python automation script", 0.94),
    "powershell": ("Run PowerShell script", "Execute administrative PowerShell script", 0.95),
    "doscommand": ("Run DOS command", "Execute local CMD/batch command", 0.95),
    "dll": ("Call DLL function", "Invoke functions in dynamic link libraries (.dll)", 0.90),
    "pdf": ("Extract text from PDF / Extract tables from PDF", "Local PDF parsing and table extraction", 0.92),
}

def match_desktop_rule(command: str, action: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> Optional[Tuple[str, str, float]]:
    """
    Check if an A360 action matches Desktop (PAD) rules.
    Returns (TargetAction, Reason, Confidence) or None.
    """
    cmd_clean = (command or "").strip()
    cmd_lower = cmd_clean.lower().replace(" ", "").replace("_", "")
    op_clean = (action or "").strip()
    op_lower = op_clean.lower()

    # SAP GUI fine-grained action matching
    if "sap" in cmd_lower:
        if "connect" in op_lower or "logon" in op_lower:
            return ("SAP GUI Automation / Connect to SAP", "Connect to SAP session using PAD SAP GUI Automation.", 0.96)
        elif "runtransaction" in op_lower or "transaction" in op_lower:
            return ("SAP GUI Automation (Execute Transaction)", "Execute SAP transaction code via PAD SAP GUI.", 0.95)
        elif "settext" in op_lower or "enter" in op_lower:
            return ("Populate text field in SAP window", "Set SAP field value via PAD SAP element interaction.", 0.95)
        elif "press" in op_lower or "click" in op_lower:
            return ("Press button in SAP window", "Trigger SAP button click in active SAP GUI window.", 0.95)
        elif "gettext" in op_lower or "read" in op_lower:
            return ("Get details of element on SAP window", "Extract SAP UI text field into flow variable.", 0.94)
        elif "selectitem" in op_lower:
            return ("Select menu item in SAP window", "Select SAP menu item or table row.", 0.94)
        elif "closesession" in op_lower or "close" in op_lower:
            return ("Close SAP session", "End active SAP GUI session.", 0.96)
        return ("SAP GUI Automation", "SAP GUI interaction requires Power Automate Desktop execution.", 0.93)

    # Word fine-grained action matching
    if "word" in cmd_lower:
        if "open" in op_lower or "launch" in op_lower:
            return ("Launch Word", "Launch desktop Microsoft Word application.", 0.95)
        elif "save" in op_lower:
            return ("Save Word document", "Save desktop Word document.", 0.95)
        elif "close" in op_lower:
            return ("Close Word", "Close desktop Word document and application.", 0.95)
        elif "read" in op_lower or "get" in op_lower:
            return ("Read from Word document", "Extract text content from Word document.", 0.93)
        elif "replace" in op_lower:
            return ("Find and replace text in Word document", "Find and replace text strings in Word document.", 0.93)
        return ("Launch Word / Word Operations", "Microsoft Word manipulation on desktop.", 0.93)

    # Excel (Desktop) fine-grained action matching
    if "excel" in cmd_lower:
        if "open" in op_lower or "launch" in op_lower:
            return ("Launch Excel", "Open workbook in local desktop Excel instance.", 0.96)
        elif "save" in op_lower:
            return ("Save Excel", "Save workbook in local desktop Excel instance.", 0.96)
        elif "close" in op_lower:
            return ("Close Excel", "Close workbook and local Excel process.", 0.96)
        elif "read" in op_lower or "get" in op_lower:
            return ("Read from Excel worksheet", "Extract cells or range into a datatable in PAD.", 0.95)
        elif "write" in op_lower or "set" in op_lower:
            return ("Write to Excel worksheet", "Write cell values or datatable into local Excel worksheet.", 0.95)
        elif "runmacro" in op_lower or "macro" in op_lower:
            return ("Run Excel macro", "Execute VBA macro in local Excel workbook.", 0.94)
        elif "activate" in op_lower:
            return ("Activate Excel worksheet", "Switch active sheet in Excel workbook.", 0.95)
        return ("Launch Excel / Read from Excel worksheet", "Local desktop Excel workbook manipulation.", 0.94)

    # Workload / Queue in desktop flow
    if "workload" in cmd_lower or "queue" in cmd_lower:
        if "insert" in op_lower or "add" in op_lower:
            return ("Add work queue item", "Directly maps to PAD Work queues 'Add work queue item' action.", 0.95)
        elif "process" in op_lower or "get" in op_lower:
            return ("Process work queue items", "Directly maps to PAD Work queues 'Process work queue items' action.", 0.95)
        elif "update" in op_lower or "status" in op_lower:
            return ("Update work queue item status", "Update status of work queue item in PAD.", 0.95)
        return ("Manage work queue items", "Directly maps to PAD Work queues module.", 0.94)

    # Direct match in DESKTOP_COMMANDS
    if cmd_lower in DESKTOP_COMMANDS:
        target, reason, conf = DESKTOP_COMMANDS[cmd_lower]
        return target, reason, conf

    # Partial / substring matches for desktop operations
    if "browser" in cmd_lower or "web" in cmd_lower:
        return "Launch new Microsoft Edge / UI Automation", "Web browser automation requires Power Automate Desktop browser extension.", 0.92
    if "window" in cmd_lower or "desktop" in cmd_lower:
        return "Focus window / UI Automation", "Desktop UI interaction requires Power Automate Desktop agent.", 0.90
    if "mouse" in cmd_lower or "key" in cmd_lower:
        return "Send keys / Move mouse", "Desktop peripheral simulation requires local execution.", 0.90
    if "script" in cmd_lower or "powershell" in cmd_lower or "python" in cmd_lower or "vbs" in cmd_lower:
        return "Run script (PowerShell / Python / VBScript)", "Local script execution requires PAD script runner.", 0.92
    if "file" in cmd_lower or "folder" in cmd_lower:
        return "File & Folder actions (Read/Write/Copy/Delete)", "Local file system access requires PAD file actions.", 0.93

    return None
