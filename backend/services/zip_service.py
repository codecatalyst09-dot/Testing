import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from backend.utils.security import validate_and_extract_zip, SecurityException
from backend.models.job import InventoryItem
from backend.utils.logger import logger

class ZipService:
    @staticmethod
    def extract_and_inventory(
        zip_path: Path,
        extract_dir: Path
    ) -> Tuple[List[InventoryItem], List[Path]]:
        """
        Safely extract ZIP and build an inventory of A360 files.
        """
        logger.info("ZIP_EXTRACTION", f"Extracting archive {zip_path.name} to {extract_dir}")
        extracted_paths, _ = validate_and_extract_zip(zip_path, extract_dir)

        inventory: List[InventoryItem] = []
        taskbot_files: List[Path] = []

        # Recursively scan extracted contents
        for file_path in extracted_paths:
            if not file_path.is_file():
                continue

            rel_path = file_path.relative_to(extract_dir).as_posix()
            file_size = file_path.stat().st_size
            file_name = file_path.name
            ext = file_path.suffix.lower()

            item_type = "Other"
            is_main = False

            if ext == ".json":
                # Determine if it's a taskbot or manifest
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        if "nodes" in data or "commandName" in data or "commands" in data or "variables" in data:
                            item_type = "Taskbot"
                            taskbot_files.append(file_path)
                            # Check if likely main task
                            lower_name = file_name.lower()
                            if "main" in lower_name or "master" in lower_name or len(taskbot_files) == 1:
                                is_main = True
                        elif "version" in data and ("packages" in data or "dependencies" in data):
                            item_type = "Manifest"
                        else:
                            item_type = "Config"
                except Exception:
                    item_type = "Data"
            elif ext in {".png", ".jpg", ".jpeg", ".ico", ".svg"}:
                item_type = "Asset"
            elif ext in {".csv", ".xlsx", ".txt", ".xml"}:
                item_type = "Data"

            inventory.append(InventoryItem(
                name=file_name,
                path=rel_path,
                size=file_size,
                file_type=item_type,
                is_main_task=is_main
            ))

        # If multiple taskbots and none marked main, designate the first or largest as main
        taskbots = [item for item in inventory if item.file_type == "Taskbot"]
        if taskbots and not any(t.is_main_task for t in taskbots):
            # Pick the largest taskbot as main
            largest = max(taskbots, key=lambda x: x.size)
            largest.is_main_task = True

        return inventory, taskbot_files
