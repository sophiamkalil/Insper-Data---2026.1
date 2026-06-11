"""
Mapeia automaticamente item_number das obrigações para a página do PDF do contrato.
Execução única: python -m app.scripts.mapear_paginas_contrato
"""
import os
import re
import sqlite3

import pdfplumber

PDF_PATH = os.path.join(os.path.expanduser('~'), 'front-concessoes', 'public', 'contrato.pdf')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'dev.db')


def build_clause_index(pdf_path: str) -> dict[str, int]:
    """Retorna {clausula: primeira_pagina}, ex: {"5.3": 22, "11.6": 45}."""
    index: dict[str, int] = {}
    # Padrões em ordem de confiança (mais específico primeiro)
    patterns = [
        # Exatamente no início da linha: "5.3." ou "5.3 "
        r'(?m)^(\d+\.\d+(?:\.\d+)*)\s*[.\s]',
        # Com até 4 espaços de recuo: "  5.3." (itens indentados)
        r'(?m)^\s{1,4}(\d+\.\d+(?:\.\d+)*)\s*[.\s]',
    ]
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ''
            for pattern in patterns:
                for m in re.findall(pattern, text):
                    if m not in index:
                        index[m] = page_num
    return index


def primary_clause(item_number: str) -> str | None:
    """Extrai a primeira cláusula numérica de um item_number.

    "11.6 (i) e 35.1"  → "11.6"
    "12.8.2.2"          → "12.8.2.2"
    "4. do Apêndice D"  → None
    """
    if not item_number:
        return None
    m = re.search(r'\d+\.\d+(?:\.\d+)*', item_number)
    return m.group(0) if m else None


def fallback_clauses(clausula: str) -> list[str]:
    """Gera cláusulas de fallback mais gerais caso a específica não seja encontrada.
    "12.8.2.2" → ["12.8.2", "12.8"]
    """
    parts = clausula.split('.')
    fallbacks = []
    for i in range(len(parts) - 1, 1, -1):
        fallbacks.append('.'.join(parts[:i]))
    return fallbacks


def main():
    pdf_path = os.path.abspath(PDF_PATH)
    db_path = os.path.abspath(DB_PATH)

    if not os.path.exists(pdf_path):
        print(f"PDF não encontrado: {pdf_path}")
        return
    if not os.path.exists(db_path):
        print(f"Banco não encontrado: {db_path}")
        return

    print(f"Lendo PDF: {pdf_path}")
    index = build_clause_index(pdf_path)
    print(f"Cláusulas encontradas no PDF: {len(index)}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    obrigacoes = cur.execute(
        'SELECT id, item_number FROM obligations WHERE item_number IS NOT NULL'
    ).fetchall()

    atualizados = nao_encontrados = 0
    nao_encontrados_lista = []

    for oid, item_num in obrigacoes:
        clausula = primary_clause(item_num)
        if not clausula:
            nao_encontrados += 1
            nao_encontrados_lista.append(item_num)
            continue

        pagina = index.get(clausula)
        if pagina is None:
            for fb in fallback_clauses(clausula):
                pagina = index.get(fb)
                if pagina:
                    break

        if pagina:
            cur.execute(
                'UPDATE obligations SET pagina_contrato = ? WHERE id = ?',
                (pagina, oid)
            )
            atualizados += 1
        else:
            nao_encontrados += 1
            nao_encontrados_lista.append(item_num)

    conn.commit()
    conn.close()

    print(f"\nResultado:")
    print(f"  Atualizados:    {atualizados}")
    print(f"  Não encontrados: {nao_encontrados}")
    if nao_encontrados_lista:
        print(f"\nItens sem página mapeada (defina manualmente no detalhe da obrigação):")
        for item in sorted(set(nao_encontrados_lista))[:20]:
            print(f"  {item}")
        if len(nao_encontrados_lista) > 20:
            print(f"  ... e mais {len(nao_encontrados_lista) - 20}")


if __name__ == '__main__':
    main()
