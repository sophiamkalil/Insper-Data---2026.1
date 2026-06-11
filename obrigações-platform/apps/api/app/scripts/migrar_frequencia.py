"""Adiciona colunas de frequência por tipo à tabela app_settings."""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dev.db')

COLUNAS = [
    ('frequencia_mensal_dias', 3),
    ('frequencia_anual_dias', 7),
    ('frequencia_encerramento_dias', 30),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for col, default in COLUNAS:
    try:
        cur.execute(f"ALTER TABLE app_settings ADD COLUMN {col} INTEGER DEFAULT {default}")
        print(f"Coluna '{col}' adicionada.")
    except Exception:
        print(f"Coluna '{col}' já existe, pulando.")
    cur.execute(f"UPDATE app_settings SET {col} = ? WHERE {col} IS NULL", (default,))

conn.commit()
conn.close()
print("Migração concluída.")
