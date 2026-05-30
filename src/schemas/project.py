from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .place import ProjectPlaceCreate, ProjectPlaceRead

class TravelProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    start_date: date | None = None
    places: list[ProjectPlaceCreate] | None = Field(default=None, max_length=10)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name cannot be blank")
        return value

    @field_validator("places")
    @classmethod
    def validate_places(
        cls,
        value: list[ProjectPlaceCreate] | None,
    ) -> list[ProjectPlaceCreate] | None:
        if value is not None and len(value) == 0:
            raise ValueError("places must not be empty when provided")
        return value

class TravelProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    start_date: date | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("name cannot be blank")
        return value

class TravelProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    start_date: date | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TravelProjectDetailRead(TravelProjectRead):
    places: list[ProjectPlaceRead] = Field(default_factory=list)
