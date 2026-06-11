from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.settings import AppSettings
from app.schemas.settings import SettingsRead, SettingsUpdate

router = APIRouter()


def _get_or_create(db: Session) -> AppSettings:
    row = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if row is None:
        row = AppSettings(id=1)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@router.get("", response_model=SettingsRead)
def get_settings(db: Session = Depends(get_db)):
    return _get_or_create(db)


@router.patch("", response_model=SettingsRead)
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    row = _get_or_create(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    from app.services.lembretes_prazo import aplicar_lembretes_por_prazo
    aplicar_lembretes_por_prazo(db)
    return row
