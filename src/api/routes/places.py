from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from ...db.session import get_session
from ...models.place import ProjectPlace
from ...models.project import TravelProject
from ...schemas.place import ProjectPlaceCreate, ProjectPlaceRead, ProjectPlaceUpdate

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])


def _ensure_project_exists(session: Session, project_id: int) -> None:
    project = session.get(TravelProject, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"project with id={project_id} was not found",
        )


def _get_project_place_or_404(session: Session, project_id: int, place_id: int) -> ProjectPlace:
    statement = select(ProjectPlace).where(
        ProjectPlace.id == place_id,
        ProjectPlace.project_id == project_id,
    )
    place = session.exec(statement).first()
    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"place with id={place_id} was not found in project id={project_id}",
        )
    return place


@router.post("", response_model=ProjectPlaceRead, status_code=status.HTTP_201_CREATED)
def create_project_place_endpoint(
    project_id: int,
    payload: ProjectPlaceCreate,
    session: Session = Depends(get_session),
) -> ProjectPlaceRead:
    _ensure_project_exists(session, project_id)

    place = ProjectPlace(
        project_id=project_id,
        external_id=payload.external_id,
        notes=payload.notes,
    )
    session.add(place)

    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="place with the same external_id already exists in this project",
        ) from exc

    session.refresh(place)
    return ProjectPlaceRead.model_validate(place)


@router.get("", response_model=list[ProjectPlaceRead])
def list_project_places_endpoint(
    project_id: int,
    session: Session = Depends(get_session),
) -> list[ProjectPlaceRead]:
    _ensure_project_exists(session, project_id)
    statement = (
        select(ProjectPlace)
        .where(ProjectPlace.project_id == project_id)
        .order_by(col(ProjectPlace.id).desc())
    )
    places = session.exec(statement).all()
    return [ProjectPlaceRead.model_validate(place) for place in places]


@router.get("/{place_id}", response_model=ProjectPlaceRead)
def get_project_place_endpoint(
    project_id: int,
    place_id: int,
    session: Session = Depends(get_session),
) -> ProjectPlaceRead:
    _ensure_project_exists(session, project_id)
    place = _get_project_place_or_404(session, project_id, place_id)
    return ProjectPlaceRead.model_validate(place)


@router.patch("/{place_id}", response_model=ProjectPlaceRead)
def update_project_place_endpoint(
    project_id: int,
    place_id: int,
    payload: ProjectPlaceUpdate,
    session: Session = Depends(get_session),
) -> ProjectPlaceRead:
    _ensure_project_exists(session, project_id)
    place = _get_project_place_or_404(session, project_id, place_id)

    updates = payload.model_dump(exclude_unset=True)
    for field_name, field_value in updates.items():
        setattr(place, field_name, field_value)

    session.add(place)
    session.commit()
    session.refresh(place)
    return ProjectPlaceRead.model_validate(place)
