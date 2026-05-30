from collections.abc import Generator
from importlib import import_module
from sqlmodel import SQLModel, Session, create_engine
from ..config import get_settings

settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def create_db_and_tables() -> None:
    import_module("src.models")
    SQLModel.metadata.create_all(engine)
