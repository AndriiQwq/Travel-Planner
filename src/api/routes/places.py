from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from ...db.session import get_session
from ...schemas.place import ProjectPlaceCreate, ProjectPlaceRead, ProjectPlaceUpdate
from ...services.art_api import ArtInstituteClient, get_art_institute_client
from ...services.places import (
    add_project_place,
    get_project_place,
    list_project_places,
    update_project_place,
)

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])


@router.post("", response_model=ProjectPlaceRead, status_code=status.HTTP_201_CREATED)
def create_project_place_endpoint(
    project_id: int,
    payload: ProjectPlaceCreate,
    session: Session = Depends(get_session),
    art_client: ArtInstituteClient = Depends(get_art_institute_client),
) -> ProjectPlaceRead:
    try:
        place = add_project_place(session, project_id, payload, art_client)
        return ProjectPlaceRead.model_validate(place)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("", response_model=list[ProjectPlaceRead])
def list_project_places_endpoint(
    project_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[ProjectPlaceRead]:
    try:
        places = list_project_places(session, project_id, offset=offset, limit=limit)
        return [ProjectPlaceRead.model_validate(place) for place in places]
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{place_id}", response_model=ProjectPlaceRead)
def get_project_place_endpoint(
    project_id: int,
    place_id: int,
    session: Session = Depends(get_session),
) -> ProjectPlaceRead:
    try:
        place = get_project_place(session, project_id, place_id)
        return ProjectPlaceRead.model_validate(place)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{place_id}", response_model=ProjectPlaceRead)
def update_project_place_endpoint(
    project_id: int,
    place_id: int,
    payload: ProjectPlaceUpdate,
    session: Session = Depends(get_session),
) -> ProjectPlaceRead:
    try:
        place = update_project_place(session, project_id, place_id, payload)
        return ProjectPlaceRead.model_validate(place)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
