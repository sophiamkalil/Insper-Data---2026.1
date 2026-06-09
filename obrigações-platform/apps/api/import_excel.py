import pandas as pd

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.contract import Contract
from app.models.obligation import Obligation
import app.models  # noqa: F401


FILE_PATH = "../../data/PV_ASP_Obrigações_ContratodeConcessao_20251218 (versao inicial).xlsx"

def normalize(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def main():
    Base.metadata.create_all(bind=engine)

    df = pd.read_excel(FILE_PATH)

    db = SessionLocal()

    try:
        contract = db.query(Contract).filter(
            Contract.code == "PV-ASP-001"
        ).first()

        if not contract:
            contract = Contract(
                name="Contrato de Concessão PV ASP",
                code="PV-ASP-001",
                description="Importação inicial da planilha base",
            )

            db.add(contract)
            db.flush()

        for idx, row in df.iterrows():
            obligation = Obligation(
                contract_id=contract.id,
                document_name=normalize(row.get("Documento")),
                item_number=normalize(row.get("Item")),
                recurrence=normalize(row.get("Recorrência")),
                obligation_text=normalize(row.get("Obrigação")) or "",
                observations=normalize(row.get("Observações")),
                status="pending",
                source_row=idx + 2,
            )

            db.add(obligation)

        db.commit()

        print(f"{len(df)} obrigações importadas com sucesso.")

    finally:
        db.close()


if __name__ == "__main__":
    main()