from datetime import datetime, timedelta

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.obligation import Obligation
from app.models.status_history import ObligationStatusHistory
from app.schemas.obligation import ObligationDetailResponse, ObligationUpdateRequest
from app.services.email_service import enviar_email
from app.services.recurrence import (
    calculate_next_recurrence_at,
    calculate_next_reminder_at,
)
from app.services.reminder_rules import montar_assunto, montar_mensagem

router = APIRouter()


class SendEmailRequest(BaseModel):
    send_at: str | None = None


def _parse_send_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _tem_lembrete_em_payload(payload: ObligationUpdateRequest) -> bool:
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


_CONTINUAS = {"contínuo"}


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


@router.get("/{obligation_id}", response_model=ObligationDetailResponse)
def get_obligation(obligation_id: int, db: Session = Depends(get_db)):
    obligation = db.query(Obligation).filter(Obligation.id == obligation_id).first()

    if not obligation:
        raise HTTPException(status_code=404, detail="Obrigação não encontrada")

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
    obligation = db.query(Obligation).filter(Obligation.id == obligation_id).first()

    if not obligation:
        raise HTTPException(status_code=404, detail="Obrigação não encontrada")

    new_email_enabled = (
        payload.email_enabled
        if payload.email_enabled is not None
        else obligation.email_enabled
    )
    new_email_destino = (
        payload.email_destino
        if payload.email_destino is not None
        else obligation.email_destino
    )

    is_continua = (obligation.recurrence or "").strip().lower() in _CONTINUAS
    if not is_continua:
        _validar_email_para_lembrete(
            email_enabled=new_email_enabled,
            email_destino=new_email_destino,
            tem_lembrete=_tem_lembrete_em_payload(payload) or bool(obligation.recurrence_mode or obligation.manual_reminder_at),
        )

    old_status = obligation.status
    status_changed = False

    if payload.status is not None and payload.status != obligation.status:
        if (
            payload.status == "completed"
            and (obligation.trigger_family or "").strip().lower() == "eventual"
            and (obligation.condition_status or "").strip().lower() != "cumprida"
        ):
            raise HTTPException(
                status_code=400,
                detail="A condição de ativação desta obrigação ainda não foi cumprida.",
            )
        obligation.status = payload.status
        status_changed = True

    if payload.observations is not None:
        obligation.observations = payload.observations

    if payload.email_enabled is not None:
        obligation.email_enabled = payload.email_enabled

    if payload.email_destino is not None:
        obligation.email_destino = payload.email_destino

    if payload.manual_reminder_at is not None:
        obligation.manual_reminder_at = payload.manual_reminder_at

    if payload.recurrence_mode is not None:
        obligation.recurrence_mode = payload.recurrence_mode

    if payload.recurrence_time is not None:
        obligation.recurrence_time = payload.recurrence_time

    if payload.recurrence_interval_days is not None:
        obligation.recurrence_interval_days = payload.recurrence_interval_days

    if payload.recurrence_weekday is not None:
        obligation.recurrence_weekday = payload.recurrence_weekday

    if payload.recurrence_day_of_month is not None:
        obligation.recurrence_day_of_month = payload.recurrence_day_of_month

    if payload.recurrence_month is not None:
        obligation.recurrence_month = payload.recurrence_month

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

    obligation.next_recurrence_at = calculate_next_recurrence_at(
        obligation,
        reference_datetime=datetime.now(),
    )
    obligation.next_reminder_at = calculate_next_reminder_at(
        obligation,
        reference_datetime=datetime.now(),
    )

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
    payload: SendEmailRequest | None = None,
    db: Session = Depends(get_db),
):
    obligation = db.query(Obligation).filter(Obligation.id == obligation_id).first()

    if not obligation:
        raise HTTPException(status_code=404, detail="Obrigação não encontrada")

    if not obligation.email_destino:
        raise HTTPException(status_code=400, detail="Obrigação sem email configurado")

    if obligation.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Obrigação concluída não deve receber lembrete",
        )

    if (
        (obligation.trigger_family or "").strip().lower() == "eventual"
        and (obligation.condition_status or "").strip().lower() != "cumprida"
    ):
        raise HTTPException(
            status_code=400,
            detail="Condição acionadora ainda não foi cumprida",
        )

    send_at = _parse_send_at(payload.send_at if payload else None)

    if send_at and send_at > datetime.now():
        obligation.manual_reminder_at = send_at
        obligation.next_reminder_at = send_at
        db.commit()
        return {
            "success": True,
            "scheduled": True,
            "send_at": send_at.isoformat(),
        }

    assunto = montar_assunto(obligation)
    mensagem = montar_mensagem(obligation)

    enviar_email(obligation.email_destino, assunto, mensagem)

    now = datetime.now()
    obligation.status_envio = "enviado"
    obligation.last_email_sent_at = now
    obligation.manual_reminder_sent_at = now
    obligation.manual_reminder_at = None
    obligation.next_recurrence_at = calculate_next_recurrence_at(
        obligation,
        reference_datetime=now + timedelta(seconds=1),
    )
    obligation.next_reminder_at = calculate_next_reminder_at(
        obligation,
        reference_datetime=now + timedelta(seconds=1),
    )

    db.commit()

    return {
        "success": True,
        "scheduled": False,
    }


@router.delete("/{obligation_id}")
def delete_obligation(obligation_id: int, db: Session = Depends(get_db)):
    obligation = db.query(Obligation).filter(Obligation.id == obligation_id).first()

    if not obligation:
        raise HTTPException(status_code=404, detail="Obrigação não encontrada")

    db.delete(obligation)
    db.commit()

    return {
        "success": True,
    }