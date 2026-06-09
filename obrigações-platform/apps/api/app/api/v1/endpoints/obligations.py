from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.obligation import Obligation
from app.schemas.obligation import (
    ObligationCreateRequest,
    ObligationListResponse,
    ObligationRead,
)

router = APIRouter()


@router.get("/", response_model=ObligationListResponse)
def list_obligations(
    db: Session = Depends(get_db),
    q: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=15, le=100),
):
    query = db.query(Obligation)

    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Obligation.obligation_text.ilike(term),
                Obligation.document_name.ilike(term),
                Obligation.item_number.ilike(term),
                Obligation.responsible.ilike(term),
                Obligation.observations.ilike(term),
                Obligation.recurrence.ilike(term),
                Obligation.trigger_family.ilike(term),
                Obligation.condition_raw.ilike(term),
                Obligation.condition_canonical.ilike(term),
            )
        )

    if status and status != "all":
        query = query.filter(Obligation.status == status)

    total = query.count()

    items = (
        query.order_by(Obligation.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/", response_model=ObligationRead)
def create_obligation(
    payload: ObligationCreateRequest,
    db: Session = Depends(get_db),
):
    obligation = Obligation(
        contract_id=payload.contract_id,
        document_name=payload.document_name,
        item_number=payload.item_number,
        recurrence=payload.recurrence,
        obligation_text=payload.obligation_text,
        observations=payload.observations,
        responsible=payload.responsible,
        status=payload.status,
        email_enabled=payload.email_enabled,
        email_destino=payload.email_destino,
        data_envio_email=payload.data_envio_email,
        trigger_family=payload.trigger_family,
        trigger_type=payload.trigger_type,
        condition_raw=payload.condition_raw,
        condition_canonical=payload.condition_canonical,
        condition_status=payload.condition_status,
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation