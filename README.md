# A360 → Microsoft Power Automate Migration Analyzer

A production-ready, full-stack enterprise web application that analyzes Automation Anywhere A360 automation packages (`.zip` or `.json`) and generates actionable migration blueprints for **Microsoft Power Automate Cloud Flows** and **Power Automate Desktop (PAD)**.

---

## System Architecture

```
                                  [ Upload: .zip / .json ]
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │    A360 Safe Zip & File      │
                             │       Security Gate          │
                             └──────────────┬───────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │   Pre-Pruning Extraction     │
                             │ (Preserves Disabled Actions) │
                             └──────────────┬───────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │   Authoritative A360 JSON    │
                             │         Preprocessor         │
                             └──────────────┬───────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │     Hierarchical Parser      │
                             │ (Tasks, Actions, Variables)  │
                             └──────────────┬───────────────┘
                                             │
                                             ▼
        ┌────────────────────────────────────┼───────────────────────────────────┐
        │                                    │                                   │
        ▼                                    ▼                                   ▼
┌──────────────────┐               ┌──────────────────┐               ┌──────────────────┐
│ Cloud Rule Engine│               │Desktop Rule Engine│               │Hybrid Rule Engine│
│   (HTTP, Email,  │               │ (Excel, Browser, │               │ (Cloud Trigger   │
│ SharePoint, O365)│               │  SAP GUI, Files) │               │ calling PAD bot) │
└────────┬─────────┘               └────────┬─────────┘               └────────┬─────────┘
        │                                    │                                   │
        └────────────────────────────────────┼───────────────────────────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │  Action & Variable Mapping   │
                             │    (Unknown Command Policy)  │
                             └──────────────┬───────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │  Target Architecture Engine  │
                             │  - Cloud Flow Blueprint      │
                             │  - Desktop Flow Blueprint    │
                             │  - Migration Roadmap & Risks │
                             └──────────────┬───────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │    10 Output Artifacts &     │
                             │  Downloadable ZIP Package    │
                             └──────────────────────────────┘
```

---

## Key Features

1. **Upload & Multi-Taskbot Discovery**: Accepts `.zip` packages or `.json` taskbots. Safely extracts files with path traversal and zip bomb protection, and automatically discovers main tasks, child subtasks, and manifests.
2. **Authoritative Preprocessing**:
   - Implements the exact pruning algorithm specified.
   - **Zero Data Loss**: Automatically captures and records all disabled actions prior to removal into `disabled_actions.json`.
   - Strips `Comment`, `messageBox`, `logToFile`, and unwraps single-key parameter objects.
3. **Deterministic Parser**:
   - Recursively inspects unknown structures, nested blocks (`children`, `branches`, `then`, `else`, `loop`).
   - Extracts all variables, scopes, read/write usages, and maps them to Power Automate types.
   - Builds task dependency hierarchy trees from `runTask` actions.
4. **Cloud vs Desktop Classification**:
   - **Power Automate Cloud**: APIs, Office 365, SharePoint, Teams, approvals, serverless actions.
   - **Power Automate Desktop**: Local Excel, Web Browser Automation, SAP GUI, Windows UI, Local Files, Scripts.
   - **Hybrid**: Cloud Flows that orchestrate Desktop Flows via on-premises machine connections.
   - **Manual Review**: Any unknown or proprietary command is never silently ignored; it is flagged with migration instructions.
5. **Interactive Flow Visualization**: Built with `@xyflow/react` (React Flow), featuring custom color-coded nodes for each platform, interactive minimap, controls, and click-to-inspect detail drawer.
6. **Executive & Technical Reports**: Generates standalone styled HTML reports, Markdown blueprints, and 10 structured JSON datasets.

---

## Project Structure

