from datetime import UTC, date, datetime

from sqlalchemy import Column, DateTime, Text
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class TravelProject(SQLModel, table=True):
    __tablename__ = "travel_projects"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=150)
    description: str | None = Field(default=None, sa_column=Column(Text))
    start_date: date | None = None
    is_completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False, default=utc_now),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=utc_now,
            onupdate=utc_now,
        ),
    )

    places: list["ProjectPlace"] = Relationship(back_populates="project")
