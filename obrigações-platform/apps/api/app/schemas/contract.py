from pydantic import BaseModel, ConfigDict


from datetime import datetime


class ContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None = None
    signed_at: datetime | None = None