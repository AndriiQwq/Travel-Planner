from sqlmodel import Session, col, func, select

from ..models.place import ProjectPlace
from ..models.project import TravelProject
from ..schemas.project import TravelProjectCreate, TravelProjectUpdate
from .art_api import ArtInstituteClient
from .places import add_project_place


def list_projects(session: Session) -> list[TravelProject]:
    statement = select(TravelProject).order_by(col(TravelProject.id).desc())
    return list(session.exec(statement).all())


def get_project(session: Session, project_id: int) -> TravelProject:
    project = session.get(TravelProject, project_id)
    if project is None:
        raise LookupError(f"project with id={project_id} was not found")
    return project


def create_project(
    session: Session,
    payload: TravelProjectCreate,
    art_client: ArtInstituteClient,
) -> TravelProject:
    project = TravelProject(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )
    session.add(project)
    session.flush()

    if payload.places:
        for place_payload in payload.places:
            add_project_place(
                session=session,
                project_id=project.id,
                payload=place_payload,
                art_client=art_client,
                auto_commit=False,
            )

    update_project_completion(session, project.id)
    session.commit()
    session.refresh(project)
    return project


def update_project(
    session: Session,
    project_id: int,
    payload: TravelProjectUpdate,
) -> TravelProject:
    project = get_project(session, project_id)
    updates = payload.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(project, key, value)

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_project(session: Session, project_id: int) -> None:
    project = get_project(session, project_id)

    visited_count_statement = select(func.count()).select_from(ProjectPlace).where(
        ProjectPlace.project_id == project_id,
        ProjectPlace.visited.is_(True),
    )
    visited_count = session.exec(visited_count_statement).one()
    if visited_count > 0:
        raise ValueError("cannot delete project with visited places")

    session.delete(project)
    session.commit()


def update_project_completion(session: Session, project_id: int) -> None:
    project = get_project(session, project_id)
    places = session.exec(
        select(ProjectPlace).where(ProjectPlace.project_id == project_id)
    ).all()

    project.is_completed = bool(places) and all(place.visited for place in places)
    session.add(project)
