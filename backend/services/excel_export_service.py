import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone

from backend.models.workflow import WorkflowModel
from backend.models.action import ActionModel, DisabledActionModel
from backend.models.variable import VariableModel
from backend.migration.excel_mapping_db import ExcelMappingDB

# Professional Color Palette
NAVY_HEADER = "0F172A"       # Slate 900
SLATE_HEADER = "1E293B"      # Slate 800
WHITE = "FFFFFF"
BORDER_COLOR = "CBD5E1"      # Slate 300
ROW_ALT = "F8FAFC"           # Slate 50
DISABLED_ROW_FILL = "FFFBEB" # Amber 50
DISABLED_STATUS_FILL = "FEE2E2" # Red 100
DISABLED_STATUS_FONT = "991B1B" # Red 800
ACTIVE_STATUS_FILL = "DCFCE7"   # Green 100
ACTIVE_STATUS_FONT = "166534"   # Green 800

# Complexity Badge Palette
COMPLEXITY_STYLES = {
    "Easy": {
        "fill": "DCFCE7",
        "font_color": "166534",
        "label": "EASY MIGRATION (< 200 Steps)",
        "desc": "Low step volume (< 200 steps). Suitable for direct, low-friction migration to Power Automate."
    },
    "Medium": {
        "fill": "FEF3C7",
        "font_color": "92400E",
        "label": "MEDIUM MIGRATION (200 - 400 Steps)",
        "desc": "Moderate step volume (200 to 400 steps). Recommended modular decomposition between Cloud and Desktop."
    },
    "Hard": {
        "fill": "FEE2E2",
        "font_color": "991B1B",
        "label": "HARD MIGRATION (> 400 Steps)",
        "desc": "High step volume (> 400 steps). Multi-phase migration required with subtask decoupling and queue orchestration."
    }
}

