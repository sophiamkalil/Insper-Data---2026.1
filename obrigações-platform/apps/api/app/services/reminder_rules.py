from __future__ import annotations

from datetime import datetime

from app.models.obligation import Obligation
from app.services.recurrence import describe_recurrence, should_send_now


def deve_enviar_lembrete(
    obligation: Obligation,
    agora: datetime | None = None,
) -> bool:
    return should_send_now(obligation, now=agora)


def montar_assunto(obligation: Obligation) -> str:
    return "Alerta: obrigação próxima do prazo"


def montar_mensagem(obligation: Obligation) -> str:
    documento = obligation.document_name or "Sem documento"
    item = obligation.item_number or "Sem item"
    obrigacao = obligation.obligation_text
    prazo = (
        obligation.next_reminder_at.strftime("%d/%m/%Y %H:%M")
        if obligation.next_reminder_at
        else "Sem data"
    )

    tipo = describe_recurrence(obligation)

    return f"""Olá,

Segue um lembrete automático de obrigação contratual.

Recorrência: {tipo}
Documento: {documento}
Item: {item}
Obrigação: {obrigacao}
Próximo lembrete: {prazo}
Status atual: {obligation.status}

Verifique e tome as providências necessárias.
"""