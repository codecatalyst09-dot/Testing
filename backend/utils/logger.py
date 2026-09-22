import os
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

class StructuredLogger:
    def __init__(self, name: str = "A360MigrationAnalyzer"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(
        self,
        level: str,
        stage: str,
        message: str,
        job_id: Optional[str] = None,
        workflow: Optional[str] = None,
        file: Optional[str] = None,
        duration: Optional[float] = None,
        error: Optional[str] = None,
        **kwargs: Any
    ):
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "stage": stage,
            "message": message,
        }
        if job_id:
            payload["job_id"] = job_id
        if workflow:
            payload["workflow"] = workflow
        if file:
            payload["file"] = file
        if duration is not None:
            payload["duration_sec"] = round(duration, 4)
        if error:
            payload["error"] = error
        if kwargs:
            payload["extra"] = kwargs

        log_fn = getattr(self.logger, level.lower(), self.logger.info)
        log_fn(json.dumps(payload))

    def info(self, stage: str, message: str, **kwargs):
        self.log("info", stage, message, **kwargs)

    def warning(self, stage: str, message: str, **kwargs):
        self.log("warning", stage, message, **kwargs)

    def error(self, stage: str, message: str, **kwargs):
        self.log("error", stage, message, **kwargs)

logger = StructuredLogger()
