import os
import re
import zipfile
from pathlib import Path
from typing import List, Tuple

# Security limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB max upload
MAX_UNCOMPRESSED_SIZE = 300 * 1024 * 1024  # 300 MB max uncompressed
MAX_ZIP_RATIO = 100  # Max compression ratio to prevent zip bombs
MAX_FILE_COUNT = 1000  # Max files allowed in a zip
ALLOWED_EXTENSIONS = {".zip", ".json"}

class SecurityException(Exception):
    pass

def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename to prevent directory traversal and illegal characters."""
    base = os.path.basename(filename)
    # Remove unwanted characters
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    return clean or "upload"

def validate_file_extension(filename: str) -> str:
    """Ensure file extension is allowed."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise SecurityException(f"Unsupported file extension: {ext}. Only .zip and .json are accepted.")
    return ext

def validate_and_extract_zip(zip_path: Path, target_dir: Path) -> Tuple[List[Path], int]:
    """
    Safely extract a ZIP archive while preventing:
    - Path traversal attacks (e.g. ../../../etc/passwd or absolute paths)
    - Zip bombs (excessive file count or compression ratios)
    - Files outside the target directory
    """
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    extracted_files: List[Path] = []
    total_uncompressed_size = 0
    total_files = 0

    if not zipfile.is_zipfile(zip_path):
        raise SecurityException("The provided file is not a valid or readable ZIP archive.")

    with zipfile.ZipFile(zip_path, 'r') as zf:
        infolist = zf.infolist()
        if len(infolist) > MAX_FILE_COUNT:
            raise SecurityException(f"ZIP contains {len(infolist)} files, exceeding the limit of {MAX_FILE_COUNT}.")

        for info in infolist:
            total_files += 1
            total_uncompressed_size += info.file_size

            # Check uncompressed size
            if total_uncompressed_size > MAX_UNCOMPRESSED_SIZE:
                raise SecurityException(
                    f"ZIP uncompressed size exceeds security threshold of {MAX_UNCOMPRESSED_SIZE // (1024*1024)} MB."
                )

            # Check zip bomb compression ratio
            if info.compress_size > 0:
                ratio = info.file_size / info.compress_size
                if ratio > MAX_ZIP_RATIO and info.file_size > 5 * 1024 * 1024:
                    raise SecurityException(f"Suspicious compression ratio ({ratio:.1f}) detected for {info.filename}.")

            # Check for path traversal attacks
            # Normalize and inspect target path
            extracted_path = (target_dir / info.filename).resolve()
            try:
                # Ensure extracted_path is within target_dir
                extracted_path.relative_to(target_dir)
            except ValueError:
                raise SecurityException(f"Path traversal detected in archive item: {info.filename}")

            if ".." in info.filename or info.filename.startswith("/") or info.filename.startswith("\\"):
                raise SecurityException(f"Illegal relative or absolute path in archive: {info.filename}")

        # Extract safely
        for info in infolist:
            target_path = (target_dir / info.filename).resolve()
            if info.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as source, open(target_path, "wb") as dest:
                    dest.write(source.read())
                extracted_files.append(target_path)

    return extracted_files, total_uncompressed_size
