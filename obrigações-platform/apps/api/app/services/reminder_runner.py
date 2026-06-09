from __future__ import annotations

from datetime import datetime, date

from sqlalchemy.orm import Session

from app.models.obligation import Obligation
from app.services.email_service import enviar_email
from app.services.reminder_rules import (
    deve_enviar_lembrete,
    montar_assunto,
    montar_mensagem,
)


def rodar_lembretes_email(db: Session) -> int:
    hoje = date.today()
    enviados = 0

    obligations = (
        db.query(Obligation)
        .filter(Obligation.email_enabled == True)  # noqa: E712
        .all()
    )

    for obligation in obligations:
        if not deve_enviar_lembrete(obligation, hoje=hoje):
            continue

        destinatario = obligation.email_destino
        if not destinatario:
            continue

        assunto = montar_assunto(obligation)
        mensagem = montar_mensagem(obligation)

        enviar_email(destinatario, assunto, mensagem)

        obligation.status_envio = "enviado"
        obligation.last_email_sent_at = datetime.utcnow()
        enviados += 1

    db.commit()
    return enviados