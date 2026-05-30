from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectPlaceCreate(BaseModel):
    external_id: str = Field(min_length=1, max_length=64)
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("external_id")
    @classmethod
    def clean_external_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("external_id cannot be blank")
        return value


class ProjectPlaceUpdate(BaseModel):
    notes: str | None = Field(default=None, max_length=5000)
    visited: bool | None = None


class ProjectPlaceRead(BaseModel):
    id: int
    project_id: int
    external_id: str
    title: str | None
    notes: str | None
    visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
