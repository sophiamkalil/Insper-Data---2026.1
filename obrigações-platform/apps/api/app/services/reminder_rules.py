from __future__ import annotations

from datetime import datetime

from app.models.obligation import Obligation
from app.models.settings import ASSUNTO_PADRAO, CORPO_PADRAO
from app.services.recurrence import describe_recurrence, should_send_now


def deve_enviar_lembrete(
    obligation: Obligation,
    agora: datetime | None = None,
) -> bool:
    return should_send_now(obligation, now=agora)


def _aplicar_template(template: str, vars: dict) -> str:
    result = template
    for k, v in vars.items():
        result = result.replace(f'{{{k}}}', str(v))
    return result


def montar_assunto(obligation: Obligation, settings=None) -> str:
    template = (
        settings.email_assunto
        if settings and settings.email_assunto
        else ASSUNTO_PADRAO
    )
    return _aplicar_template(template, {
        'item': obligation.item_number or '',
        'documento': obligation.document_name or '',
    })


def montar_mensagem(obligation: Obligation, settings=None) -> str:
    template = (
        settings.email_corpo
        if settings and settings.email_corpo
        else CORPO_PADRAO
    )
    prazo = (
        obligation.next_reminder_at.strftime("%d/%m/%Y %H:%M")
        if obligation.next_reminder_at
        else "Sem data"
    )
    return _aplicar_template(template, {
        'tipo':      describe_recurrence(obligation),
        'documento': obligation.document_name or 'Sem documento',
        'item':      obligation.item_number or 'Sem item',
        'obrigacao': obligation.obligation_text,
        'prazo':     prazo,
        'status':    obligation.status,
    })