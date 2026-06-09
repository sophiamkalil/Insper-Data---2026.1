from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.obligation import Obligation
from app.services.email_service import enviar_email
from app.services.recurrence import (
    calculate_next_recurrence_at,
    calculate_next_reminder_at,
)
from app.services.reminder_rules import (
    montar_assunto,
    montar_mensagem,
    should_send_now,
)


def rodar_lembretes_email(db: Session) -> int:
    agora = datetime.now()
    enviados = 0

    obligations = (
        db.query(Obligation)
        .filter(Obligation.email_enabled == True)  # noqa: E712
        .all()
    )

    for obligation in obligations:
        if not should_send_now(obligation, now=agora):
            continue

        destinatario = obligation.email_destino
        if not destinatario:
            continue

        assunto = montar_assunto(obligation)
        mensagem = montar_mensagem(obligation)

        enviar_email(destinatario, assunto, mensagem)

        obligation.status_envio = "enviado"
        obligation.last_email_sent_at = agora

        if obligation.manual_reminder_at and obligation.manual_reminder_at <= agora:
            obligation.manual_reminder_sent_at = agora
            obligation.manual_reminder_at = None

        obligation.next_recurrence_at = calculate_next_recurrence_at(
            obligation,
            reference_datetime=agora + timedelta(seconds=1),
        )
        obligation.next_reminder_at = calculate_next_reminder_at(
            obligation,
            reference_datetime=agora + timedelta(seconds=1),
        )

        enviados += 1

    db.commit()
    return enviados