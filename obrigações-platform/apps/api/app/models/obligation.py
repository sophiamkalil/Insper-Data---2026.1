from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False,
        index=True,
    )

    document_name = Column(String(255), nullable=True)
    item_number = Column(String(100), nullable=True)
    recurrence = Column(String(100), nullable=True)

    obligation_text = Column(Text, nullable=False)
    observations = Column(Text, nullable=True)

    status = Column(String(50), nullable=False, default="pending")
    responsible = Column(String(255), nullable=True)
    deadline = Column(DateTime, nullable=True)
    source_row = Column(Integer, nullable=True)

    email_enabled = Column(Boolean, nullable=False, default=False)
    email_destino = Column(String(255), nullable=True)
    data_envio_email = Column(DateTime, nullable=True)
    status_envio = Column(String(50), nullable=True)
    last_email_sent_at = Column(DateTime, nullable=True)

    trigger_family = Column(String(50), nullable=True)
    trigger_type = Column(String(100), nullable=True)
    condition_raw = Column(Text, nullable=True)
    condition_canonical = Column(String(255), nullable=True)
    condition_status = Column(String(50), nullable=True, default="pendente")

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contract = relationship(
        "Contract",
        back_populates="obligations",
    )

    history = relationship(
        "ObligationStatusHistory",
        back_populates="obligation",
        cascade="all, delete-orphan",
    )