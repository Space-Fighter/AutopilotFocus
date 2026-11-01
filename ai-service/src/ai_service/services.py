"""Everything the pipeline needs, built once at startup and passed around as one object."""

from dataclasses import dataclass

from sqlalchemy import Engine

from .config import Settings, get_settings, load_providers
from .db import make_engine
from .embedder import Embedder
from .llm import ProviderChain
from .matcher import GoalVectors
from .summary_index import SummaryIndex


@dataclass
class Services:
    settings: Settings
    llm: ProviderChain
    embedder: Embedder
    engine: Engine
    index: SummaryIndex
    goal_vectors: GoalVectors


def build_services(settings: Settings | None = None) -> Services:
    settings = settings or get_settings()
    embedder = Embedder(settings.embedding_model)
    engine = make_engine(settings)
    index = SummaryIndex()
    index.load_from_db(engine)  # FAISS lives in memory: rebuild it from Postgres on every start
    return Services(
        settings=settings,
        llm=ProviderChain(load_providers(settings.providers_file), settings.llm_timeout_s),
        embedder=embedder,
        engine=engine,
        index=index,
        goal_vectors=GoalVectors(embedder),
    )
