from pydantic import BaseModel, ConfigDict


class ContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None = None