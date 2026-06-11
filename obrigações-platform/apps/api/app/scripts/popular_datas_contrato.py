"""Popula datas concretas nas obrigações com base nas datas âncora do contrato.

Datas âncora:
  Data de eficácia:    01/04/2022
  Aniversário:         todo dia 1º de abril
  Término da concessão: 31/03/2052
  Ano civil:           1 jan – 31 dez
"""
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.obligation import Obligation

TERMINO = datetime(2052, 3, 31, tzinfo=timezone.utc)

ENCERRAMENTO = [
    # (id, deadline, deadline_text)
    (33,  datetime(2052, 3, 31, tzinfo=timezone.utc), "Término da concessão: 31/03/2052"),
    (129, datetime(2049, 3, 31, tzinfo=timezone.utc), "3 anos antes do término: 31/03/2049"),
    (130, datetime(2051, 3, 31, tzinfo=timezone.utc), "1 ano antes do término: 31/03/2051"),
    (156, datetime(2052, 3, 31, tzinfo=timezone.utc), "Término da concessão: 31/03/2052"),
    (162, datetime(2052, 3, 31, tzinfo=timezone.utc), "Término da concessão: 31/03/2052"),
]

MENSAL = [
    # (id, next_recurrence_at, deadline_text)
    (263, datetime(2026, 6, 25, tzinfo=timezone.utc), "Todo dia 25 do mês seguinte"),
    (1,   datetime(2026, 7,  1, tzinfo=timezone.utc), "Todo dia 1 do mês"),
    (226, datetime(2026, 7,  1, tzinfo=timezone.utc), "Todo dia 1 do mês"),
    (227, datetime(2026, 7,  1, tzinfo=timezone.utc), "Todo dia 1 do mês"),
    (230, datetime(2026, 7,  1, tzinfo=timezone.utc), "Todo dia 1 do mês"),
    (265, datetime(2026, 7,  1, tzinfo=timezone.utc), "Todo dia 1 do mês"),
]

ANUAL = [
    # (id, next_recurrence_at, deadline_text, recurrence_override)
    (21,  datetime(2027, 2,  1, tzinfo=timezone.utc), "1º dia útil de fevereiro", None),
    (224, datetime(2027, 4,  1, tzinfo=timezone.utc), "Todo 1º de abril",         None),
    (231, datetime(2027, 4, 30, tzinfo=timezone.utc), "Até 30 de abril",          None),
    # ID 225: deadline_value diz mensal mas recorrência estava errada
    (225, datetime(2026, 7,  1, tzinfo=timezone.utc), "Todo dia 1 do mês",        "Periódica - Mensal"),
]


def run():
    db = SessionLocal()
    try:
        agora = datetime.now(tz=timezone.utc)
        atualizadas = {"encerramento": 0, "mensal": 0, "anual": 0}

        for ob_id, deadline, text in ENCERRAMENTO:
            o = db.get(Obligation, ob_id)
            if o:
                o.deadline = deadline
                o.deadline_text = text
                o.updated_at = agora
                atualizadas["encerramento"] += 1

        for ob_id, next_rec, text in MENSAL:
            o = db.get(Obligation, ob_id)
            if o:
                o.next_recurrence_at = next_rec
                o.deadline_text = text
                o.updated_at = agora
                atualizadas["mensal"] += 1

        for ob_id, next_rec, text, recurrence in ANUAL:
            o = db.get(Obligation, ob_id)
            if o:
                o.next_recurrence_at = next_rec
                o.deadline_text = text
                if recurrence:
                    o.recurrence = recurrence
                o.updated_at = agora
                atualizadas["anual"] += 1

        db.commit()
        print(f"Encerramento: {atualizadas['encerramento']} obrigações atualizadas.")
        print(f"Periódica - Mensal: {atualizadas['mensal']} obrigações atualizadas.")
        print(f"Periódica - Anual: {atualizadas['anual']} obrigações atualizadas.")
        print("Concluído.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
