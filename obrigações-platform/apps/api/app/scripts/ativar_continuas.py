"""Ativa email_enabled=True em todas as obrigações contínuas."""
from app.db.session import SessionLocal
from app.models.obligation import Obligation

db = SessionLocal()
try:
    atualizadas = (
        db.query(Obligation)
        .filter(Obligation.recurrence.ilike('contín%'))
        .all()
    )
    for o in atualizadas:
        o.email_enabled = True
    db.commit()
    print(f"{len(atualizadas)} obrigacoes continuas ativadas no lembrete mensal.")
finally:
    db.close()
