from datetime import datetime

from app.db.session import SessionLocal
from app.models.obligation import Obligation
from app.models.status_history import ObligationStatusHistory


def run():
    db = SessionLocal()
    try:
        obrigacoes = (
            db.query(Obligation)
            .filter(
                Obligation.contract_phase.ilike("Fase I-A%"),
                Obligation.status != "completed",
            )
            .all()
        )

        print(f"Atualizando {len(obrigacoes)} obrigações...")
        agora = datetime.now()
        for o in obrigacoes:
            old = o.status
            o.status = "completed"
            o.updated_at = agora
            db.add(
                ObligationStatusHistory(
                    obligation_id=o.id,
                    old_status=old,
                    new_status="completed",
                    note="Fase I-A concluída — etapa anterior à Fase I-B",
                )
            )

        db.commit()
        print("Concluído.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
