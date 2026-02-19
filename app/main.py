from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import analyze, data, health, llm, upload
from app.utils.logging import configure_logging


configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="Unified interface for LLMs to query CRM, support tickets, and analytics via function calling.",
)

app.include_router(health.router)
app.include_router(data.router)
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(llm.router)

# Static files (frontend)
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(static_dir / "index.html")
