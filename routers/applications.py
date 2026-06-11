from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Application, User
from models import AppStatus as ModelAppStatus
from schemas import ApplicationCreate, ApplicationResponse, ApplicationUpdate, StatsResponse
from auth import get_current_user

router = APIRouter(prefix="/api", tags=["applications"])


@router.get("/applications", response_model=list[ApplicationResponse])
def list_applications(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("date"),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Application).filter(Application.user_id == current_user.id)

    if status:
        try:
            query = query.filter(Application.status == ModelAppStatus(status))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Application.company.ilike(search_term)) | (Application.role.ilike(search_term))
        )

    sort_map = {
        "date": Application.applied_date,
        "company": Application.company,
        "status": Application.status,
        "created": Application.created_at,
    }
    sort_column = sort_map.get(sort, Application.created_at)
    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.all()


@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    app_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = Application(user_id=current_user.id, **app_data.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
def get_application(
    app_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.query(Application).filter(
        Application.id == app_id, Application.user_id == current_user.id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.put("/applications/{app_id}", response_model=ApplicationResponse)
def update_application(
    app_id: UUID,
    app_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.query(Application).filter(
        Application.id == app_id, Application.user_id == current_user.id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    for key, value in app_data.model_dump(exclude_unset=True).items():
        setattr(application, key, value)

    db.commit()
    db.refresh(application)
    return application


@router.delete("/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    app_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.query(Application).filter(
        Application.id == app_id, Application.user_id == current_user.id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(application)
    db.commit()


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base = db.query(Application).filter(Application.user_id == current_user.id)
    total = base.count()

    counts = {s.value: base.filter(Application.status == s).count() for s in ModelAppStatus}

    responded = counts["interview"] + counts["offer"] + counts["rejected"]
    applied_total = counts["applied"] + responded
    response_rate = (responded / applied_total * 100) if applied_total > 0 else 0
    interviewed = counts["interview"] + counts["offer"]
    interview_rate = (interviewed / applied_total * 100) if applied_total > 0 else 0

    return StatsResponse(
        total=total,
        saved=counts["saved"],
        applied=counts["applied"],
        interview=counts["interview"],
        offer=counts["offer"],
        rejected=counts["rejected"],
        response_rate=round(response_rate, 1),
        interview_rate=round(interview_rate, 1),
    )
