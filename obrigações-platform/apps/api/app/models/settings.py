from sqlalchemy import Column, Integer, String

from app.db.base import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, default=1)
    email_escritorio = Column(String(255), nullable=True)
