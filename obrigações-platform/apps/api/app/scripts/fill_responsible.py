"""Preenche o campo responsible nas obrigacoes com base em trigger_category e obligation_text."""
from app.db.session import SessionLocal
from app.models.obligation import Obligation

db = SessionLocal()
try:
    obrigacoes = db.query(Obligation).filter(Obligation.responsible == None).all()
    for o in obrigacoes:
        o.responsible = "Concessionária"
    db.commit()
    print(f"{len(obrigacoes)} obrigacoes preenchidas como Concessionaria.")
finally:
    db.close()
