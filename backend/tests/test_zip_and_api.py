import io
import zipfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app import app
from backend.utils.security import validate_and_extract_zip, SecurityException
from backend.services.pipeline_orchestrator import PipelineOrchestrator

client = TestClient(app)

def test_zip_path_traversal_blocked(tmp_path):
    # Construct malicious zip with ../ attack
    malicious_buf = io.BytesIO()
    with zipfile.ZipFile(malicious_buf, "w") as zf:
        zf.writestr("../../evil.txt", "malicious payload")
    malicious_buf.seek(0)

    zip_file_path = tmp_path / "evil.zip"
    zip_file_path.write_bytes(malicious_buf.getvalue())

    dest_dir = tmp_path / "extracted"

    with pytest.raises(SecurityException) as exc:
        validate_and_extract_zip(zip_file_path, dest_dir)
    assert "Path traversal" in str(exc.value) or "Illegal relative" in str(exc.value)

def test_end_to_end_api_json_pipeline(tmp_path):
    test_json = {
        "name": "ProductionWorkflow",
        "variables": [
            {"name": "TransactionID", "type": "String", "input": True},
            {"name": "MasterPath", "type": "String", "defaultValue": {"string": "C:\\Data\\Master.xlsx"}}
        ],
        "nodes": [
            {
                "commandName": "Comment",
                "attributes": [{"name": "text", "value": {"string": "Start"}}]
            },
            {
                "commandName": "Excel",
                "disabled": True,
                "attributes": [{"name": "action", "value": {"string": "Open"}}]
            },
            {
                "commandName": "Excel",
                "attributes": [
                    {"name": "filePath", "value": {"string": "$MasterPath$"}},
                    {"name": "action", "value": {"string": "Open"}}
                ]
            },
            {
                "commandName": "HTTP",
                "attributes": [
                    {"name": "url", "value": {"string": "https://api.enterprise.com/orders"}},
                    {"name": "method", "value": {"string": "POST"}}
                ]
            }
        ]
    }
    json_path = tmp_path / "test_workflow.json"
    import json
    json_path.write_text(json.dumps(test_json), encoding="utf-8")

    # 1. Upload
    with open(json_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test_workflow.json", f, "application/json")}
        )
    assert response.status_code == 200
    upload_data = response.json()
    job_id = upload_data["job_id"]
    assert job_id is not None
    assert upload_data["status"] == "PENDING"

    # 2. Run analysis synchronously for test
    PipelineOrchestrator.run_analysis(job_id)

    # 3. Check status
    status_resp = client.get(f"/api/jobs/{job_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["status"] == "COMPLETED"
    assert status_data["current_stage"] == "REPORT_GENERATED"
    assert status_data["progress_percentage"] == 100

    # 4. Check workflow
    wf_resp = client.get(f"/api/jobs/{job_id}/workflows")
    assert wf_resp.status_code == 200
    wf_data = wf_resp.json()
    assert wf_data["statistics"]["totalActions"] > 0
    assert wf_data["statistics"]["totalDisabledActions"] >= 1

    # 5. Check actions
    act_resp = client.get(f"/api/jobs/{job_id}/actions")
    assert act_resp.status_code == 200
    act_data = act_resp.json()
    assert act_data["total_actions"] > 0

    # 6. Check variables
    var_resp = client.get(f"/api/jobs/{job_id}/variables")
    assert var_resp.status_code == 200
    var_data = var_resp.json()
    assert var_data["total_variables"] > 0

    # 7. Check disabled actions
    da_resp = client.get(f"/api/jobs/{job_id}/disabled-actions")
    assert da_resp.status_code == 200
    da_data = da_resp.json()
    assert len(da_data) >= 1
    assert any(da["command"] == "Excel" for da in da_data)

    # 8. Check reports
    rep_resp = client.get(f"/api/jobs/{job_id}/report")
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert "A360 to Microsoft Power Automate Migration Blueprint" in rep_data["markdown"]

    # 9. Check outputs list
    out_resp = client.get(f"/api/jobs/{job_id}/outputs")
    assert out_resp.status_code == 200
    out_files = [f["filename"] for f in out_resp.json()["files"]]
    assert "cleaned_workflow.json" in out_files
    assert "parsed_workflow.json" in out_files
    assert "action_analysis.json" in out_files
    assert "variable_analysis.json" in out_files
    assert "disabled_actions.json" in out_files
    assert "task_dependency.json" in out_files
    assert "migration_plan.json" in out_files
    assert "migration_report.md" in out_files
    assert "migration_report.html" in out_files
    assert "migration_summary.json" in out_files

    # 10. Check ZIP bundle download
    zip_resp = client.get(f"/api/jobs/{job_id}/download")
    assert zip_resp.status_code == 200
    assert zip_resp.headers["content-type"] == "application/zip"

def test_end_to_end_api_zip_package(tmp_path):
    import json
    main_bot = {
        "name": "MainWorkflow",
        "nodes": [
            {
                "commandName": "runTask",
                "attributes": [{"name": "taskbot", "value": {"string": "SubTaskBot"}}]
            },
            {
                "commandName": "HTTP",
                "attributes": [{"name": "url", "value": {"string": "https://api.test.com"}}]
            }
        ]
    }
    sub_bot = {
        "name": "SubTaskBot",
        "nodes": [
            {
                "commandName": "Excel",
                "attributes": [{"name": "action", "value": {"string": "Open"}}]
            }
        ]
    }
    manifest = {"version": "2.0.0", "name": "DynamicPackage"}

    zip_file_path = tmp_path / "DynamicPackage.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zf:
        zf.writestr("MainWorkflow.json", json.dumps(main_bot))
        zf.writestr("SubTaskBot.json", json.dumps(sub_bot))
        zf.writestr("manifest.json", json.dumps(manifest))

    with open(zip_file_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("DynamicPackage.zip", f, "application/zip")}
        )
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    # Run analysis
    PipelineOrchestrator.run_analysis(job_id)

    # Check workflow
    wf_resp = client.get(f"/api/jobs/{job_id}/workflows")
    assert wf_resp.status_code == 200
    wf_data = wf_resp.json()
    assert wf_data["statistics"]["totalTasks"] >= 2
    assert wf_data["statistics"]["totalActions"] >= 3

    # Check tasks endpoint
    tasks_resp = client.get(f"/api/jobs/{job_id}/tasks")
    assert tasks_resp.status_code == 200
    assert len(tasks_resp.json()) >= 2

    # Check search endpoint
    search_resp = client.get(f"/api/jobs/{job_id}/search?q=Excel")
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["total_matches"] > 0
