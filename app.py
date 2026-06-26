"""
aegis-ai / app.py
==================
FastAPI Web Server for AegisAI.
"""

import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from main import run_aegis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aegis.app")

app = FastAPI(title="AegisAI")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serves the main UI page."""
    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/run")
async def run_incident(request: Request):
    """Receives error log and repo URL, runs AegisAI, returns results."""
    try:
        body = await request.json()
        repo_url  = body.get("repo_url",  "https://github.com/demo-org/my-app")
        error_log = body.get("error_log", "")

        if not error_log.strip():
            return JSONResponse({"error": "error_log is required"}, status_code=400)

        logger.info("Web request received. Running AegisAI...")
        result = run_aegis(repo_url=repo_url, error_log=error_log)

        return JSONResponse({
            "status":        result["status"],
            "retry_count":   result["retry_count"],
            "current_patch": result["current_patch"],
            "test_results":  result["test_results"],
            "patch_history": result["patch_history"],
        })

    except Exception as e:
        logger.error("Web handler error: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)