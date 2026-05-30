from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/travel_planner"
    database_echo: bool = Field(default=False)
    art_api_base_url: str = "https://api.artic.edu/api/v1"
    art_api_timeout_seconds: float = Field(default=5.0, gt=0)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
