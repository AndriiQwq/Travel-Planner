from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from ...db.session import get_session
from ...schemas.project import (
    TravelProjectCreate,
    TravelProjectDetailRead,
    TravelProjectRead,
    TravelProjectUpdate,
)
from ...services.art_api import ArtInstituteClient, get_art_institute_client
from ...services.projects import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=TravelProjectDetailRead, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    payload: TravelProjectCreate,
    session: Session = Depends(get_session),
    art_client: ArtInstituteClient = Depends(get_art_institute_client),
) -> TravelProjectDetailRead:
    try:
        project = create_project(session, payload, art_client)
        return TravelProjectDetailRead.model_validate(project)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("", response_model=list[TravelProjectRead])
def list_projects_endpoint(session: Session = Depends(get_session)) -> list[TravelProjectRead]:
    projects = list_projects(session)
    return [TravelProjectRead.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=TravelProjectDetailRead)
def get_project_endpoint(
    project_id: int,
    session: Session = Depends(get_session),
) -> TravelProjectDetailRead:
    try:
        project = get_project(session, project_id)
        return TravelProjectDetailRead.model_validate(project)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{project_id}", response_model=TravelProjectDetailRead)
def update_project_endpoint(
    project_id: int,
    payload: TravelProjectUpdate,
    session: Session = Depends(get_session),
) -> TravelProjectDetailRead:
    try:
        project = update_project(session, project_id, payload)
        return TravelProjectDetailRead.model_validate(project)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_project_endpoint(
    project_id: int,
    session: Session = Depends(get_session),
) -> Response:
    try:
        delete_project(session, project_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
