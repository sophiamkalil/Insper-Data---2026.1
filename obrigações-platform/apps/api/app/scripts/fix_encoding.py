"""Corrige caracteres cp1252 que foram importados como latin-1 (U+0080-U+009F)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.db.session import SessionLocal
from app.models.obligation import Obligation

TEXT_FIELDS = [
    'obligation_text', 'item_number', 'recurrence', 'document_name', 'deadline_text',
    'deadline_value', 'observations', 'contract_phase', 'trigger_category',
    'compliance_logic', 'trigger_source', 'internal_inputs', 'external_inputs',
    'depends_on_clauses', 'is_input_for_clauses', 'expected_output',
    'interpretive_notes', 'condition_raw',
]


def fix_text(s):
    if not s:
        return s
    try:
        return s.encode('latin-1').decode('cp1252')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


db = SessionLocal()
try:
    obligations = db.query(Obligation).all()
    corrigidas = 0
    for o in obligations:
        changed = False
        for field in TEXT_FIELDS:
            original = getattr(o, field)
            fixed = fix_text(original)
            if fixed != original:
                setattr(o, field, fixed)
                changed = True
        if changed:
            db.add(o)
            corrigidas += 1
    db.commit()
    print(f"{corrigidas} obrigacoes corrigidas (encoding cp1252).")
finally:
    db.close()
