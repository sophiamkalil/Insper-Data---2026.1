"""
Resolve dependências entre obrigações eventuais e suas obrigações-condição,
cruzando Depende_de_Cláusulas (números de cláusula) com o campo item_number.

Uso:
    python -m app.scripts.resolve_dependencies
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.db.session import SessionLocal
from app.models.obligation import Obligation
from app.models.obligation_dependency import ObligationDependency


def _extrair_numeros_clausula(texto: str) -> list[str]:
    """Extrai números de cláusula de um texto como 'cl. 14.1 operação; cl. 33.6 conta'."""
    if not texto or texto.strip() in ("—", "\x97", "—"):
        return []
    # Captura o número logo após "cl." ou "cláusula" — ex: "14.1", "7.1", "16.1 (xix)"
    matches = re.findall(r'cl\.\s*([\d]+\.[\d.]+(?:\s*\([^)]+\))?)', texto, re.IGNORECASE)
    # Normaliza: pega apenas a parte numérica base (ex: "14.1" de "14.1 (xix)")
    numeros = []
    for m in matches:
        base = re.match(r'([\d]+\.[\d.]+)', m.strip())
        if base:
            numeros.append(base.group(1).rstrip('.'))
    return numeros


def resolve_dependencies() -> None:
    db = SessionLocal()
    try:
        eventuais = (
            db.query(Obligation)
            .filter(Obligation.recurrence.ilike("Eventual%"))
            .all()
        )

        inseridos = 0
        nao_encontrados: list[str] = []

        for eventual in eventuais:
            numeros = _extrair_numeros_clausula(eventual.depends_on_clauses or "")
            if not numeros:
                continue

            for num in numeros:
                # Busca por item_number que começa com esse número
                condicao = (
                    db.query(Obligation)
                    .filter(
                        Obligation.item_number.ilike(f"{num}%"),
                        Obligation.id != eventual.id,
                    )
                    .first()
                )

                if condicao:
                    existing = (
                        db.query(ObligationDependency)
                        .filter(
                            ObligationDependency.eventual_id == eventual.id,
                            ObligationDependency.condition_id == condicao.id,
                        )
                        .first()
                    )
                    if not existing:
                        dep = ObligationDependency(
                            eventual_id=eventual.id,
                            condition_id=condicao.id,
                        )
                        db.add(dep)
                        inseridos += 1
                        print(
                            f"  {eventual.obligation_code} -> {condicao.obligation_code} "
                            f"(cl. {num} = item {condicao.item_number})"
                        )
                else:
                    nao_encontrados.append(
                        f"{eventual.obligation_code}: cl. {num} (sem correspondência)"
                    )

        db.commit()
        print(f"\nConcluído: {inseridos} dependências criadas.")
        if nao_encontrados:
            print(f"\nCláusulas sem obrigação correspondente ({len(nao_encontrados)}):")
            for msg in nao_encontrados:
                print(f"  {msg}")
    finally:
        db.close()


if __name__ == "__main__":
    resolve_dependencies()
