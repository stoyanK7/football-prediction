"""Contains the main FastAPI application."""
from fastapi import FastAPI

from src.api.tasks import router as tasks_router
from src.api.logfiles import router as logfiles_router

app = FastAPI()

app.include_router(tasks_router)
app.include_router(logfiles_router)
