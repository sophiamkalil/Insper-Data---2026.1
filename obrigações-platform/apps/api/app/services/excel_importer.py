from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
import re
import unicodedata

import pandas as pd
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.status_history import ObligationStatusHistory
from app.services.recurrence import (
    calculate_next_recurrence_at,
    calculate_next_reminder_at,
)


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


def _inferir_recurrencia(recorrencia_texto: str) -> dict:
    txt = _limpar(recorrencia_texto).lower()

    resultado = {
        "recurrence_mode": None,
        "recurrence_time": "08:00",
        "recurrence_interval_days": None,
        "recurrence_weekday": None,
        "recurrence_day_of_month": None,
        "recurrence_month": None,
    }

    if not txt:
        return resultado

    match = re.search(r"(?:a cada|cada)\s*(\d+)\s*dias?", txt)
    if match:
        resultado["recurrence_mode"] = "manual_days"
        resultado["recurrence_interval_days"] = int(match.group(1))
        return resultado

    if "seman" in txt:
        resultado["recurrence_mode"] = "weekly"
        if "segunda" in txt:
            resultado["recurrence_weekday"] = 0
        elif "terca" in txt or "terça" in txt:
            resultado["recurrence_weekday"] = 1
        elif "quarta" in txt:
            resultado["recurrence_weekday"] = 2
        elif "quinta" in txt:
            resultado["recurrence_weekday"] = 3
        elif "sexta" in txt:
            resultado["recurrence_weekday"] = 4
        elif "sabado" in txt or "sábado" in txt:
            resultado["recurrence_weekday"] = 5
        elif "domingo" in txt:
            resultado["recurrence_weekday"] = 6
        return resultado

    if "mens" in txt:
        resultado["recurrence_mode"] = "monthly"
        return resultado

    if "anual" in txt or "ano" in txt:
        resultado["recurrence_mode"] = "yearly"
        return resultado

    return resultado


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

        if not obligation_text:
            obligation_text = document_name or item_number or "Obrigação importada"

        recurrence_map = _inferir_recurrencia(recurrence or "")

        manual_reminder_at = _data(row.get("manual_reminder_at"))
        if manual_reminder_at is None:
            manual_reminder_at = _data(row.get("data_envio_email"))

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
            email_enabled=_bool(
                row.get("email_enabled") or row.get("ativar_lembrete_por_email")
            ),
            email_destino=_primeiro_valor(row, ["email_destino", "email"]),
            manual_reminder_at=manual_reminder_at,
            recurrence_mode=recurrence_map["recurrence_mode"],
            recurrence_time=recurrence_map["recurrence_time"],
            recurrence_interval_days=recurrence_map["recurrence_interval_days"],
            recurrence_weekday=recurrence_map["recurrence_weekday"],
            recurrence_day_of_month=recurrence_map["recurrence_day_of_month"],
            recurrence_month=recurrence_map["recurrence_month"],
            trigger_family=_primeiro_valor(row, ["trigger_family"]),
            trigger_type=_primeiro_valor(row, ["trigger_type"]),
            condition_raw=_primeiro_valor(row, ["condition_raw"]),
            condition_canonical=_primeiro_valor(row, ["condition_canonical"]),
            condition_status=_primeiro_valor(row, ["condition_status"]),
        )

        if _primeiro_valor(row, ["condicao_atendida"]) in {"SIM", "sim", "1", "true", "yes"}:
            obligation.condition_status = "cumprida"

        obligation.next_recurrence_at = calculate_next_recurrence_at(
            obligation,
            reference_datetime=datetime.now(),
        )
        obligation.next_reminder_at = calculate_next_reminder_at(
            obligation,
            reference_datetime=datetime.now(),
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