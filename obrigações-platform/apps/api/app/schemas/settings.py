from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email_escritorio: str | None = None
    antecedencia_mensal_dias: int = 7
    antecedencia_anual_dias: int = 30
    antecedencia_encerramento_dias: int = 180
    frequencia_mensal_dias: int = 3
    frequencia_anual_dias: int = 7
    frequencia_encerramento_dias: int = 30
    email_assunto: str | None = None
    email_corpo: str | None = None


class SettingsUpdate(BaseModel):
    email_escritorio: str | None = None
    antecedencia_mensal_dias: int | None = None
    antecedencia_anual_dias: int | None = None
    antecedencia_encerramento_dias: int | None = None
    frequencia_mensal_dias: int | None = None
    frequencia_anual_dias: int | None = None
    frequencia_encerramento_dias: int | None = None
    email_assunto: str | None = None
    email_corpo: str | None = None
