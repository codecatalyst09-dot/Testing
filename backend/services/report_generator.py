import json
from typing import Dict, Any, List
from backend.models.workflow import WorkflowModel
from backend.models.migration import MigrationPlanModel

class ReportGenerator:
    @staticmethod
    def generate_markdown(workflow: WorkflowModel, plan: MigrationPlanModel) -> str:
        s = workflow.statistics
        lines = []
        lines.append(f"# A360 to Microsoft Power Automate Migration Blueprint")
        lines.append(f"**Automation:** {workflow.workflow.name}  ")
        lines.append(f"**Generated:** Automated Analysis by A360 Migration Analyzer  ")
        lines.append(f"**Target Architecture:** {plan.architecture.architectureType}  \n")

        # 1. Executive Summary
        lines.append("## 1. Executive Summary\n")
        lines.append(f"This migration blueprint analyzes Automation Anywhere A360 automation **{workflow.workflow.name}** "
                     f"and provides actionable architecture, action mappings, variable translations, and dependency specifications "
                     f"for Microsoft Power Automate.\n")
        lines.append("| Metric | Count | Distribution |")
        lines.append("|---|---|---|")
        lines.append(f"| **Total Workflows** | {s.totalWorkflows} | - |")
        lines.append(f"| **Total Tasks / Taskbots** | {s.totalTasks} | - |")
        lines.append(f"| **Total Action Steps** | {s.totalActions} | 100% |")
        lines.append(f"| ☁️ **Power Automate Cloud** | {s.cloudActions} | {s.platformDistribution.get('Power Automate Cloud', 0)}% |")
        lines.append(f"| 🖥️ **Power Automate Desktop (PAD)** | {s.desktopActions} | {s.platformDistribution.get('Power Automate Desktop', 0)}% |")
        lines.append(f"| 🔀 **Hybrid Orchestration** | {s.hybridActions} | {s.platformDistribution.get('Hybrid', 0)}% |")
        lines.append(f"| ⚠️ **Manual Review Required** | {s.manualReviewActions} | {s.platformDistribution.get('Manual Review', 0)}% |")
        lines.append(f"| **Extracted Variables** | {s.totalVariables} | - |")
        lines.append(f"| **Subtask Invocations** | {s.totalSubtasks} | - |")
        lines.append(f"| **Disabled Actions Preserved** | {s.totalDisabledActions} | - |")
        lines.append(f"| **Estimated Migration Effort** | ~{plan.estimated_effort_hours} hours | Base + Step complexity |\n")

        # 2. Workflow Architecture
        lines.append("## 2. Original A360 Architecture\n")
        lines.append(f"The source package comprises **{len(workflow.tasks)} taskbots** interacting with local and remote systems.\n")
        for t in workflow.tasks:
            lines.append(f"- **{t.name}** ({'Main Taskbot' if t.isMain else 'Subtask'}): {t.purpose}. Steps: {t.stepsCount}. Classification: `{t.cloudOrDesktop}`.")
        lines.append("")

        # 3. Target Power Automate Architecture
        lines.append("## 3. Recommended Power Automate Target Architecture\n")
        lines.append(f"**Pattern:** {plan.architecture.orchestrationPattern}\n")
        lines.append(f"> {plan.architecture.summary}\n")
        lines.append("### 3.1 Cloud Flows")
        for cf in plan.architecture.cloudFlows:
            lines.append(f"- **{cf.name}**: {cf.description}")
            lines.append(f"  - Trigger: `{cf.trigger.get('type')}`")
            lines.append(f"  - Key Actions: {len(cf.actions)} steps")
            if cf.connectionsNeeded:
                lines.append(f"  - Required Connections: {', '.join(cf.connectionsNeeded)}")
        lines.append("\n### 3.2 Desktop Flows (PAD)")
        for df in plan.architecture.desktopFlows:
            lines.append(f"- **{df.name}**: {df.description}")
            lines.append(f"  - Subroutines: {', '.join(df.subroutines)}")
            lines.append(f"  - Action Count: {len(df.actions)}")
            if df.prerequisites:
                lines.append(f"  - Host Prerequisites: {', '.join(df.prerequisites)}")
        lines.append("")

        # 4. Action-by-Action Migration Mapping
        lines.append("## 4. Action-by-Action Migration Mapping\n")
        lines.append("| Step | Task | A360 Command | Target Platform | Power Automate Action | Strategy | Complexity | Confidence |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for a in workflow.actions:
            lines.append(
                f"| {a.step} | {a.task} | `{a.command}` | {a.cloudOrDesktop} | **{a.powerAutomateAction}** | {a.migrationStrategy} | {a.migrationComplexity} | {int(a.confidence*100)}% |"
            )
        lines.append("")

        # 5. Variable Mapping
        lines.append("## 5. Variable Mapping & Translation\n")
        lines.append("| Variable Name | A360 Type | Scope | Usage | Power Automate Equivalent | Referenced in Steps |")
        lines.append("|---|---|---|---|---|---|")
        for v in workflow.variables:
            steps_str = ", ".join(str(s) for s in v.usedInSteps[:8])
            if len(v.usedInSteps) > 8:
                steps_str += f" (+{len(v.usedInSteps)-8} more)"
            lines.append(
                f"| `{v.name}` | {v.type} | {v.scope} | {v.usage} | **{v.powerAutomateEquivalent}** | {steps_str or 'None'} |"
            )
        lines.append("")

        # 6. Disabled Actions
        lines.append("## 6. Disabled Actions (Recorded Prior to Pruning)\n")
        if workflow.disabledActions:
            lines.append("| Original Step | Task | Command | Action / Operation | Reason | Location |")
            lines.append("|---|---|---|---|---|---|")
            for da in workflow.disabledActions:
                lines.append(f"| {da.originalStep} | {da.task} | `{da.command}` | {da.action} | {da.reason} | {da.location or 'N/A'} |")
        else:
            lines.append("_No disabled actions were found in this A360 automation._")
        lines.append("")

        # 7. External Dependencies
        lines.append("## 7. External System Dependencies\n")
        lines.append("| Dependency | Type | Required by Tasks | Recommended Power Automate Mechanism |")
        lines.append("|---|---|---|---|")
        for d in workflow.dependencies:
            lines.append(f"| **{d.name}** | {d.type} | {', '.join(d.requiredByTasks)} | {d.suggestedPAMechanism} |")
        lines.append("")

        # 8. Migration Risks & Mitigation
        lines.append("## 8. Technical Migration Risks & Considerations\n")
        for r in plan.migration_risks:
            lines.append(f"### ⚠️ [{r['severity']}] {r['title']}")
            lines.append(f"- **Risk:** {r['description']}")
            lines.append(f"- **Mitigation:** {r['mitigation']}\n")

        # 9. Manual Review Items
        lines.append("## 9. Manual Review Items\n")
        if plan.manual_review_items:
            lines.append("The following actions require RPA developer investigation because no automatic direct rule exists:\n")
            for m in plan.manual_review_items:
                lines.append(f"- **Step {m['step']} ({m['command']}) in task `{m['task']}`:** {m['reason']}")
                lines.append(f"  - _Guidance:_ {m['suggestedAction']}")
        else:
            lines.append("✅ All actions have validated deterministic Power Automate mapping rules.")
        lines.append("")

        # 10. Implementation Roadmap
        lines.append("## 10. Suggested Migration Roadmap\n")
        for phase in plan.architecture.migrationRoadmapPhases:
            lines.append(f"### {phase['phase']} (~{phase['durationDays']} days)")
            for task in phase['tasks']:
                lines.append(f"- [ ] {task}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def generate_html(workflow: WorkflowModel, plan: MigrationPlanModel, markdown_content: str) -> str:
        s = workflow.statistics
        actions_rows = "".join([
            f"<tr>"
            f"<td>{a.step}</td>"
            f"<td><span class='badge task'>{a.task}</span></td>"
            f"<td><code>{a.command}</code></td>"
            f"<td><span class='badge {a.cloudOrDesktop.lower().replace(' ', '-')}'>{a.cloudOrDesktop}</span></td>"
            f"<td><strong>{a.powerAutomateAction}</strong></td>"
            f"<td>{a.migrationStrategy}</td>"
            f"<td><span class='badge {a.migrationComplexity.lower()}'>{a.migrationComplexity}</span></td>"
            f"<td>{int(a.confidence*100)}%</td>"
            f"</tr>"
            for a in workflow.actions
        ])

        variables_rows = "".join([
            f"<tr>"
            f"<td><code>{v.name}</code></td>"
            f"<td>{v.type}</td>"
            f"<td>{v.scope}</td>"
            f"<td>{v.usage}</td>"
            f"<td><strong>{v.powerAutomateEquivalent}</strong></td>"
            f"<td>{', '.join(str(st) for st in v.usedInSteps[:5])}</td>"
            f"</tr>"
            for v in workflow.variables
        ])

        disabled_rows = "".join([
            f"<tr>"
            f"<td>{da.originalStep}</td>"
            f"<td>{da.task}</td>"
            f"<td><code>{da.command}</code></td>"
            f"<td>{da.action}</td>"
            f"<td>{da.reason}</td>"
            f"</tr>"
            for da in workflow.disabledActions
        ]) or "<tr><td colspan='5'>No disabled actions recorded.</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>A360 to Power Automate Migration Blueprint - {workflow.workflow.name}</title>
  <style>
    :root {{
      --primary: #2563eb;
      --bg: #f8fafc;
      --card: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --muted: #64748b;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      margin: 0;
      padding: 32px;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      background: var(--card);
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }}
    h1, h2, h3 {{ color: #1e293b; font-weight: 700; }}
    h1 {{ border-bottom: 2px solid var(--primary); padding-bottom: 12px; margin-top: 0; }}
    h2 {{ border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-top: 32px; }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin: 24px 0;
    }}
    .stat-card {{
      background: #f1f5f9;
      padding: 16px;
      border-radius: 8px;
      text-align: center;
      border: 1px solid var(--border);
    }}
    .stat-val {{ font-size: 28px; font-weight: 800; color: var(--primary); }}
    .stat-lbl {{ font-size: 13px; color: var(--muted); text-transform: uppercase; font-weight: 600; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0 24px 0;
      font-size: 14px;
    }}
    th, td {{
      padding: 10px 14px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{ background: #f8fafc; font-weight: 600; color: #475569; }}
    code {{ background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 13px; }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
    }}
    .power-automate-cloud {{ background: #dbeafe; color: #1e40af; }}
    .power-automate-desktop {{ background: #ede9fe; color: #5b21b6; }}
    .hybrid {{ background: #fef3c7; color: #92400e; }}
    .manual-review {{ background: #fee2e2; color: #991b1b; }}
    .low {{ background: #dcfce7; color: #166534; }}
    .medium {{ background: #fef9c3; color: #854d0e; }}
    .high {{ background: #fee2e2; color: #991b1b; }}
    .alert-box {{
      background: #f8fafc;
      border-left: 4px solid var(--primary);
      padding: 14px 18px;
      border-radius: 4px;
      margin: 16px 0;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>A360 to Microsoft Power Automate Migration Blueprint</h1>
    <p><strong>Package:</strong> {workflow.workflow.name} &nbsp;|&nbsp; <strong>Target Architecture:</strong> {plan.architecture.architectureType}</p>

    <div class="stats-grid">
      <div class="stat-card"><div class="stat-val">{s.totalActions}</div><div class="stat-lbl">Total Steps</div></div>
      <div class="stat-card"><div class="stat-val" style="color: #2563eb;">{s.cloudActions}</div><div class="stat-lbl">Cloud Actions</div></div>
      <div class="stat-card"><div class="stat-val" style="color: #7c3aed;">{s.desktopActions}</div><div class="stat-lbl">Desktop Actions</div></div>
      <div class="stat-card"><div class="stat-val" style="color: #d97706;">{s.hybridActions}</div><div class="stat-lbl">Hybrid Actions</div></div>
      <div class="stat-card"><div class="stat-val" style="color: #dc2626;">{s.manualReviewActions}</div><div class="stat-lbl">Manual Review</div></div>
      <div class="stat-card"><div class="stat-val">{s.totalVariables}</div><div class="stat-lbl">Variables</div></div>
      <div class="stat-card"><div class="stat-val">~{plan.estimated_effort_hours}h</div><div class="stat-lbl">Est. Effort</div></div>
    </div>

    <div class="alert-box">
      <strong>Target Architecture Summary:</strong> {plan.architecture.summary}
    </div>

    <h2>Action-by-Action Migration Mapping</h2>
    <table>
      <thead>
        <tr>
          <th>Step</th>
          <th>Task</th>
          <th>A360 Command</th>
          <th>Target Platform</th>
          <th>Power Automate Action</th>
          <th>Strategy</th>
          <th>Complexity</th>
          <th>Confidence</th>
        </tr>
      </thead>
      <tbody>
        {actions_rows}
      </tbody>
    </table>

    <h2>Variable Dictionary</h2>
    <table>
      <thead>
        <tr>
          <th>Variable</th>
          <th>Type</th>
          <th>Scope</th>
          <th>Usage</th>
          <th>Power Automate Equivalent</th>
          <th>Used In Steps</th>
        </tr>
      </thead>
      <tbody>
        {variables_rows}
      </tbody>
    </table>

    <h2>Disabled Actions (Preserved Before Pruning)</h2>
    <table>
      <thead>
        <tr>
          <th>Original Step</th>
          <th>Task</th>
          <th>Command</th>
          <th>Action</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>
        {disabled_rows}
      </tbody>
    </table>
  </div>
</body>
</html>"""
        return html

    @staticmethod
    def generate_summary(workflow: WorkflowModel, plan: MigrationPlanModel) -> Dict[str, Any]:
        return {
            "workflow_id": workflow.workflow.id,
            "workflow_name": workflow.workflow.name,
            "architecture_type": plan.architecture.architectureType,
            "statistics": workflow.statistics.model_dump(),
            "estimated_effort_hours": plan.estimated_effort_hours,
            "risks_count": len(plan.migration_risks),
            "manual_review_count": len(plan.manual_review_items),
            "dependencies_count": len(workflow.dependencies)
        }
