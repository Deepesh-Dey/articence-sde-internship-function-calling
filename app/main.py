from fastapi import FastAPI

from app.config import settings
from app.routers import data, health, llm
from app.utils.logging import configure_logging


configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="Unified interface for LLMs to query CRM, support tickets, and analytics via function calling.",
)

app.include_router(health.router)
app.include_router(data.router)
app.include_router(llm.router)
