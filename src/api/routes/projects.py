from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, col, select

from ...db.session import get_session
from ...models.project import TravelProject
from ...schemas.project import (
    TravelProjectCreate,
    TravelProjectDetailRead,
    TravelProjectRead,
    TravelProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_project_or_404(session: Session, project_id: int) -> TravelProject:
    project = session.get(TravelProject, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"project with id={project_id} was not found",
        )
    return project


@router.post("", response_model=TravelProjectDetailRead, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    payload: TravelProjectCreate,
    session: Session = Depends(get_session),
) -> TravelProjectDetailRead:
    if payload.places:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="project places on create will be added in next step",
        )

    project = TravelProject(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return TravelProjectDetailRead.model_validate(project)


@router.get("", response_model=list[TravelProjectRead])
def list_projects_endpoint(session: Session = Depends(get_session)) -> list[TravelProjectRead]:
    statement = select(TravelProject).order_by(col(TravelProject.id).desc())
    projects = session.exec(statement).all()
    return [TravelProjectRead.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=TravelProjectDetailRead)
def get_project_endpoint(
    project_id: int,
    session: Session = Depends(get_session),
) -> TravelProjectDetailRead:
    project = _get_project_or_404(session, project_id)
    return TravelProjectDetailRead.model_validate(project)


@router.patch("/{project_id}", response_model=TravelProjectDetailRead)
def update_project_endpoint(
    project_id: int,
    payload: TravelProjectUpdate,
    session: Session = Depends(get_session),
) -> TravelProjectDetailRead:
    project = _get_project_or_404(session, project_id)
    updates = payload.model_dump(exclude_unset=True)

    for field_name, field_value in updates.items():
        setattr(project, field_name, field_value)

    session.add(project)
    session.commit()
    session.refresh(project)
    return TravelProjectDetailRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_project_endpoint(
    project_id: int,
    session: Session = Depends(get_session),
) -> Response:
    project = _get_project_or_404(session, project_id)
    session.delete(project)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
