from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.excel_importer import importar_planilha_substituindo_base

router = APIRouter()


@router.post("/spreadsheet/replace")
async def replace_spreadsheet(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo inválido")

    filename = file.filename.lower()
    if not filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Envie um arquivo .xlsx ou .xls",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Arquivo vazio",
        )

    return importar_planilha_substituindo_base(
        db=db,
        arquivo_bytes=content,
        nome_arquivo=file.filename,
    )