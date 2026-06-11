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

    # lembrete manual / pontual
    manual_reminder_at = Column(DateTime, nullable=True)
    manual_reminder_sent_at = Column(DateTime, nullable=True)

    # recorrência
    recurrence_mode = Column(String(20), nullable=True)
    recurrence_time = Column(String(5), nullable=True)
    recurrence_interval_days = Column(Integer, nullable=True)
    recurrence_weekday = Column(Integer, nullable=True)
    recurrence_day_of_month = Column(Integer, nullable=True)
    recurrence_month = Column(Integer, nullable=True)

    # resultado final calculado
    next_recurrence_at = Column(DateTime, nullable=True)
    next_reminder_at = Column(DateTime, nullable=True)
    last_email_sent_at = Column(DateTime, nullable=True)

    status_envio = Column(String(50), nullable=True)

    trigger_family = Column(String(50), nullable=True)
    trigger_type = Column(String(100), nullable=True)
    condition_raw = Column(Text, nullable=True)
    condition_canonical = Column(String(255), nullable=True)
    condition_status = Column(String(50), nullable=True, default="pendente")

    obligation_code = Column(String(20), nullable=True, index=True)
    contract_phase = Column(Text, nullable=True)
    trigger_category = Column(Text, nullable=True)
    compliance_logic = Column(String(50), nullable=True)
    trigger_source = Column(Text, nullable=True)
    internal_inputs = Column(Text, nullable=True)
    external_inputs = Column(Text, nullable=True)
    depends_on_clauses = Column(Text, nullable=True)
    is_input_for_clauses = Column(Text, nullable=True)
    deadline_type = Column(String(50), nullable=True)
    deadline_value = Column(Text, nullable=True)
    deadline_text = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    interpretive_notes = Column(Text, nullable=True)

    pagina_contrato = Column(Integer, nullable=True)

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

    dependency_entries = relationship(
        "ObligationDependency",
        foreign_keys="[ObligationDependency.eventual_id]",
        backref="eventual_obligation",
        lazy="select",
    )

    condition_for_entries = relationship(
        "ObligationDependency",
        foreign_keys="[ObligationDependency.condition_id]",
        backref="condition_obligation",
        lazy="select",
    )

    @property
    def has_dependency(self) -> bool:
        return len(self.dependency_entries) > 0

    @property
    def is_condition_for_count(self) -> int:
        return len(self.condition_for_entries)