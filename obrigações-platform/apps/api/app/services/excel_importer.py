from __future__ import annotations

from io import BytesIO
from pathlib import Path
import unicodedata

import pandas as pd
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.status_history import ObligationStatusHistory


def _limpar(valor):
    if valor is None or pd.isna(valor):
        return ""
    return str(valor).strip()


def _normalizar_coluna(valor: str) -> str:
    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = texto.replace(" ", "_")
    texto = texto.replace("-", "_")
    return texto


def _bool(valor) -> bool:
    texto = _limpar(valor).lower()
    return texto in {"1", "true", "sim", "s", "yes", "y", "x"}


def _data(valor):
    if valor is None or pd.isna(valor):
        return None

    parsed = pd.to_datetime(valor, errors="coerce")
    if pd.isna(parsed):
        return None

    return parsed.to_pydatetime()


def _primeiro_valor(row, campos: list[str]) -> str | None:
    for campo in campos:
        if campo in row.index:
            valor = _limpar(row.get(campo))
            if valor:
                return valor
    return None


def importar_planilha_substituindo_base(
    db: Session,
    arquivo_bytes: bytes,
    nome_arquivo: str,
) -> dict:
    df = pd.read_excel(BytesIO(arquivo_bytes))
    df.columns = [_normalizar_coluna(col) for col in df.columns]

    contrato = db.query(Contract).order_by(Contract.id.asc()).first()
    if not contrato:
        contrato = Contract(
            name=Path(nome_arquivo).stem or "Planilha importada",
            code=None,
            description=f"Importado de {nome_arquivo}",
        )
        db.add(contrato)
        db.flush()

    db.query(ObligationStatusHistory).delete(synchronize_session=False)
    db.query(Obligation).delete(synchronize_session=False)

    importadas = 0

    for idx, row in df.iterrows():
        document_name = _primeiro_valor(row, ["documento"])
        item_number = _primeiro_valor(row, ["item"])
        recurrence = _primeiro_valor(row, ["recorrencia"])
        obligation_text = _primeiro_valor(
            row,
            ["obrigacao", "descricao", "clausula", "texto_obrigacao"],
        )
        observations = _primeiro_valor(row, ["observacoes"])
        responsible = _primeiro_valor(row, ["responsavel"])

        trigger_family = _primeiro_valor(row, ["trigger_family"])
        trigger_type = _primeiro_valor(row, ["trigger_type"])
        condition_raw = _primeiro_valor(row, ["condition_raw"])
        condition_canonical = _primeiro_valor(row, ["condition_canonical"])
        condition_status = _primeiro_valor(row, ["condition_status"])

        if _primeiro_valor(row, ["condicao_atendida"]) in {"SIM", "sim", "1", "true", "yes"}:
            condition_status = "cumprida"

        if not condition_status and trigger_family == "eventual":
            condition_status = "pendente"

        if not obligation_text:
            obligation_text = document_name or item_number or "Obrigação importada"

        obligation = Obligation(
            contract_id=contrato.id,
            document_name=document_name,
            item_number=item_number,
            recurrence=recurrence,
            obligation_text=obligation_text,
            observations=observations,
            responsible=responsible,
            status="pending",
            source_row=idx + 2,
            email_enabled=_bool(row.get("email_enabled") or row.get("ativar_lembrete_por_email")),
            email_destino=_primeiro_valor(row, ["email_destino", "email"]),
            data_envio_email=_data(row.get("data_envio_email")),
            status_envio=_primeiro_valor(row, ["status_envio"]),
            last_email_sent_at=_data(row.get("last_email_sent_at")),
            trigger_family=trigger_family,
            trigger_type=trigger_type,
            condition_raw=condition_raw,
            condition_canonical=condition_canonical,
            condition_status=condition_status,
        )

        db.add(obligation)
        importadas += 1

    db.commit()

    return {
        "success": True,
        "contract_id": contrato.id,
        "imported": importadas,
        "filename": nome_arquivo,
    }