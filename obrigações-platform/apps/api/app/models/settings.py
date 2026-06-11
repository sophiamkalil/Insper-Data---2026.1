from sqlalchemy import Column, Integer, String, Text

from app.db.base import Base

ASSUNTO_PADRAO = "Alerta: obrigação próxima do prazo"
CORPO_PADRAO = (
    "Olá,\n\n"
    "Segue um lembrete automático de obrigação contratual.\n\n"
    "Recorrência: {tipo}\n"
    "Documento: {documento}\n"
    "Item: {item}\n"
    "Obrigação: {obrigacao}\n"
    "Próximo lembrete: {prazo}\n"
    "Status atual: {status}\n\n"
    "Verifique e tome as providências necessárias."
)


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, default=1)
    email_escritorio = Column(String(255), nullable=True)
    antecedencia_mensal_dias = Column(Integer, nullable=False, default=7, server_default='7')
    antecedencia_anual_dias = Column(Integer, nullable=False, default=30, server_default='30')
    antecedencia_encerramento_dias = Column(Integer, nullable=False, default=180, server_default='180')
    frequencia_mensal_dias = Column(Integer, nullable=False, default=3, server_default='3')
    frequencia_anual_dias = Column(Integer, nullable=False, default=7, server_default='7')
    frequencia_encerramento_dias = Column(Integer, nullable=False, default=30, server_default='30')
    email_assunto = Column(Text, nullable=True, default=ASSUNTO_PADRAO, server_default=ASSUNTO_PADRAO)
    email_corpo = Column(Text, nullable=True, default=CORPO_PADRAO, server_default=CORPO_PADRAO)
