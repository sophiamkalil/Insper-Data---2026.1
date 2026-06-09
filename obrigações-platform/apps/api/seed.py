from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.contract import Contract
from app.models.obligation import Obligation
import app.models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Contract).count() == 0:
            contract = Contract(
                name="Modelo Base - Concessão",
                code="BASE-001",
                description="Contrato inicial para validar a plataforma",
            )
            db.add(contract)
            db.flush()

            obligations = [
                Obligation(
                    contract_id=contract.id,
                    document_name="Documento Modelo",
                    item_number="1",
                    recurrence="Mensal",
                    obligation_text="Enviar relatório operacional mensal.",
                    observations="Exemplo inicial para validar a tela.",
                    status="pending",
                    responsible="Equipe Operacional",
                    source_row=1,
                ),
                Obligation(
                    contract_id=contract.id,
                    document_name="Documento Modelo",
                    item_number="2",
                    recurrence="Anual",
                    obligation_text="Apresentar prestação de contas anual.",
                    observations=None,
                    status="completed",
                    responsible="Financeiro",
                    source_row=2,
                ),
            ]
            db.add_all(obligations)
            db.commit()
            print("Seed criado com sucesso.")
        else:
            print("Banco já possui contratos. Nada a fazer.")
    finally:
        db.close()


if __name__ == "__main__":
    main()