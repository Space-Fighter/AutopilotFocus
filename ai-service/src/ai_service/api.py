"""HTTP wrapper the Go API calls (Step 1). Internal only: never exposed to the internet.

Run: uv run uvicorn ai_service.api:app --port 8001
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from .config import get_settings, load_providers
from .embedder import Embedder
from .llm import ProviderChain
from .pipeline import classify
from .schemas import Goal, PageData, Verdict


class ClassifyRequest(BaseModel):
    page: PageData
    goal: Goal
    use_llm: bool = True  # False = basic mode (Go sends it when the free daily cap is used up)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the embedding model and LLM clients once at startup, not per request.
    settings = get_settings()
    app.state.settings = settings
    app.state.embedder = Embedder(settings.embedding_model)
    app.state.llm = ProviderChain(load_providers(settings.providers_file), settings.llm_timeout_s)
    yield


app = FastAPI(title="AutopilotFocus AI service", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/v1/classify")
def classify_endpoint(req: ClassifyRequest) -> Verdict:
    s = app.state
    return classify(req.page, req.goal, s.llm, s.embedder, s.settings, use_llm=req.use_llm)
