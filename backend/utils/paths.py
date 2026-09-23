import sys
import os
from pathlib import Path

def get_base_dir() -> Path:
    """
    Returns the base directory for read-only bundled assets.
    In PyInstaller frozen mode, sys._MEIPASS contains unpacked files.
    In normal dev mode, returns the project root.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    # File is at backend/utils/paths.py -> parent.parent.parent is project root
    return Path(__file__).resolve().parent.parent.parent

def get_storage_dir() -> Path:
    """
    Returns the persistent storage directory for SQLite database and uploaded bot jobs.
    When packaged as an .exe, storage is placed in a 'storage' folder beside the executable
    so data persists across runs, rather than inside the ephemeral temp directory.
    """
    if getattr(sys, "frozen", False):
        storage_path = Path(sys.executable).resolve().parent / "storage"
    else:
        storage_path = Path(__file__).resolve().parent.parent / "storage"
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path

def get_frontend_dist_dir() -> Path:
    """
    Returns the path to the compiled frontend static assets.
    """
    return get_base_dir() / "frontend" / "dist"

def get_mapping_file_path() -> Path:
    """
    Returns the path to the AA to Power Automate Excel mapping file.
    Checks bundled location first, then folder beside executable.
    """
    bundled = get_base_dir() / "Mapping" / "AA_to_PowerAutomate_Action_Mapping.xlsx"
    if bundled.exists():
        return bundled
    if getattr(sys, "frozen", False):
        beside_exe = Path(sys.executable).resolve().parent / "Mapping" / "AA_to_PowerAutomate_Action_Mapping.xlsx"
        if beside_exe.exists():
            return beside_exe
    return bundled
