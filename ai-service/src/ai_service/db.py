"""Postgres connection.

The tables are created by the SQL files in db/migrations/ at the repo root, never from Python:
this module only connects. Run the migrations before starting the service (db/README.md).
"""

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from .config import Settings


def make_engine(settings: Settings) -> Engine:
    # An Engine holds a pool of open connections; create it once at startup and reuse it.
    # pool_pre_ping checks a connection is still alive before using it (Docker restarts, Neon sleep).
    return create_engine(settings.database_url, pool_pre_ping=True)


def new_session(engine: Engine) -> Session:
    # A Session is one unit of work: queries + changes, then commit. Use it in a `with` block.
    return Session(engine)
