import os
import sys
import time
import socket
import threading
import webbrowser
from pathlib import Path

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def find_available_port(start_port: int = 8000, max_tries: int = 20) -> int:
    for p in range(start_port, start_port + max_tries):
        if not is_port_in_use(p):
            return p
    return start_port

def launch_browser(url: str, delay_seconds: float = 1.2):
    time.sleep(delay_seconds)
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[Warning] Could not open browser automatically: {e}")
        print(f"Please open your browser manually at: {url}")

def main():
    import uvicorn
    from backend.app import app

    host = os.getenv("HOST", "127.0.0.1")
    requested_port = int(os.getenv("PORT", 8000))
    port = find_available_port(requested_port)
    url = f"http://localhost:{port}"

    print("=" * 68)
    print("  A360 to Microsoft Power Automate Migration Analyzer")
    print("=" * 68)
    print(f"  Status:  Running (100% Offline / Deterministic)")
    print(f"  URL:     {url}")
    print(f"  Storage: Persistent (in storage/ folder)")
    print("=" * 68)
    print("  Opening web dashboard in your browser...")
    print("  Press Ctrl+C or close this window to stop the server.")
    print("=" * 68)

    # Spawn thread to open default web browser
    threading.Thread(target=launch_browser, args=(url,), daemon=True).start()

    # Start FastAPI / Uvicorn server
    uvicorn.run(app, host=host, port=port, log_level="warning")

if __name__ == "__main__":
    main()
