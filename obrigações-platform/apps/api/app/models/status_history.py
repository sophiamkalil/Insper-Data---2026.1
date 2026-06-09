from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ObligationStatusHistory(Base):
    __tablename__ = "obligation_status_history"

    id = Column(Integer, primary_key=True, index=True)
    obligation_id = Column(Integer, ForeignKey("obligations.id"), nullable=False, index=True)

    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)

    changed_at = Column(DateTime, server_default=func.now(), nullable=False)

    obligation = relationship("Obligation", back_populates="history")