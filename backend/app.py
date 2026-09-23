import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import init_db
from backend.api import (
    upload,
    analysis,
    workflows,
    actions,
    variables,
    disabled_actions,
    tasks,
    migration,
    reports,
    search,
    codegen
)
from backend.utils.logger import logger

app = FastAPI(
    title="A360 → Microsoft Power Automate Migration Analyzer",
    description="Production-ready RPA analyzer converting Automation Anywhere A360 bots into Power Automate Cloud and Desktop architectures.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(workflows.router)
app.include_router(actions.router)
app.include_router(variables.router)
app.include_router(disabled_actions.router)
app.include_router(tasks.router)
app.include_router(migration.router)
app.include_router(reports.router)
app.include_router(search.router)
app.include_router(codegen.router)

@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("APP_STARTUP", "A360 to Power Automate Migration Analyzer started successfully.")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "A360 Migration Analyzer",
        "version": "1.0.0"
    }

# Serve static frontend if built
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.utils.paths import get_frontend_dist_dir

frontend_dist = get_frontend_dist_dir()
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            return None
        target_file = frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
