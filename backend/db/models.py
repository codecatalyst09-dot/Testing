import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Float
from backend.db.database import Base

class JobRecord(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(16), nullable=False)  # "zip" or "json"
    file_size = Column(Integer, default=0)
    status = Column(String(32), default="PENDING", index=True)
    current_stage = Column(String(64), default="FILE_UPLOADED")
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    inventory_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_inventory(self, inventory_list):
        self.inventory_json = json.dumps(inventory_list)

    def get_inventory(self):
        try:
            return json.loads(self.inventory_json)
        except Exception:
            return []

class AnalysisResultRecord(Base):
    __tablename__ = "analysis_results"

    job_id = Column(String(64), primary_key=True, index=True)
    workflow_name = Column(String(255), default="A360 Workflow")
    total_workflows = Column(Integer, default=1)
    total_tasks = Column(Integer, default=0)
    total_actions = Column(Integer, default=0)
    cloud_actions = Column(Integer, default=0)
    desktop_actions = Column(Integer, default=0)
    hybrid_actions = Column(Integer, default=0)
    manual_review_actions = Column(Integer, default=0)
    total_variables = Column(Integer, default=0)
    total_subtasks = Column(Integer, default=0)
    total_disabled_actions = Column(Integer, default=0)
    summary_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
