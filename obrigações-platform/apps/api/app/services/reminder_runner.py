from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.models.obligation import Obligation
from app.models.status_history import ObligationStatusHistory
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

_RECORRENCIAS_CONTINUAS = {"contínuo"}
_RECORRENCIAS_CONTINUAS_LIST = ["Contínuo"]


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


def rodar_lembretes_continuos(db: Session) -> int:
    """Envia um único lembrete ao escritório no dia 1 de cada mês."""
    from app.models.settings import AppSettings

    agora = datetime.now()

    config = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if not config or not config.email_escritorio:
        logger.warning("Lembrete mensal: email do escritório não configurado.")
        return 0

    tem_continuas = (
        db.query(Obligation)
        .filter(
            Obligation.email_enabled == True,  # noqa: E712
            Obligation.status != "completed",
            Obligation.recurrence.in_(_RECORRENCIAS_CONTINUAS_LIST),
        )
        .first()
    ) is not None

    if not tem_continuas:
        return 0

    mes_ano = agora.strftime("%B de %Y")
    assunto = "Lembrete mensal: obrigações contínuas"
    mensagem = (
        f"Lembrete automático: verifique o cumprimento das obrigações contínuas "
        f"pela concessionária neste mês de {mes_ano}.\n\n"
        "Acesse o painel para conferir as obrigações de recorrência "
        "Mensal, Trimestral, Semestral e Anual."
    )

    enviar_email(config.email_escritorio, assunto, mensagem)
    return 1


def resetar_obrigacoes_continuas(db: Session) -> int:
    """Reseta status 'completed' → 'pending' das obrigações contínuas no início do mês."""
    concluidas = (
        db.query(Obligation)
        .filter(
            Obligation.status == "completed",
            Obligation.recurrence.in_(_RECORRENCIAS_CONTINUAS_LIST),
        )
        .all()
    )
    for o in concluidas:
        o.status = "pending"
        db.add(ObligationStatusHistory(
            obligation_id=o.id,
            old_status="completed",
            new_status="pending",
            note="Reiniciado automaticamente no início do mês",
        ))
    db.commit()
    return len(concluidas)