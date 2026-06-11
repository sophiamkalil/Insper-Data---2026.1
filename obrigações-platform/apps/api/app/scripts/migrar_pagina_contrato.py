"""Adiciona coluna pagina_contrato à tabela obligations."""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dev.db')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE obligations ADD COLUMN pagina_contrato INTEGER")
    print("Coluna 'pagina_contrato' adicionada.")
except Exception:
    print("Coluna 'pagina_contrato' já existe, pulando.")

conn.commit()
conn.close()
print("Migração concluída.")
