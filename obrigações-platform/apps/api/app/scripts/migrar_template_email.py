"""Adiciona colunas email_assunto e email_corpo à tabela app_settings."""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dev.db')

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

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for col, val in [('email_assunto', ASSUNTO_PADRAO), ('email_corpo', CORPO_PADRAO)]:
    try:
        cur.execute(f"ALTER TABLE app_settings ADD COLUMN {col} TEXT")
        print(f"Coluna '{col}' adicionada.")
    except Exception:
        print(f"Coluna '{col}' já existe, pulando.")
    cur.execute(f"UPDATE app_settings SET {col} = ? WHERE {col} IS NULL", (val,))

conn.commit()
conn.close()
print("Migração concluída.")
