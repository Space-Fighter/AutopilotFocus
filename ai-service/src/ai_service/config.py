"""Settings (from env / .env) and the LLM provider list (from providers.toml)."""

import tomllib
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=SERVICE_ROOT / ".env", extra="ignore")

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    # Similarity at or above this -> "related"; at or below unrelated_threshold -> "unrelated";
    # anything between is "unclear" and goes to the LLM judge.
    related_threshold: float = 0.75
    unrelated_threshold: float = 0.55
    llm_timeout_s: float = 20.0
    providers_file: Path = SERVICE_ROOT / "providers.toml"


class ProviderConfig(BaseModel):
    name: str
    base_url: str
    model: str
    api_key_env: str


def get_settings() -> Settings:
    # Also put .env into os.environ, so ProviderChain can read API keys by name.
    load_dotenv(SERVICE_ROOT / ".env")
    return Settings()


def load_providers(path: Path) -> list[ProviderConfig]:
    with path.open("rb") as f:
        data = tomllib.load(f)
    return [ProviderConfig(**p) for p in data.get("provider", [])]
