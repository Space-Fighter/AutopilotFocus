"""Database models used by the AI service.

The classes come from db_models.py, which is GENERATED from the live database by
scripts/gen_models.py. Never edit db_models.py and never call SQLModel.metadata.create_all():
db/migrations/*.sql owns the schema.

They're re-exported here under clearer names, because the table class `ContentFacts` would
clash with the pydantic `ContentFacts` in schemas.py.
"""

from .db_models import ContentFacts as ContentFactsRow

EMBEDDING_DIM = 384  # bge-small-en-v1.5; must match vector(384) in the migrations

__all__ = ["ContentFactsRow", "EMBEDDING_DIM"]
