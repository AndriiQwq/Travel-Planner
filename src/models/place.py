from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from .project import TravelProject, utc_now


class ProjectPlace(SQLModel, table=True):
    __tablename__ = "project_places"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "external_id",
            name="uq_project_places_project_id_external_id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(
        sa_column=Column(
            ForeignKey("travel_projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )
    external_id: str = Field(index=True, max_length=64)
    title: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, sa_column=Column(Text))
    visited: bool = Field(default=False, index=True)
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

    project: TravelProject = Relationship(back_populates="places")
