import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

def print_banner(text: str):
    print("\n" + "=" * 65)
    print(f"  {text}")
    print("=" * 65 + "\n")

def run_step(cmd, cwd=None, step_name=""):
    print(f"--> [Running] {step_name}...")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        print(f"\n[ERROR] Step '{step_name}' failed with exit code {result.returncode}.")
        sys.exit(result.returncode)
    print(f"--> [Done] {step_name}\n")

def main():
    root_dir = Path(__file__).resolve().parent
    frontend_dir = root_dir / "frontend"
    frontend_dist = frontend_dir / "dist"
    spec_file = root_dir / "A360_Migration_Analyzer.spec"
    dist_dir = root_dir / "dist"
    # Use system temp directory for PyInstaller workpath to prevent OneDrive locking issues
    work_dir = Path(tempfile.gettempdir()) / "a360_migration_build"

    print_banner("Building A360 to Power Automate Standalone Windows EXE")

    # Step 1: Ensure PyInstaller is installed
    try:
        import PyInstaller
        print("--> PyInstaller is installed.")
    except ImportError:
        run_step(f'"{sys.executable}" -m pip install pyinstaller', cwd=root_dir, step_name="Installing PyInstaller")

    # Step 2: Build the React frontend if dist is missing or rebuild requested
    if not (frontend_dist / "index.html").exists():
        print("--> Frontend dist not found. Building React Vite frontend...")
        run_step("npm run build", cwd=frontend_dir, step_name="Building Frontend (Vite)")
    else:
        print("--> Using existing compiled frontend at frontend/dist (run 'npm run build' inside frontend to update).")

    # Step 3: Run PyInstaller with customized spec file and safe temp workpath
    work_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)
    cmd = f'"{sys.executable}" -m PyInstaller --noconfirm --workpath "{work_dir}" --distpath "{dist_dir}" "{spec_file}"'
    run_step(cmd, cwd=root_dir, step_name="Packaging Executable with PyInstaller")

    output_exe = dist_dir / "A360_to_PowerAutomate_Migration_Analyzer.exe"
    if output_exe.exists():
        size_mb = output_exe.stat().st_size / (1024 * 1024)
        print_banner(f"BUILD SUCCESSFUL!\n  Output: {output_exe}\n  File Size: {size_mb:.1f} MB")
        print("How to run:")
        print(f"  1. Double click '{output_exe.name}' in the dist/ folder.")
        print("  2. The server starts and automatically opens http://localhost:8000 in your browser.")
        print("  3. Your data will be saved in a 'storage/' folder created next to the exe.")
    else:
        print("\n[Warning] Build completed, but executable was not found at expected location.")

if __name__ == "__main__":
    main()
