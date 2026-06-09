from __future__ import annotations

from datetime import date

from app.models.obligation import Obligation


def deve_enviar_lembrete(
    obligation: Obligation,
    hoje: date | None = None,
) -> bool:
    hoje = hoje or date.today()

    if not obligation.email_enabled:
        return False

    if not obligation.email_destino:
        return False

    if (obligation.status_envio or "").lower() == "enviado":
        return False

    if obligation.status == "completed":
        return False

    if (
        (obligation.trigger_family or "").lower() == "eventual"
        and (obligation.condition_status or "").lower() != "cumprida"
    ):
        return False

    if not obligation.data_envio_email:
        return False

    return obligation.data_envio_email.date() == hoje


def montar_assunto(obligation: Obligation) -> str:
    return "Alerta: obrigação próxima do prazo"


def montar_mensagem(obligation: Obligation) -> str:
    documento = obligation.document_name or "Sem documento"
    item = obligation.item_number or "Sem item"
    obrigacao = obligation.obligation_text
    prazo = (
        obligation.data_envio_email.strftime("%d/%m/%Y")
        if obligation.data_envio_email
        else "Sem data"
    )

    if obligation.trigger_family == "eventual":
        tipo = "Eventual"
    else:
        tipo = "Operacional"

    return f"""Olá,

Segue um lembrete automático de obrigação contratual.

Tipo: {tipo}
Documento: {documento}
Item: {item}
Obrigação: {obrigacao}
Prazo do envio: {prazo}
Status atual: {obligation.status}

Verifique e tome as providências necessárias.
"""