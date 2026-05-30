from sqlmodel import Session, col, func, select

from ..models.place import ProjectPlace
from ..models.project import TravelProject
from ..schemas.place import ProjectPlaceCreate, ProjectPlaceUpdate
from .art_api import ArtInstituteClient

MAX_PROJECT_PLACES = 10


def _get_project(session: Session, project_id: int) -> TravelProject:
    project = session.get(TravelProject, project_id)
    if project is None:
        raise LookupError(f"project with id={project_id} was not found")
    return project


def _update_project_completion(session: Session, project_id: int) -> None:
    project = _get_project(session, project_id)
    places = session.exec(select(ProjectPlace).where(ProjectPlace.project_id == project_id)).all()
    project.is_completed = bool(places) and all(place.visited for place in places)
    session.add(project)


def list_project_places(
    session: Session,
    project_id: int,
    offset: int = 0,
    limit: int = 20,
) -> list[ProjectPlace]:
    _get_project(session, project_id)
    statement = (
        select(ProjectPlace)
        .where(ProjectPlace.project_id == project_id)
        .order_by(col(ProjectPlace.id).desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_project_place(session: Session, project_id: int, place_id: int) -> ProjectPlace:
    _get_project(session, project_id)
    statement = select(ProjectPlace).where(
        ProjectPlace.id == place_id,
        ProjectPlace.project_id == project_id,
    )
    place = session.exec(statement).first()
    if place is None:
        raise LookupError(f"place with id={place_id} was not found in project id={project_id}")
    return place


def add_project_place(
    session: Session,
    project_id: int,
    payload: ProjectPlaceCreate,
    art_client: ArtInstituteClient,
    auto_commit: bool = True,
) -> ProjectPlace:
    _get_project(session, project_id)

    count_statement = (
        select(func.count()).select_from(ProjectPlace).where(ProjectPlace.project_id == project_id)
    )
    current_count = session.exec(count_statement).one()
    if current_count >= MAX_PROJECT_PLACES:
        raise ValueError("project cannot have more than 10 places")

    duplicate_statement = select(ProjectPlace).where(
        ProjectPlace.project_id == project_id,
        ProjectPlace.external_id == payload.external_id,
    )
    duplicate = session.exec(duplicate_statement).first()
    if duplicate is not None:
        raise FileExistsError("place with the same external_id already exists in this project")

    if not art_client.validate_place_exists(payload.external_id):
        raise ValueError("external place does not exist in art institute api")

    title = None
    try:
        artwork = art_client.get_artwork(payload.external_id)
        title = artwork.get("title")
    except Exception:
        title = None

    place = ProjectPlace(
        project_id=project_id,
        external_id=payload.external_id,
        title=title if isinstance(title, str) and title.strip() else None,
        notes=payload.notes,
    )
    session.add(place)
    session.flush()

    _update_project_completion(session, project_id)

    if auto_commit:
        session.commit()
        session.refresh(place)

    return place


def update_project_place(
    session: Session,
    project_id: int,
    place_id: int,
    payload: ProjectPlaceUpdate,
) -> ProjectPlace:
    place = get_project_place(session, project_id, place_id)
    updates = payload.model_dump(exclude_unset=True)

    if "notes" in updates:
        place.notes = updates["notes"]
    if "visited" in updates:
        place.visited = updates["visited"]

    session.add(place)
    _update_project_completion(session, project_id)
    session.commit()
    session.refresh(place)
    return place
