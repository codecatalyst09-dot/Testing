import os
import json
import shutil
import zipfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.models.job import JobStatus, PipelineStage, PIPELINE_STAGE_ORDER, InventoryItem
from backend.services.zip_service import ZipService
from backend.services.a360_preprocessor import A360Preprocessor, split_json_file
from backend.services.a360_parser import A360Parser
from backend.services.report_generator import ReportGenerator
from backend.migration.migration_plan import MigrationPlanBuilder
from backend.models.workflow import WorkflowModel
from backend.models.migration import MigrationPlanModel
from backend.utils.logger import logger
from backend.db.database import SessionLocal
from backend.db.models import JobRecord, AnalysisResultRecord

STORAGE_BASE = Path(__file__).parent.parent / "storage" / "jobs"

class PipelineOrchestrator:
    @staticmethod
    def get_job_dir(job_id: str) -> Path:
        job_dir = STORAGE_BASE / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    @classmethod
    def update_job_stage(
        cls,
        job_id: str,
        stage: PipelineStage,
        error_msg: Optional[str] = None
    ):
        try:
            db = SessionLocal()
            job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
            if job:
                job.current_stage = stage.value
                idx = PIPELINE_STAGE_ORDER.index(stage)
                job.progress_percentage = int(((idx + 1) / len(PIPELINE_STAGE_ORDER)) * 100)
                if stage == PipelineStage.REPORT_GENERATED:
                    job.status = JobStatus.COMPLETED.value
                if error_msg:
                    job.status = JobStatus.FAILED.value
                    job.error_message = error_msg
                db.commit()
            db.close()
        except Exception as e:
            logger.error("PIPELINE_DB_UPDATE", f"Failed to update job {job_id} in DB: {e}")

    @classmethod
    def run_analysis(cls, job_id: str):
        """
        Executes the 13-stage analysis pipeline end-to-end.
        """
        start_time = time.time()
        job_dir = cls.get_job_dir(job_id)

        # Directory structure preservation
        original_dir = job_dir / "original"
        processed_dir = job_dir / "processed"
        parsed_dir = job_dir / "parsed"
        analysis_dir = job_dir / "analysis"
        reports_dir = job_dir / "reports"
        migration_dir = job_dir / "migration"
        outputs_dir = job_dir / "outputs"
        chunks_dir = job_dir / "chunks"

        for d in (original_dir, processed_dir, parsed_dir, analysis_dir, reports_dir, migration_dir, outputs_dir, chunks_dir):
            d.mkdir(parents=True, exist_ok=True)

        logger.info("PIPELINE_START", f"Starting analysis pipeline for job {job_id}", job_id=job_id)

        try:
            # Stage 1: FILE_UPLOADED (Already achieved during upload)
            cls.update_job_stage(job_id, PipelineStage.FILE_UPLOADED)

            # Find uploaded file in original/
            orig_files = list(original_dir.glob("*"))
            if not orig_files:
                raise RuntimeError("No input file found in job's original directory.")
            uploaded_file = orig_files[0]
            file_ext = uploaded_file.suffix.lower()

            taskbot_files: List[Path] = []
            inventory: List[InventoryItem] = []

            # Stage 2: ZIP_EXTRACTED (if ZIP)
            if file_ext == ".zip":
                extracted_dir = job_dir / "extracted"
                inventory, taskbot_files = ZipService.extract_and_inventory(uploaded_file, extracted_dir)
                cls.update_job_stage(job_id, PipelineStage.ZIP_EXTRACTED)
            else:
                # Direct JSON
                inventory = [
                    InventoryItem(
                        name=uploaded_file.name,
                        path=uploaded_file.name,
                        size=uploaded_file.stat().st_size,
                        file_type="Taskbot",
                        is_main_task=True
                    )
                ]
                taskbot_files = [uploaded_file]
                cls.update_job_stage(job_id, PipelineStage.ZIP_EXTRACTED)

            # Update DB with inventory
            db = SessionLocal()
            job_rec = db.query(JobRecord).filter(JobRecord.id == job_id).first()
            if job_rec:
                job_rec.set_inventory([inv.model_dump() for inv in inventory])
                db.commit()
            db.close()

            # Stage 3: A360_FILES_DISCOVERED
            if not taskbot_files:
                raise RuntimeError("No valid A360 taskbot JSON files found in uploaded package.")
            cls.update_job_stage(job_id, PipelineStage.A360_FILES_DISCOVERED)

            # Stage 4: ORIGINAL_ACTIONS_CAPTURED & Stage 5: DISABLED_ACTIONS_DETECTED & Stage 6: JSON_CLEANED
            preprocessor = A360Preprocessor()
            all_disabled_actions: List[Dict[str, Any]] = []
            cleaned_taskbots: List[tuple] = []
            raw_data_map: Dict[str, Any] = {}

            for tb_file in taskbot_files:
                task_name = tb_file.stem
                with open(tb_file, "r", encoding="utf-8", errors="ignore") as f:
                    raw_data = json.load(f)

                raw_data_map[task_name] = raw_data

                # Preprocessing
                cleaned_data, disabled_acts = preprocessor.process(
                    raw_data=raw_data,
                    task_name=task_name,
                    file_path=tb_file.name
                )
                all_disabled_actions.extend(disabled_acts)
                cleaned_taskbots.append((task_name, tb_file.name, cleaned_data))

                # Save individual cleaned JSON
                cleaned_out = processed_dir / f"{task_name}_cleaned.json"
                with open(cleaned_out, "w", encoding="utf-8") as f:
                    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

            cls.update_job_stage(job_id, PipelineStage.ORIGINAL_ACTIONS_CAPTURED)
            cls.update_job_stage(job_id, PipelineStage.DISABLED_ACTIONS_DETECTED)
            cls.update_job_stage(job_id, PipelineStage.JSON_CLEANED)

            # Stage 7: WORKFLOW_PARSED
            parser = A360Parser()
            workflow_name = uploaded_file.stem.replace("_", " ").title()
            workflow_model = parser.parse(
                cleaned_taskbots_data=cleaned_taskbots,
                raw_data_map=raw_data_map,
                disabled_actions=all_disabled_actions,
                workflow_id=f"wf-{job_id[:8]}",
                workflow_name=workflow_name
            )
            cls.update_job_stage(job_id, PipelineStage.WORKFLOW_PARSED)

            # Stage 8: VARIABLES_EXTRACTED
            cls.update_job_stage(job_id, PipelineStage.VARIABLES_EXTRACTED)

            # Stage 9: SUBTASKS_IDENTIFIED
            cls.update_job_stage(job_id, PipelineStage.SUBTASKS_IDENTIFIED)

            # Stage 10: ACTIONS_ANALYZED
            cls.update_job_stage(job_id, PipelineStage.ACTIONS_ANALYZED)

            # Stage 11: CLASSIFICATION_COMPLETE
            cls.update_job_stage(job_id, PipelineStage.CLASSIFICATION_COMPLETE)

            # Stage 12: MAPPING_COMPLETE
            migration_plan = MigrationPlanBuilder.build_plan(
                job_id=job_id,
                workflow_name=workflow_name,
                actions=workflow_model.actions,
                variables=workflow_model.variables,
                dependencies=workflow_model.dependencies
            )
            cls.update_job_stage(job_id, PipelineStage.MAPPING_COMPLETE)

            # Stage 13: REPORT_GENERATED
            md_report = ReportGenerator.generate_markdown(workflow_model, migration_plan)
            html_report = ReportGenerator.generate_html(workflow_model, migration_plan, md_report)
            summary_json = ReportGenerator.generate_summary(workflow_model, migration_plan)

            # Save parsed and analysis files into appropriate folders
            with open(parsed_dir / "parsed_workflow.json", "w", encoding="utf-8") as f:
                json.dump(workflow_model.model_dump(), f, indent=2, ensure_ascii=False)

            with open(analysis_dir / "action_analysis.json", "w", encoding="utf-8") as f:
                json.dump([a.model_dump() for a in workflow_model.actions], f, indent=2, ensure_ascii=False)

            with open(analysis_dir / "variable_analysis.json", "w", encoding="utf-8") as f:
                json.dump([v.model_dump() for v in workflow_model.variables], f, indent=2, ensure_ascii=False)

            with open(analysis_dir / "disabled_actions.json", "w", encoding="utf-8") as f:
                json.dump([da.model_dump() for da in workflow_model.disabledActions], f, indent=2, ensure_ascii=False)

            with open(analysis_dir / "task_dependency.json", "w", encoding="utf-8") as f:
                json.dump({
                    "tasks": [t.model_dump() for t in workflow_model.tasks],
                    "dependencies": [d.model_dump() for d in workflow_model.dependencies]
                }, f, indent=2, ensure_ascii=False)

            with open(migration_dir / "migration_plan.json", "w", encoding="utf-8") as f:
                json.dump(migration_plan.model_dump(), f, indent=2, ensure_ascii=False)

            with open(reports_dir / "migration_report.md", "w", encoding="utf-8") as f:
                f.write(md_report)

            with open(reports_dir / "migration_report.html", "w", encoding="utf-8") as f:
                f.write(html_report)

            with open(reports_dir / "migration_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary_json, f, indent=2, ensure_ascii=False)

            # Save unified cleaned_workflow.json
            unified_cleaned = [ct[2] for ct in cleaned_taskbots] if len(cleaned_taskbots) > 1 else (cleaned_taskbots[0][2] if cleaned_taskbots else {})
            with open(processed_dir / "cleaned_workflow.json", "w", encoding="utf-8") as f:
                json.dump(unified_cleaned, f, indent=2, ensure_ascii=False)

            # Also generate chunks for downstream analysis
            split_json_file(processed_dir / "cleaned_workflow.json", output_dir=chunks_dir, chunk_size=25000)

            # Populate outputs/ directory with the 10 required artifacts
            # 1. cleaned_workflow.json
            shutil.copy(processed_dir / "cleaned_workflow.json", outputs_dir / "cleaned_workflow.json")
            # 2. parsed_workflow.json
            shutil.copy(parsed_dir / "parsed_workflow.json", outputs_dir / "parsed_workflow.json")
            # 3. action_analysis.json
            shutil.copy(analysis_dir / "action_analysis.json", outputs_dir / "action_analysis.json")
            # 4. variable_analysis.json
            shutil.copy(analysis_dir / "variable_analysis.json", outputs_dir / "variable_analysis.json")
            # 5. disabled_actions.json
            shutil.copy(analysis_dir / "disabled_actions.json", outputs_dir / "disabled_actions.json")
            # 6. task_dependency.json
            shutil.copy(analysis_dir / "task_dependency.json", outputs_dir / "task_dependency.json")
            # 7. migration_plan.json
            shutil.copy(migration_dir / "migration_plan.json", outputs_dir / "migration_plan.json")
            # 8. migration_report.md
            shutil.copy(reports_dir / "migration_report.md", outputs_dir / "migration_report.md")
            # 9. migration_report.html
            shutil.copy(reports_dir / "migration_report.html", outputs_dir / "migration_report.html")
            # 10. migration_summary.json
            shutil.copy(reports_dir / "migration_summary.json", outputs_dir / "migration_summary.json")

            # Package all 10 outputs into A360_Migration_Analysis_<timestamp>.zip
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            zip_filename = f"A360_Migration_Analysis_{timestamp}.zip"
            zip_path = job_dir / zip_filename
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in outputs_dir.iterdir():
                    if item.is_file():
                        zf.write(item, arcname=item.name)

            # Record analysis results in DB
            db = SessionLocal()
            res_rec = db.query(AnalysisResultRecord).filter(AnalysisResultRecord.job_id == job_id).first()
            if not res_rec:
                res_rec = AnalysisResultRecord(job_id=job_id)
                db.add(res_rec)
            res_rec.workflow_name = workflow_name
            res_rec.total_workflows = workflow_model.statistics.totalWorkflows
            res_rec.total_tasks = workflow_model.statistics.totalTasks
            res_rec.total_actions = workflow_model.statistics.totalActions
            res_rec.cloud_actions = workflow_model.statistics.cloudActions
            res_rec.desktop_actions = workflow_model.statistics.desktopActions
            res_rec.hybrid_actions = workflow_model.statistics.hybridActions
            res_rec.manual_review_actions = workflow_model.statistics.manualReviewActions
            res_rec.total_variables = workflow_model.statistics.totalVariables
            res_rec.total_subtasks = workflow_model.statistics.totalSubtasks
            res_rec.total_disabled_actions = workflow_model.statistics.totalDisabledActions
            res_rec.summary_json = json.dumps(summary_json)
            db.commit()
            db.close()

            cls.update_job_stage(job_id, PipelineStage.REPORT_GENERATED)

            duration = time.time() - start_time
            logger.info("PIPELINE_COMPLETE", f"Analysis completed successfully in {duration:.2f}s", job_id=job_id, duration=duration)

        except Exception as e:
            err_str = str(e)
            logger.error("PIPELINE_ERROR", f"Analysis failed: {err_str}", job_id=job_id, error=err_str)
            cls.update_job_stage(job_id, PipelineStage.FILE_UPLOADED, error_msg=err_str)
            raise
