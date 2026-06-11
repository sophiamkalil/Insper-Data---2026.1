from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.models.obligation import Obligation
from app.models.settings import AppSettings
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


def _next_month_date(dt: datetime) -> datetime:
    if dt.month == 12:
        return dt.replace(year=dt.year + 1, month=1)
    return dt.replace(month=dt.month + 1)


def _advance_periodico_prazo(obligation: Obligation, settings: AppSettings, agora: datetime) -> None:
    """Avança next_recurrence_at e recalcula next_reminder_at para periódicas com prazo definido."""
    nr = obligation.next_recurrence_at
    if not nr:
        return
    rec = obligation.recurrence or ''
    if rec == 'Periódica - Mensal':
        ant = getattr(settings, 'antecedencia_mensal_dias', 7) if settings else 7
        freq = getattr(settings, 'frequencia_mensal_dias', 3) if settings else 3
        proximo = agora + timedelta(days=freq)
        if proximo < nr:
            obligation.next_reminder_at = proximo
        else:
            nr = _next_month_date(nr)
            obligation.next_recurrence_at = nr
            obligation.next_reminder_at = nr - timedelta(days=ant)
    elif 'Periódica - Anual' in rec:
        ant = getattr(settings, 'antecedencia_anual_dias', 30) if settings else 30
        freq = getattr(settings, 'frequencia_anual_dias', 7) if settings else 7
        proximo = agora + timedelta(days=freq)
        if proximo < nr:
            obligation.next_reminder_at = proximo
        else:
            nr = nr.replace(year=nr.year + 1)
            obligation.next_recurrence_at = nr
            obligation.next_reminder_at = nr - timedelta(days=ant)


def rodar_lembretes_email(db: Session) -> int:
    agora = datetime.now()
    enviados = 0

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.email_enabled == True,  # noqa: E712
            ~Obligation.recurrence.ilike('contín%'),
        )
        .all()
    )

    settings = None

    for obligation in obligations:
        if not should_send_now(obligation, now=agora):
            continue

        destinatario = obligation.email_destino
        if not destinatario:
            continue

        if settings is None:
            settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
        assunto = montar_assunto(obligation, settings)
        mensagem = montar_mensagem(obligation, settings)

        enviar_email(destinatario, assunto, mensagem)

        obligation.status_envio = "enviado"
        obligation.last_email_sent_at = agora

        if obligation.manual_reminder_at and obligation.manual_reminder_at <= agora:
            obligation.manual_reminder_sent_at = agora
            obligation.manual_reminder_at = None

        rec = obligation.recurrence or ''
        if settings is None:
            settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
        if rec.startswith('Periódica') and obligation.next_recurrence_at and not obligation.recurrence_mode:
            _advance_periodico_prazo(obligation, settings, agora)
        elif rec == 'Encerramento da Concessão' and obligation.next_recurrence_at:
            freq = getattr(settings, 'frequencia_encerramento_dias', 30) if settings else 30
            obligation.next_reminder_at = agora + timedelta(days=freq)
        else:
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
            Obligation.recurrence.ilike('contín%'),
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
            Obligation.recurrence.ilike('contín%'),
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