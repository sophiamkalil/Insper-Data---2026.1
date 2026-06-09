from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SettingsRead(BaseModel):
    email_escritorio: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SettingsUpdate(BaseModel):
    email_escritorio: str | None = None
