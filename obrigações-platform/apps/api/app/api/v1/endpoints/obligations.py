from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.obligation import Obligation
from app.schemas.obligation import (
    ObligationCreateRequest,
    ObligationListResponse,
    ObligationRead,
)
from app.services.recurrence import (
    calculate_next_recurrence_at,
    calculate_next_reminder_at,
)

router = APIRouter()


def _tem_lembrete(payload: ObligationCreateRequest) -> bool:
    return any(
        [
            payload.manual_reminder_at is not None,
            payload.recurrence_mode is not None,
            payload.recurrence_interval_days is not None,
            payload.recurrence_weekday is not None,
            payload.recurrence_day_of_month is not None,
            payload.recurrence_month is not None,
        ]
    )


def _validar_email_para_lembrete(
    email_enabled: bool,
    email_destino: str | None,
    tem_lembrete: bool,
) -> None:
    if tem_lembrete and (not email_enabled or not email_destino):
        raise HTTPException(
            status_code=400,
            detail="Preencha o email antes de salvar uma recorrência ou lembrete manual.",
        )


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
    _validar_email_para_lembrete(
        email_enabled=payload.email_enabled,
        email_destino=payload.email_destino,
        tem_lembrete=_tem_lembrete(payload),
    )

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
        manual_reminder_at=payload.manual_reminder_at,
        recurrence_mode=payload.recurrence_mode,
        recurrence_time=payload.recurrence_time,
        recurrence_interval_days=payload.recurrence_interval_days,
        recurrence_weekday=payload.recurrence_weekday,
        recurrence_day_of_month=payload.recurrence_day_of_month,
        recurrence_month=payload.recurrence_month,
        trigger_family=payload.trigger_family,
        trigger_type=payload.trigger_type,
        condition_raw=payload.condition_raw,
        condition_canonical=payload.condition_canonical,
        condition_status=payload.condition_status,
    )

    obligation.next_recurrence_at = calculate_next_recurrence_at(
        obligation,
        reference_datetime=datetime.now(),
    )
    obligation.next_reminder_at = calculate_next_reminder_at(
        obligation,
        reference_datetime=datetime.now(),
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation