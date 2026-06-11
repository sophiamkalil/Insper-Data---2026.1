import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


def enviar_email(destinatario: str, assunto: str, mensagem: str) -> None:
    remetente = os.getenv("EMAIL_REMETENTE", "alertas.contratuais@gmail.com")
    senha = os.getenv("EMAIL_SENHA", "")

    if not senha:
        raise RuntimeError("EMAIL_SENHA não definido nas variáveis de ambiente.")

    msg = MIMEText(mensagem, 'plain', 'utf-8')
    msg["Subject"] = Header(assunto, 'utf-8')
    msg["From"] = remetente
    msg["To"] = destinatario

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remetente, senha)
        server.send_message(msg)