
from fastapi import FastAPI

from app.config import settings
from app.routers import data, health
from app.utils.logging import configure_logging


configure_logging()

app = FastAPI(title=settings.APP_NAME)

app.include_router(health.router)
app.include_router(data.router)
