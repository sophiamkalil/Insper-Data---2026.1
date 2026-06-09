from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.obligation import Obligation
from app.models.status_history import ObligationStatusHistory
from app.schemas.obligation import (
    ObligationDetailResponse,
    ObligationUpdateRequest,
)
from app.services.email_service import enviar_email
from app.services.reminder_rules import montar_assunto, montar_mensagem

router = APIRouter()


@router.get("/{obligation_id}", response_model=ObligationDetailResponse)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obrigação não encontrada",
        )

    history = (
        db.query(ObligationStatusHistory)
        .filter(ObligationStatusHistory.obligation_id == obligation_id)
        .order_by(ObligationStatusHistory.changed_at.desc())
        .all()
    )

    return {
        "obligation": obligation,
        "history": history,
    }


@router.patch("/{obligation_id}", response_model=ObligationDetailResponse)
def update_obligation(
    obligation_id: int,
    payload: ObligationUpdateRequest,
    db: Session = Depends(get_db),
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obrigação não encontrada",
        )

    old_status = obligation.status
    status_changed = False

    if payload.status is not None and payload.status != obligation.status:
        obligation.status = payload.status
        status_changed = True

    if payload.observations is not None:
        obligation.observations = payload.observations

    if payload.email_enabled is not None:
        obligation.email_enabled = payload.email_enabled

    if payload.email_destino is not None:
        obligation.email_destino = payload.email_destino

    if payload.data_envio_email is not None:
        obligation.data_envio_email = payload.data_envio_email

    if payload.trigger_family is not None:
        obligation.trigger_family = payload.trigger_family

    if payload.trigger_type is not None:
        obligation.trigger_type = payload.trigger_type

    if payload.condition_raw is not None:
        obligation.condition_raw = payload.condition_raw

    if payload.condition_canonical is not None:
        obligation.condition_canonical = payload.condition_canonical

    if payload.condition_status is not None:
        obligation.condition_status = payload.condition_status

    if status_changed:
        history_entry = ObligationStatusHistory(
            obligation_id=obligation.id,
            old_status=old_status,
            new_status=obligation.status,
            note=payload.note,
        )
        db.add(history_entry)

    db.commit()
    db.refresh(obligation)

    history = (
        db.query(ObligationStatusHistory)
        .filter(ObligationStatusHistory.obligation_id == obligation_id)
        .order_by(ObligationStatusHistory.changed_at.desc())
        .all()
    )

    return {
        "obligation": obligation,
        "history": history,
    }


@router.post("/{obligation_id}/send-email")
def send_email_now(
    obligation_id: int,
    db: Session = Depends(get_db),
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obrigação não encontrada",
        )

    if not obligation.email_enabled:
        raise HTTPException(
            status_code=400,
            detail="Lembrete por email está desativado",
        )

    if not obligation.email_destino:
        raise HTTPException(
            status_code=400,
            detail="Obrigação sem email configurado",
        )

    if obligation.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Obrigação concluída não deve receber lembrete",
        )

    if (
        (obligation.trigger_family or "").lower() == "eventual"
        and (obligation.condition_status or "").lower() != "cumprida"
    ):
        raise HTTPException(
            status_code=400,
            detail="Condição acionadora ainda não foi cumprida",
        )

    assunto = montar_assunto(obligation)
    mensagem = montar_mensagem(obligation)

    enviar_email(
        obligation.email_destino,
        assunto,
        mensagem,
    )

    obligation.status_envio = "enviado"
    obligation.last_email_sent_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
    }


@router.delete("/{obligation_id}")
def delete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obrigação não encontrada",
        )

    db.delete(obligation)
    db.commit()

    return {
        "success": True,
    }