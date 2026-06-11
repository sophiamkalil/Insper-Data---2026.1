from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from app.db.base import Base


class ObligationDependency(Base):
    __tablename__ = "obligation_dependencies"

    id = Column(Integer, primary_key=True)
    eventual_id = Column(Integer, ForeignKey("obligations.id"), nullable=False)
    condition_id = Column(Integer, ForeignKey("obligations.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("eventual_id", "condition_id", name="uq_dep_pair"),
    )
