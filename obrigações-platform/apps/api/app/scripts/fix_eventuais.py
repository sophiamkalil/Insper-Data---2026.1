"""
Migration: popula trigger_family, condition_raw e condition_status
para obrigações com recorrência "Eventual (Sob Condição)".

Uso:
    python -m app.scripts.fix_eventuais
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.db.session import SessionLocal
from app.models.obligation import Obligation


def fix_eventuais() -> None:
    db = SessionLocal()
    try:
        eventuais = (
            db.query(Obligation)
            .filter(Obligation.recurrence.ilike("Eventual%"))
            .all()
        )
        updated = 0
        for obr in eventuais:
            changed = False
            if not obr.trigger_family:
                obr.trigger_family = "eventual"
                changed = True
            dep = (obr.depends_on_clauses or "").strip()
            if not obr.condition_raw and dep and dep not in ("—", "\x97", "—"):
                obr.condition_raw = dep
                changed = True
            if not obr.condition_status:
                obr.condition_status = "pendente"
                changed = True
            if changed:
                db.add(obr)
                updated += 1
        db.commit()
        print(f"Concluído: {len(eventuais)} eventuais encontradas, {updated} atualizadas.")
    finally:
        db.close()


if __name__ == "__main__":
    fix_eventuais()
