from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractRead

router = APIRouter()


@router.get("/", response_model=list[ContractRead])
def list_contracts(db: Session = Depends(get_db)):
    return db.query(Contract).order_by(Contract.id.asc()).all()