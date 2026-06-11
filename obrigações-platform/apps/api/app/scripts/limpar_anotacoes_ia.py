"""Remove anotações '(Adicionado por IA: ...)' dos campos de texto das obrigações."""
import re
from app.db.session import SessionLocal
from app.models.obligation import Obligation

CAMPOS = ['contract_phase', 'deadline_text', 'interpretive_notes']


def limpar(s):
    if not s:
        return s
    s = re.sub(r'\s*\(Adicionado por IA:.*$', '', s, flags=re.DOTALL)
    s = re.sub(r'\s*[–-]\s*Adicionado por IA:.*$', '', s, flags=re.DOTALL)
    if s.startswith('* '):
        s = s[2:]
    return s.strip()


db = SessionLocal()
try:
    alteradas = 0
    for o in db.query(Obligation).all():
        mudou = False
        for campo in CAMPOS:
            original = getattr(o, campo)
            limpo = limpar(original)
            if limpo != original:
                setattr(o, campo, limpo)
                mudou = True
        if mudou:
            alteradas += 1
    db.commit()
    print(f"{alteradas} obrigações limpas.")
finally:
    db.close()