class ExcelExportService:
    @classmethod
    def generate_migration_excel(
        cls,
        workflow: WorkflowModel,
        output_path: Path
    ) -> Path:
        """
        Generates the definitive step-by-step Excel migration blueprint.
        """
        wb = openpyxl.Workbook()
        default_sheet = wb.active

        # 1. Sheet 1: Migration Action Mapping (Step by Step)
        ws_steps = wb.create_sheet(title="Migration Action Mapping")
        cls._build_step_mapping_sheet(ws_steps, workflow)

        # 2. Sheet 2: Variables Dictionary
        ws_vars = wb.create_sheet(title="Variables Dictionary")
        cls._build_variables_sheet(ws_vars, workflow)

        # 3. Sheet 3: Disabled Actions Audit
        ws_disabled = wb.create_sheet(title="Disabled Actions Audit")
        cls._build_disabled_sheet(ws_disabled, workflow)

        # 4. Sheet 4: Reference Package Summary
        ws_packages = wb.create_sheet(title="Package Reference Summary")
        cls._build_package_summary_sheet(ws_packages, workflow)

        # Remove initial empty sheet
        if default_sheet in wb.worksheets:
            wb.remove(default_sheet)

        # Ensure directory exists and save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)
        return output_path

    @classmethod
    def _build_step_mapping_sheet(cls, ws, workflow: WorkflowModel):
        stats = workflow.statistics
        total_steps = stats.totalStepsEvaluated or (stats.totalActions + stats.totalDisabledActions)
        complexity = stats.migrationComplexity or ("Hard" if total_steps > 400 else ("Medium" if total_steps >= 200 else "Easy"))
        comp_style = COMPLEXITY_STYLES.get(complexity, COMPLEXITY_STYLES["Easy"])

        thin_border = Border(
            left=Side(style="thin", color=BORDER_COLOR),
            right=Side(style="thin", color=BORDER_COLOR),
            top=Side(style="thin", color=BORDER_COLOR),
            bottom=Side(style="thin", color=BORDER_COLOR)
        )

        # Row 1: Title Banner
        ws.merge_cells("A1:P1")
        ws["A1"] = f"A360 to Microsoft Power Automate Migration Blueprint — {workflow.workflow.name}"
        ws["A1"].font = Font(name="Calibri", size=15, bold=True, color=WHITE)
        ws["A1"].fill = PatternFill("solid", fgColor=NAVY_HEADER)
        ws["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[1].height = 32

        # Row 2: Subtitle / Source info
        ws.merge_cells("A2:P2")
        ws["A2"] = f"Source Bot: {workflow.workflow.name}  |  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  |  Authoritative Mapping: Mapping/AA_to_PowerAutomate_Action_Mapping.xlsx (274 Actions)"
        ws["A2"].font = Font(name="Calibri", size=9, italic=True, color="94A3B8")
        ws["A2"].fill = PatternFill("solid", fgColor=SLATE_HEADER)
        ws["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[2].height = 20

        # Rows 4 to 6: Executive KPI Block
        # Card 1: Complexity Banner (A4:D6)
        ws.merge_cells("A4:D4")
        ws["A4"] = "MIGRATION COMPLEXITY LEVEL"
        ws["A4"].font = Font(name="Calibri", size=9, bold=True, color="64748B")
        ws["A4"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("A5:D5")
        ws["A5"] = comp_style["label"]
        ws["A5"].font = Font(name="Calibri", size=14, bold=True, color=comp_style["font_color"])
        ws["A5"].fill = PatternFill("solid", fgColor=comp_style["fill"])
        ws["A5"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("A6:D6")
        ws["A6"] = comp_style["desc"]
        ws["A6"].font = Font(name="Calibri", size=8, italic=True, color="475569")
        ws["A6"].alignment = Alignment(horizontal="center", vertical="center")

        # Card 2: Step Volumes (E4:H6)
        ws.merge_cells("E4:H4")
        ws["E4"] = "STEP VOLUME BREAKDOWN"
        ws["E4"].font = Font(name="Calibri", size=9, bold=True, color="64748B")
        ws["E4"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("E5:H5")
        ws["E5"] = f"Total Steps: {total_steps}  |  Active: {stats.totalActions}  |  Disabled: {stats.totalDisabledActions}"
        ws["E5"].font = Font(name="Calibri", size=12, bold=True, color="0F172A")
        ws["E5"].fill = PatternFill("solid", fgColor="F1F5F9")
        ws["E5"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("E6:H6")
        pct_active = round((stats.totalActions / total_steps * 100) if total_steps > 0 else 100, 1)
        pct_dis = round((stats.totalDisabledActions / total_steps * 100) if total_steps > 0 else 0, 1)
        ws["E6"] = f"Active Logic: {pct_active}%  |  Disabled Logic: {pct_dis}%  (Rules: < 200 = Easy, 200-400 = Medium, > 400 = Hard)"
        ws["E6"].font = Font(name="Calibri", size=8, italic=True, color="475569")
        ws["E6"].alignment = Alignment(horizontal="center", vertical="center")

        # Card 3: Target Architecture Distribution (I4:L6)
        ws.merge_cells("I4:L4")
        ws["I4"] = "TARGET POWER AUTOMATE PLATFORM"
        ws["I4"].font = Font(name="Calibri", size=9, bold=True, color="64748B")
        ws["I4"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("I5:L5")
        ws["I5"] = f"Desktop (PAD): {stats.desktopActions}  |  Cloud: {stats.cloudActions}  |  Hybrid: {stats.hybridActions}"
        ws["I5"].font = Font(name="Calibri", size=11, bold=True, color="1E3A8A")
        ws["I5"].fill = PatternFill("solid", fgColor="DBEAFE")
        ws["I5"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("I6:L6")
        ws["I6"] = f"Manual Review Steps: {stats.manualReviewActions}  |  Tasks/Subtasks: {stats.totalTasks}"
        ws["I6"].font = Font(name="Calibri", size=8, italic=True, color="475569")
        ws["I6"].alignment = Alignment(horizontal="center", vertical="center")

        # Card 4: Downstream Handoff Notice (M4:P6)
        ws.merge_cells("M4:P4")
        ws["M4"] = "DOWNSTREAM AGENT DIRECTIVE"
        ws["M4"].font = Font(name="Calibri", size=9, bold=True, color="64748B")
        ws["M4"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("M5:P5")
        ws["M5"] = "Publication-Grade Migration Specification"
        ws["M5"].font = Font(name="Calibri", size=11, bold=True, color="065F46")
        ws["M5"].fill = PatternFill("solid", fgColor="D1FAE5")
        ws["M5"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("M6:P6")
        ws["M6"] = "All actions mapped to Power Automate with parameters, variables & disabled flags."
        ws["M6"].font = Font(name="Calibri", size=8, italic=True, color="475569")
        ws["M6"].alignment = Alignment(horizontal="center", vertical="center")

        for r in range(4, 7):
            ws.row_dimensions[r].height = 20

        # Table Headers (Row 8)
        headers = [
            "Step #",
            "Status",
            "Taskbot / File",
            "AA Package",
            "AA Action",
            "AA Action Description",
            "Target Platform",
            "PAD Category",
            "PAD Equivalent Action",
            "PA Cloud Equivalent Action / Connector",
            "Target Recommended Action",
            "Configured Parameters / Attributes",
            "Variables Read",
            "Variables Written",
            "Disabled Reason",
            "Migration Guidance & Notes"
        ]

        ws.row_dimensions[8].height = 28
        for col_num, h in enumerate(headers, 1):
            cell = ws.cell(row=8, column=col_num, value=h)
            cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
            cell.fill = PatternFill("solid", fgColor=SLATE_HEADER)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border

        # Combine active and disabled steps in chronological order
        step_entries: List[Dict[str, Any]] = []

        for a in workflow.actions:
            attrs_str = "; ".join(f"{k}: {v}" for k, v in a.attributes.items() if k not in ("action", "operation")) if isinstance(a.attributes, dict) else str(a.attributes)
            step_entries.append({
                "sort_step": a.step,
                "status": "ACTIVE",
                "task": a.task,
                "aa_package": a.aaPackage or a.command,
                "aa_action": a.aaAction or a.operation or "Execute",
                "aa_desc": a.aaDescription or "",
                "platform": a.cloudOrDesktop,
                "pad_category": a.padCategory or "",
                "pad_action": a.padAction or "",
                "cloud_action": a.cloudAction or "",
                "rec_action": a.powerAutomateAction,
                "params": attrs_str,
                "vars_read": ", ".join(a.variablesUsed),
                "vars_written": ", ".join(a.variablesCreated),
                "disabled_reason": "N/A (Active in Production Flow)",
                "notes": a.migrationNotes or a.reason or ""
            })

        for da in workflow.disabledActions:
            attrs_str = "; ".join(f"{k}: {v}" for k, v in da.attributes.items() if k not in ("action", "operation")) if isinstance(da.attributes, dict) else str(da.attributes)
            step_entries.append({
                "sort_step": da.originalStep,
                "status": "DISABLED",
                "task": da.task,
                "aa_package": da.aaPackage or da.command,
                "aa_action": da.aaAction or da.action or "Execute",
                "aa_desc": da.aaDescription or "",
                "platform": da.targetPlatform or "Power Automate Desktop",
                "pad_category": da.padCategory or "",
                "pad_action": da.padAction or "",
                "cloud_action": da.cloudAction or "",
                "rec_action": da.recommendedAction or da.padAction or "Disabled Step",
                "params": attrs_str,
                "vars_read": "",
                "vars_written": "",
                "disabled_reason": da.reason or "Action was disabled in A360",
                "notes": da.migrationNotes or "Action was disabled in source A360 bot. Verify requirement before porting."
            })

        # Sort entries by step sequence
        step_entries.sort(key=lambda x: x["sort_step"])

        # Write data rows
        current_row = 9
        for idx, entry in enumerate(step_entries, 1):
            is_disabled = entry["status"] == "DISABLED"
            row_fill = PatternFill("solid", fgColor=DISABLED_ROW_FILL if is_disabled else (ROW_ALT if idx % 2 == 0 else WHITE))

            row_values = [
                idx,  # Step #
                entry["status"],
                entry["task"],
                entry["aa_package"],
                entry["aa_action"],
                entry["aa_desc"],
                entry["platform"],
                entry["pad_category"],
                entry["pad_action"],
                entry["cloud_action"],
                entry["rec_action"],
                entry["params"],
                entry["vars_read"],
                entry["vars_written"],
                entry["disabled_reason"],
                entry["notes"]
            ]

            for col_idx, val in enumerate(row_values, 1):
                cell = ws.cell(row=current_row, column=col_idx, value=val)
                cell.font = Font(name="Calibri", size=9, color="0F172A")
                cell.fill = row_fill
                cell.border = thin_border

                # Alignment rules
                if col_idx in (1, 2, 7, 8):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

                # Special Status pill styling
                if col_idx == 2:
                    if is_disabled:
                        cell.fill = PatternFill("solid", fgColor=DISABLED_STATUS_FILL)
                        cell.font = Font(name="Calibri", size=9, bold=True, color=DISABLED_STATUS_FONT)
                    else:
                        cell.fill = PatternFill("solid", fgColor=ACTIVE_STATUS_FILL)
                        cell.font = Font(name="Calibri", size=9, bold=True, color=ACTIVE_STATUS_FONT)

            ws.row_dimensions[current_row].height = 24
            current_row += 1

        # Auto-adjust column widths
        col_widths = {
            1: 9,   # Step #
            2: 13,  # Status
            3: 16,  # Taskbot
            4: 18,  # AA Package
            5: 18,  # AA Action
            6: 30,  # AA Action Description
            7: 24,  # Target Platform
            8: 18,  # PAD Category
            9: 26,  # PAD Equivalent Action
            10: 28, # PA Cloud Equivalent
            11: 28, # Target Recommended Action
            12: 35, # Parameters
            13: 16, # Vars Read
            14: 16, # Vars Written
            15: 25, # Disabled Reason
            16: 35  # Migration Notes
        }
        for col_num, w in col_widths.items():
            col_letter = get_column_letter(col_num)
            ws.column_dimensions[col_letter].width = w

        # Enable Auto-Filter on table header
        ws.auto_filter.ref = f"A8:P{current_row - 1}"

        # Freeze panes at row 9 (headers remain fixed)
        ws.freeze_panes = "A9"

    @classmethod
    def _build_variables_sheet(cls, ws, workflow: WorkflowModel):
        thin_border = Border(
            left=Side(style="thin", color=BORDER_COLOR),
            right=Side(style="thin", color=BORDER_COLOR),
            top=Side(style="thin", color=BORDER_COLOR),
            bottom=Side(style="thin", color=BORDER_COLOR)
        )

        ws.merge_cells("A1:J1")
        ws["A1"] = f"Variables & Data Types Dictionary — {workflow.workflow.name}"
        ws["A1"].font = Font(name="Calibri", size=14, bold=True, color=WHITE)
        ws["A1"].fill = PatternFill("solid", fgColor=NAVY_HEADER)
        ws["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[1].height = 30

        headers = [
            "Variable Name",
            "A360 Type",
            "Scope",
            "Direction",
            "Default / Constant Value",
            "PA Target Type",
            "PAD Initialization Syntax",
            "Cloud Flow Syntax / Action",
            "Used in Steps",
            "Description"
        ]

        ws.row_dimensions[3].height = 26
        for col_idx, h in enumerate(headers, 1):
            c = ws.cell(row=3, column=col_idx, value=h)
            c.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
            c.fill = PatternFill("solid", fgColor=SLATE_HEADER)
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = thin_border

        current_row = 4
        for idx, var in enumerate(workflow.variables, 1):
            row_fill = PatternFill("solid", fgColor=ROW_ALT if idx % 2 == 0 else WHITE)
            dir_str = "Input" if getattr(var, "isInput", False) else ("Output" if getattr(var, "isOutput", False) else "Local")
            init_val = getattr(var, "initialValue", None) or getattr(var, "defaultValue", "")
            pa_type = getattr(var, "powerAutomateEquivalent", None) or getattr(var, "powerAutomateEquivalentType", None) or var.type

            vals = [
                var.name,
                var.type,
                var.scope,
                dir_str,
                str(init_val) if init_val is not None else "",
                pa_type,
                f"Set variable %{var.name}%",
                f"Initialize variable ({pa_type})",
                ", ".join(map(str, var.usedInSteps)),
                var.description or ""
            ]

            for c_idx, val in enumerate(vals, 1):
                c = ws.cell(row=current_row, column=c_idx, value=val)
                c.font = Font(name="Calibri", size=9)
                c.fill = row_fill
                c.border = thin_border
                c.alignment = Alignment(horizontal="left", vertical="center")

            current_row += 1

        col_widths = {1: 22, 2: 14, 3: 14, 4: 12, 5: 25, 6: 18, 7: 28, 8: 30, 9: 16, 10: 30}
        for col_num, w in col_widths.items():
            ws.column_dimensions[get_column_letter(col_num)].width = w

        ws.auto_filter.ref = f"A3:J{max(3, current_row - 1)}"
        ws.freeze_panes = "A4"

    @classmethod
    def _build_disabled_sheet(cls, ws, workflow: WorkflowModel):
        thin_border = Border(
            left=Side(style="thin", color=BORDER_COLOR),
            right=Side(style="thin", color=BORDER_COLOR),
            top=Side(style="thin", color=BORDER_COLOR),
            bottom=Side(style="thin", color=BORDER_COLOR)
        )

        ws.merge_cells("A1:H1")
        ws["A1"] = f"Disabled Actions Audit Log — {workflow.workflow.name}"
        ws["A1"].font = Font(name="Calibri", size=14, bold=True, color=WHITE)
        ws["A1"].fill = PatternFill("solid", fgColor="7F1D1D")
        ws["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[1].height = 30

        headers = [
            "Original Step #",
            "Taskbot / File",
            "A360 Command",
            "A360 Action",
            "PA Target Equivalent",
            "Disabled Reason",
            "Original Attributes",
            "Downstream Migration Action Required"
        ]

        ws.row_dimensions[3].height = 26
        for col_idx, h in enumerate(headers, 1):
            c = ws.cell(row=3, column=col_idx, value=h)
            c.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
            c.fill = PatternFill("solid", fgColor="991B1B")
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = thin_border

        current_row = 4
        for idx, da in enumerate(workflow.disabledActions, 1):
            row_fill = PatternFill("solid", fgColor=DISABLED_ROW_FILL if idx % 2 == 0 else WHITE)
            attrs_str = "; ".join(f"{k}: {v}" for k, v in da.attributes.items()) if isinstance(da.attributes, dict) else str(da.attributes)

            vals = [
                da.originalStep,
                da.task,
                da.command,
                da.action,
                da.recommendedAction or da.padAction or "Disabled Step",
                da.reason,
                attrs_str,
                "Review with business analyst. If decommissioned, omit from Power Automate. If temporarily paused, port as disabled subflow."
            ]

            for c_idx, val in enumerate(vals, 1):
                c = ws.cell(row=current_row, column=c_idx, value=val)
                c.font = Font(name="Calibri", size=9)
                c.fill = row_fill
                c.border = thin_border
                c.alignment = Alignment(horizontal="left" if c_idx > 1 else "center", vertical="center", wrap_text=True)

            current_row += 1

        col_widths = {1: 15, 2: 18, 3: 18, 4: 18, 5: 25, 6: 25, 7: 35, 8: 35}
        for col_num, w in col_widths.items():
            ws.column_dimensions[get_column_letter(col_num)].width = w

        ws.auto_filter.ref = f"A3:H{max(3, current_row - 1)}"
        ws.freeze_panes = "A4"

    @classmethod
    def _build_package_summary_sheet(cls, ws, workflow: WorkflowModel):
        thin_border = Border(
            left=Side(style="thin", color=BORDER_COLOR),
            right=Side(style="thin", color=BORDER_COLOR),
            top=Side(style="thin", color=BORDER_COLOR),
            bottom=Side(style="thin", color=BORDER_COLOR)
        )

        ws.merge_cells("A1:E1")
        ws["A1"] = "Authoritative A360 to Power Automate Package Reference"
        ws["A1"].font = Font(name="Calibri", size=14, bold=True, color=WHITE)
        ws["A1"].fill = PatternFill("solid", fgColor=NAVY_HEADER)
        ws["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[1].height = 30

        headers = [
            "AA Package Name",
            "Mapped Actions in Reference",
            "Primary PA Platform",
            "PAD Category",
            "Coverage Status in Current Bot"
        ]

        ws.row_dimensions[3].height = 26
        for col_idx, h in enumerate(headers, 1):
            c = ws.cell(row=3, column=col_idx, value=h)
            c.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
            c.fill = PatternFill("solid", fgColor=SLATE_HEADER)
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = thin_border

        db = ExcelMappingDB.get_instance()
        packages_map: Dict[str, List[Dict[str, Any]]] = {}
        for m in db.mappings:
            pkg = m["aa_package"]
            packages_map.setdefault(pkg, []).append(m)

        used_packages = set(a.aaPackage or a.command for a in workflow.actions)
        used_packages.update(da.aaPackage or da.command for da in workflow.disabledActions)

        current_row = 4
        for idx, (pkg, items) in enumerate(sorted(packages_map.items()), 1):
            row_fill = PatternFill("solid", fgColor=ROW_ALT if idx % 2 == 0 else WHITE)
            first = items[0]
            cat = first.get("pad_category", "")
            is_used = any(pkg.lower() == up.lower() for up in used_packages)

            cloud_count = sum(1 for x in items if x.get("cloud_action") and "no direct" not in x["cloud_action"].lower())
            primary_platform = "Power Automate Cloud" if cloud_count > len(items) // 2 else "Power Automate Desktop"

            vals = [
                pkg,
                len(items),
                primary_platform,
                cat,
                "Present in Bot" if is_used else "Reference Library"
            ]

            for c_idx, val in enumerate(vals, 1):
                c = ws.cell(row=current_row, column=c_idx, value=val)
                c.font = Font(name="Calibri", size=9, bold=(is_used if c_idx == 5 else False))
                c.fill = row_fill
                c.border = thin_border
                c.alignment = Alignment(horizontal="center" if c_idx in (2, 3, 5) else "left", vertical="center")
                if c_idx == 5 and is_used:
                    c.fill = PatternFill("solid", fgColor="DCFCE7")
                    c.font = Font(name="Calibri", size=9, bold=True, color="166534")

            current_row += 1

        col_widths = {1: 26, 2: 24, 3: 26, 4: 24, 5: 26}
        for col_num, w in col_widths.items():
            ws.column_dimensions[get_column_letter(col_num)].width = w

        ws.auto_filter.ref = f"A3:E{current_row - 1}"
        ws.freeze_panes = "A4"
