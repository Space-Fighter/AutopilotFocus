"""HTTP wrapper the Go API calls. Internal only: never exposed to the internet.

Run: uv run uvicorn ai_service.api:app --port 8001
Needs Postgres running with the migrations applied (repo-root db/README.md).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from .pipeline import classify
from .schemas import Goal, PageData, Verdict
from .services import build_services


class ClassifyRequest(BaseModel):
    page: PageData
    goal: Goal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build everything once at startup (embedding model, LLM clients, DB pool, FAISS index).
    app.state.services = build_services()
    yield
    app.state.services.engine.dispose()  # close the DB connections on shutdown


app = FastAPI(title="AutopilotFocus AI service", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "cached_pages": len(app.state.services.index)}


@app.post("/v1/classify")
def classify_endpoint(req: ClassifyRequest) -> Verdict:
    return classify(req.page, req.goal, app.state.services)
