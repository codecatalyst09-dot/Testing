import os
import openpyxl
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

MAPPING_FILE_PATH = Path(__file__).parent.parent.parent / "Mapping" / "AA_to_PowerAutomate_Action_Mapping.xlsx"

class ExcelMappingDB:
    _instance = None
    _mappings: List[Dict[str, Any]] = []
    _lookup: Dict[str, Dict[str, Any]] = {}

    @property
    def mappings(self) -> List[Dict[str, Any]]:
        return self._mappings

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load_mappings()
        return cls._instance

    def _load_mappings(self):
        self._mappings = []
        self._lookup = {}

        if not MAPPING_FILE_PATH.exists():
            return

        try:
            wb = openpyxl.load_workbook(MAPPING_FILE_PATH, data_only=True)
            if "Mapping" not in wb.sheetnames:
                return
            ws = wb["Mapping"]
            headers = [cell.value for cell in ws[1]]
            
            # Map column indices
            pkg_col = headers.index("AA Package") if "AA Package" in headers else 0
            act_col = headers.index("AA Action") if "AA Action" in headers else 1
            desc_col = headers.index("AA Action Description") if "AA Action Description" in headers else 2
            
            # Find PAD Category, PAD Equivalent, PA Cloud Equivalent, Notes
            pad_cat_col = next((i for i, h in enumerate(headers) if h and "PAD Category" in str(h) or "Desktop" in str(h) and "Category" in str(h)), 3)
            pad_eq_col = next((i for i, h in enumerate(headers) if h and "PAD Equivalent" in str(h) or "Desktop" in str(h) and "Equivalent" in str(h)), 4)
            cloud_eq_col = next((i for i, h in enumerate(headers) if h and "Cloud" in str(h) and "Equivalent" in str(h)), 5)
            notes_col = next((i for i, h in enumerate(headers) if h and "Migration Notes" in str(h) or "Notes" in str(h)), 6)

            for r in range(2, ws.max_row + 1):
                vals = [cell.value for cell in ws[r]]
                if not any(v is not None for v in vals):
                    continue

                pkg = str(vals[pkg_col]).strip() if vals[pkg_col] is not None else ""
                act = str(vals[act_col]).strip() if vals[act_col] is not None else ""
                desc = str(vals[desc_col]).strip() if desc_col < len(vals) and vals[desc_col] is not None else ""
                pad_cat = str(vals[pad_cat_col]).strip() if pad_cat_col < len(vals) and vals[pad_cat_col] is not None else ""
                pad_act = str(vals[pad_eq_col]).strip() if pad_eq_col < len(vals) and vals[pad_eq_col] is not None else ""
                cloud_act = str(vals[cloud_eq_col]).strip() if cloud_eq_col < len(vals) and vals[cloud_eq_col] is not None else ""
                notes = str(vals[notes_col]).strip() if notes_col < len(vals) and vals[notes_col] is not None else ""

                entry = {
                    "aa_package": pkg,
                    "aa_action": act,
                    "aa_description": desc,
                    "pad_category": pad_cat,
                    "pad_action": pad_act,
                    "cloud_action": cloud_act,
                    "migration_notes": notes,
                }
                self._mappings.append(entry)

                # Store key variations for robust lookup
                key1 = f"{pkg.lower()}|{act.lower()}"
                self._lookup[key1] = entry

                # Package only fallback
                pkg_key = pkg.lower()
                if pkg_key not in self._lookup:
                    self._lookup[pkg_key] = entry

        except Exception as e:
            print(f"Error loading Excel mapping: {e}")

    def find_mapping(self, command: str, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Lookup mapping from the official Excel database.
        """
        cmd_clean = (command or "").strip()
        op_clean = (operation or "").strip()
        cmd_lower = cmd_clean.lower()
        op_lower = op_clean.lower()

        # Command aliases mapping to official AA Packages
        alias_map = {
            "excel": "Excel Advanced",
            "excelbasic": "Excel Basic",
            "exceladvanced": "Excel Advanced",
            "runtask": "Task Bot",
            "subtask": "Task Bot",
            "taskbot": "Task Bot",
            "http": "REST Web Service",
            "rest": "REST Web Service",
            "restapi": "REST Web Service",
            "restwebservice": "REST Web Service",
            "sendemail": "Email",
            "mail": "Email",
            "outlook": "Email",
            "csv": "CSV/TXT",
            "datatable": "Data Table",
            "table": "Data Table",
            "webautomation": "Browser",
            "capture": "Recorder",
            "messagebox": "Message box",
            "prompt": "Prompt",
            "python": "Python Script",
            "vbs": "VBScript",
            "javascript": "JavaScript",
            "string": "String",
            "number": "Number",
            "boolean": "Boolean",
            "datetime": "DateTime",
            "loop": "Loop",
            "if": "If",
            "delay": "Delay",
            "wait": "Wait",
            "file": "File",
            "folder": "Folder",
            "database": "Database",
            "sql": "Database",
            "activedirectory": "Active Directory",
            "clipboard": "Clipboard",
            "ocr": "OCR",
            "pdf": "PDF",
            "window": "Window",
            "xml": "XML",
            "json": "JSON",
            "sap": "SAP",
            "sapgui": "SAP",
            "workload": "Workload",
            "queue": "Workload",
            "iqbot": "OCR",
            "iq bot": "OCR",
            "errorhandler": "Error Handler",
            "error handling": "Error Handler",
        }

        matched_pkg = alias_map.get(cmd_lower.replace(" ", "").replace("_", ""), cmd_clean)

        # 1. Exact match package|action
        key = f"{matched_pkg.lower()}|{op_lower}"
        if key in self._lookup:
            return self._format_result(self._lookup[key], cmd_clean, op_clean)

        # 2. Match by package with similar action
        pkg_lower = matched_pkg.lower()
        for item in self._mappings:
            if item["aa_package"].lower() == pkg_lower:
                if op_lower and op_lower in item["aa_action"].lower():
                    return self._format_result(item, cmd_clean, op_clean)

        # 3. Match by package general row
        for item in self._mappings:
            if item["aa_package"].lower() == pkg_lower:
                return self._format_result(item, cmd_clean, op_clean)

        # 4. Keyword search across actions in database
        for item in self._mappings:
            if cmd_lower in item["aa_package"].lower() or (op_lower and op_lower in item["aa_action"].lower()):
                return self._format_result(item, cmd_clean, op_clean)

        # 5. Unknown command policy
        return {
            "aa_package": cmd_clean,
            "aa_action": op_clean or "Execute",
            "aa_description": "Custom or proprietary Automation Anywhere action.",
            "pad_category": "Manual Review Required",
            "pad_action": f"Manual Review ({cmd_clean})",
            "cloud_action": "No direct equivalent",
            "platform": "Manual Review",
            "recommended_action": f"Manual Review: {cmd_clean}",
            "migration_notes": "Action not found in standard A360 mapping reference. Review original bot logic and select equivalent connector or script."
        }

    def _format_result(self, raw_entry: Dict[str, Any], orig_cmd: str, orig_op: str) -> Dict[str, Any]:
        pad_action = raw_entry.get("pad_action", "")
        cloud_action = raw_entry.get("cloud_action", "")
        notes = raw_entry.get("migration_notes") or ""

        # Determine target platform based on Excel definitions
        # If Cloud has "No direct equivalent", it must be Desktop
        is_cloud_unsupported = (
            not cloud_action or
            "no direct" in cloud_action.lower() or
            "no native" in cloud_action.lower() or
            cloud_action.strip().lower() == "none"
        )

        if orig_cmd.lower() in ("runtask", "taskbot", "subtask") or raw_entry["aa_package"] == "Task Bot":
            platform = "Hybrid"
            rec_action = "Run a flow built with Power Automate for desktop (or Run Child Flow)"
        elif is_cloud_unsupported:
            platform = "Power Automate Desktop"
            rec_action = pad_action
        else:
            # Check if package is typically cloud-native
            if raw_entry["aa_package"] in ("REST Web Service", "SOAP Web Service", "Email", "Google Drive", "Google Sheets"):
                platform = "Power Automate Cloud"
                rec_action = cloud_action
            else:
                platform = "Power Automate Desktop"
                rec_action = pad_action

        return {
            "aa_package": raw_entry.get("aa_package", orig_cmd),
            "aa_action": orig_op or raw_entry.get("aa_action", ""),
            "aa_description": raw_entry.get("aa_description", ""),
            "pad_category": raw_entry.get("pad_category", "Custom"),
            "pad_action": pad_action,
            "cloud_action": cloud_action,
            "platform": platform,
            "recommended_action": rec_action,
            "migration_notes": notes
        }
