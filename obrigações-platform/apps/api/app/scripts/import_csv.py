"""
Importa/atualiza obrigações a partir do CSV enriquecido.

Uso:
    python -m app.scripts.import_csv <caminho_do_csv>

Comportamento:
  - Faz upsert por (item_number, document_name)
  - Atualiza campos descritivos; preserva status, email_enabled, reminders
  - Obrigações novas (não encontradas no banco) são inseridas com status='pending'
"""

import csv
import sys
from pathlib import Path

# garante que o pacote app é encontrado quando rodado da pasta apps/api
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.db.session import SessionLocal
from app.models.obligation import Obligation

DESCRIPTIVE_FIELDS = {
    "ID": "obligation_code",
    "Item": "item_number",
    "Documento": "document_name",
    "Recorrência": "recurrence",
    "Obrigação_Original": "obligation_text",
    "Observações_Original": "observations",
    "Fase_Contratual": "contract_phase",
    "Tipo_Gatilho": "trigger_category",
    "Lógica_Cumprimento": "compliance_logic",
    "Fonte_Gatilho": "trigger_source",
    "Insumos_Internos": "internal_inputs",
    "Insumos_Externos": "external_inputs",
    "Depende_de_Cláusulas": "depends_on_clauses",
    "É_Insumo_Para": "is_input_for_clauses",
    "Tipo_Prazo": "deadline_type",
    "Valor_Prazo": "deadline_value",
    "Prazo_Cumprimento_Texto": "deadline_text",
    "Saída_Esperada": "expected_output",
    "Notas_Interpretativas": "interpretive_notes",
}

CONTRACT_ID = 1


def _v(row: dict, key: str) -> str | None:
    val = row.get(key, "").strip()
    return val if val else None


def import_csv(csv_path: str) -> None:
    db = SessionLocal()
    try:
        with open(csv_path, encoding="latin-1", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)

        updated = 0
        inserted = 0

        for i, row in enumerate(rows):
            item_num = _v(row, "Item")
            doc_name = _v(row, "Documento")

            existing = (
                db.query(Obligation)
                .filter(
                    Obligation.item_number == item_num,
                    Obligation.document_name == doc_name,
                )
                .first()
            )

            if existing:
                for csv_col, model_col in DESCRIPTIVE_FIELDS.items():
                    setattr(existing, model_col, _v(row, csv_col))
                db.add(existing)
                updated += 1
            else:
                obr = Obligation(
                    contract_id=CONTRACT_ID,
                    status="pending",
                    email_enabled=False,
                )
                for csv_col, model_col in DESCRIPTIVE_FIELDS.items():
                    setattr(obr, model_col, _v(row, csv_col))
                db.add(obr)
                inserted += 1

            if (i + 1) % 50 == 0:
                db.commit()
                print(f"  {i + 1}/{len(rows)} processadas...")

        db.commit()
        print(f"\nConcluído: {updated} atualizadas, {inserted} inseridas.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m app.scripts.import_csv <caminho_csv>")
        sys.exit(1)
    import_csv(sys.argv[1])
