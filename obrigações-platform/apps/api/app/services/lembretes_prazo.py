"""Ativa lembretes e calcula next_reminder_at para obrigações com prazo definido.

Chamado automaticamente ao salvar configurações de antecedência.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.obligation import Obligation
from app.models.settings import AppSettings


def _next_month_date(dt: datetime) -> datetime:
    if dt.month == 12:
        return dt.replace(year=dt.year + 1, month=1)
    return dt.replace(month=dt.month + 1)


def aplicar_lembretes_por_prazo(db: Session) -> int:
    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if not settings or not settings.email_escritorio:
        return 0

    email = settings.email_escritorio
    agora = datetime.now()
    n = 0

    # Periódica - Mensal
    for o in db.query(Obligation).filter(
        Obligation.recurrence == 'Periódica - Mensal',
        Obligation.next_recurrence_at.isnot(None),
    ):
        nr = o.next_recurrence_at
        remind = nr - timedelta(days=settings.antecedencia_mensal_dias)
        if remind <= agora:
            nr = _next_month_date(nr)
            o.next_recurrence_at = nr
            remind = nr - timedelta(days=settings.antecedencia_mensal_dias)
        o.next_reminder_at = remind
        o.email_enabled = True
        if not o.email_destino:
            o.email_destino = email
        n += 1

    # Periódica - Anual
    for o in db.query(Obligation).filter(
        Obligation.recurrence.ilike('Periódica - Anual'),
        Obligation.next_recurrence_at.isnot(None),
    ):
        nr = o.next_recurrence_at
        remind = nr - timedelta(days=settings.antecedencia_anual_dias)
        if remind <= agora:
            nr = nr.replace(year=nr.year + 1)
            o.next_recurrence_at = nr
            remind = nr - timedelta(days=settings.antecedencia_anual_dias)
        o.next_reminder_at = remind
        o.email_enabled = True
        if not o.email_destino:
            o.email_destino = email
        n += 1

    # Encerramento da Concessão
    for o in db.query(Obligation).filter(
        Obligation.recurrence == 'Encerramento da Concessão',
        Obligation.deadline.isnot(None),
    ):
        o.next_reminder_at = o.deadline - timedelta(days=settings.antecedencia_encerramento_dias)
        o.email_enabled = True
        if not o.email_destino:
            o.email_destino = email
        n += 1

    db.commit()
    return n
