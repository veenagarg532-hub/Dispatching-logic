"""
FastAPI application entry point.

Run locally from the backend directory:
    uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="Factory Dynamics Simulation API",
    description=(
        "Discrete-event simulation engine for factory dynamics education. "
        "Phase 1: Load Balancing at a Toolset with Cross-Qualification."
    ),
    version="1.0.0",
)

# Allow the React dev server and any deployed frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}
