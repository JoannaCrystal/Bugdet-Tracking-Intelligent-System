"""
Main FastAPI application for the Finance Agentic System.

Serves transaction API endpoints and initializes database on startup.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure src is on PYTHONPATH when running as module
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Load .env before any config/database imports
from dotenv import load_dotenv
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.insights import router as insights_router
from api.plaid import router as plaid_router
from api.qa import router as qa_router
from api.transactions import router as transactions_router
from config.validate_env import validate_environment
from database.db import init_db
from utils.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB on startup."""
    validate_environment()
    init_db()
    yield
    # Cleanup if needed


app = FastAPI(
    title="Finance Agentic System",
    description="Personal Finance & Budgeting Agentic System with transaction ingestion and processing.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions_router)
app.include_router(plaid_router)
app.include_router(insights_router)
app.include_router(qa_router)


@app.get("/")
def root():
    """Root route: redirect to API docs for Hugging Face and better UX."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