```
.
├── backend/
│   ├── app.py                      # FastAPI entrypoint and router registration
│   ├── api/                        # REST API endpoints
│   │   ├── upload.py               # POST /api/upload
│   │   ├── analysis.py             # POST /api/analyze, GET /api/jobs/{id}/status
│   │   ├── workflows.py            # GET /api/jobs/{id}/workflows
│   │   ├── actions.py              # GET /api/jobs/{id}/actions (search & filters)
│   │   ├── variables.py            # GET /api/jobs/{id}/variables
│   │   ├── disabled_actions.py     # GET /api/jobs/{id}/disabled-actions
│   │   ├── tasks.py                # GET /api/jobs/{id}/tasks
│   │   ├── migration.py            # GET /api/jobs/{id}/migration
│   │   ├── reports.py              # GET /api/jobs/{id}/report, download ZIP/files
│   │   └── search.py               # GET /api/jobs/{id}/search (global search)
│   ├── services/                   # Business logic and processing
│   │   ├── zip_service.py          # Safe extraction, traversal check, inventory
│   │   ├── a360_preprocessor.py    # Authoritative cleaning & disabled action capture
│   │   ├── a360_parser.py          # Recursive structure parser
│   │   ├── variable_analyzer.py    # Variable scanner & type mapper
│   │   ├── task_analyzer.py        # Task tree & subtask relationship builder
│   │   ├── dependency_analyzer.py  # System dependencies (SAP, Excel, APIs, DB)
│   │   ├── report_generator.py     # Markdown, HTML, and JSON report generator
│   │   └── pipeline_orchestrator.py# 13-stage pipeline & ZIP packager
│   ├── migration/                  # Deterministic rule engine
│   │   ├── classifier.py           # Cloud vs Desktop vs Hybrid classifier
│   │   ├── cloud_rules.py          # Cloud rule set
│   │   ├── desktop_rules.py        # Desktop rule set
│   │   ├── hybrid_rules.py         # Hybrid bridging rules
│   │   ├── mapping_engine.py       # A360 to Power Automate action mapping
│   │   └── migration_plan.py       # Target Cloud and Desktop Flow blueprints
│   ├── models/                     # Pydantic schemas (V2)
│   ├── db/                         # SQLite database with SQLAlchemy ORM
│   ├── ai/                         # Deterministic process explainer architecture
│   ├── utils/                      # Security (safe extraction) and structured logger
│   └── tests/                      # Automated pytest test suite
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable UI components
│   │   │   ├── Navbar.tsx          # Top bar with active job and search
│   │   │   ├── Sidebar.tsx         # Left navigation
│   │   │   ├── UploadZone.tsx      # Drag & drop upload with validation
│   │   │   ├── PipelineProgress.tsx# 13-stage animated live progress stepper
│   │   │   ├── WorkflowGraph.tsx   # React Flow interactive diagram
│   │   │   ├── ActionDetailPanel.tsx# Slide-over detail drawer
│   │   │   ├── ActionTable.tsx     # Searchable Action Explorer
│   │   │   ├── VariableTable.tsx   # Variables Explorer
│   │   │   ├── DisabledActionsTable.tsx # Disabled actions audit view
│   │   │   ├── DependencyTree.tsx  # Task tree and system dependencies
│   │   │   ├── TargetArchitectureView.tsx # Cloud/Desktop blueprints & roadmap
│   │   │   ├── ReportViewer.tsx    # HTML & Markdown report preview
│   │   │   └── GlobalSearchModal.tsx # Ctrl+K global search
│   │   ├── pages/                  # Page views
│   │   ├── context/JobContext.tsx  # React state & active job context
│   │   ├── services/api.ts         # Typed API client
│   │   └── types/                  # TypeScript definitions
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js v18+ & npm (tested on Node v22)

---

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run FastAPI backend
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at:
- **API Base**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/health`

---

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install npm dependencies
npm install

# 3. Run Vite dev server
npm run dev
```

The web application will open at:
- **Frontend URL**: `http://127.0.0.1:5173`

---

## Running the Automated Test Suite

Run the full pytest suite:

```bash
python -m pytest backend/tests/ -v
```

All 16 test cases run against dynamic in-memory fixtures (no static sample dependencies required), testing:
- Preprocessor comment, messageBox, and logging removal
- Disabled action detection prior to pruning
- Wrapper unwrapping and attribute flattening
- Nested actions, loops, and conditions parsing
- Subtask parent/child relationships
- Cloud, Desktop, Hybrid, and Unknown Command classification
- Safe zip extraction and path traversal prevention
- End-to-end API upload, analyze, status, report, and download endpoints

---

## 10 Generated Output Artifacts

When an analysis is completed, the system generates 10 output files and bundles them into `A360_Migration_Analysis_<timestamp>.zip`:

| # | Artifact | Description |
|---|---|---|
| 1 | `cleaned_workflow.json` | Preprocessed, pruned, and flattened A360 JSON |
| 2 | `parsed_workflow.json` | Normalized hierarchical workflow model |
| 3 | `action_analysis.json` | Action-by-action mapping, platform, complexity, and confidence |
| 4 | `variable_analysis.json` | Extracted variables, scopes, types, and step usages |
| 5 | `disabled_actions.json` | Disabled actions recorded prior to cleaning |
| 6 | `task_dependency.json` | Taskbot hierarchy tree and external system dependencies |
| 7 | `migration_plan.json` | Complete migration blueprint and target flow schemas |
| 8 | `migration_report.md` | Comprehensive Markdown report |
| 9 | `migration_report.html` | Self-contained, styled executive HTML report (printable to PDF) |
| 10| `migration_summary.json`| High-level executive statistics and effort estimates |
