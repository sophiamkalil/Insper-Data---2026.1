"""
Mapeia automaticamente item_number das obrigações para a página do PDF correspondente.
Execução única: python -m app.scripts.mapear_paginas_contrato

Processa todos os documentos com PDF disponível em ~/front-concessoes/public/.
"""
import os
import re
import sqlite3

import pdfplumber

PDF_DIR = os.path.join(os.path.expanduser('~'), 'front-concessoes', 'public')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'dev.db')

DOCUMENTOS_PDF = {
    'Contrato': 'contrato.pdf',
    'Anexo 1 - Regulamento da Concessão': 'anexo1.pdf',
    'Anexo 2 - Plano de Exploração Aeroportuária (PEA)': 'anexo2.pdf',
    'Anexo 4 - Plano de Transferência Operacional (PTO)': 'anexo4.pdf',
    'Anexo 5 - Tarifas Aeroportuárias': 'anexo5.pdf',
    'Anexo 6 - Contrato de Administração de Contas': 'anexo6.pdf',
    'Anexo 8 - Termo de Aceitação e Permissão de Uso de Ativos': 'anexo8.pdf',
    'Anexo 17 - Caderno de Penalidades': 'anexo17.pdf',
}


def build_clause_index(pdf_path: str) -> dict[str, int]:
    """Retorna {clausula: primeira_pagina}, ex: {"5.3": 22, "11.6": 45}."""
    index: dict[str, int] = {}
    patterns = [
        r'(?m)^(\d+\.\d+(?:\.\d+)*)\s*[.\s]',
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
    if not item_number:
        return None
    m = re.search(r'\d+\.\d+(?:\.\d+)*', item_number)
    return m.group(0) if m else None


def fallback_clauses(clausula: str) -> list[str]:
    parts = clausula.split('.')
    return ['.'.join(parts[:i]) for i in range(len(parts) - 1, 1, -1)]


def processar_documento(doc_name: str, pdf_filename: str, conn: sqlite3.Connection) -> None:
    pdf_path = os.path.abspath(os.path.join(PDF_DIR, pdf_filename))

    if not os.path.exists(pdf_path):
        print(f'  [ignorado] PDF não encontrado: {pdf_path}')
        return

    print(f'  Lendo PDF: {pdf_path}')
    index = build_clause_index(pdf_path)
    print(f'  Cláusulas encontradas: {len(index)}')

    cur = conn.cursor()
    obrigacoes = cur.execute(
        'SELECT id, item_number FROM obligations WHERE item_number IS NOT NULL AND document_name = ?',
        (doc_name,)
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
            cur.execute('UPDATE obligations SET pagina_contrato = ? WHERE id = ?', (pagina, oid))
            atualizados += 1
        else:
            nao_encontrados += 1
            nao_encontrados_lista.append(item_num)

    conn.commit()
    print(f'  Atualizados: {atualizados} | Não encontrados: {nao_encontrados}')
    if nao_encontrados_lista:
        for item in sorted(set(nao_encontrados_lista))[:10]:
            print(f'    - {item}')
        if len(nao_encontrados_lista) > 10:
            print(f'    ... e mais {len(nao_encontrados_lista) - 10}')


def main():
    db_path = os.path.abspath(DB_PATH)
    if not os.path.exists(db_path):
        print(f'Banco não encontrado: {db_path}')
        return

    conn = sqlite3.connect(db_path)

    for doc_name, pdf_filename in DOCUMENTOS_PDF.items():
        print(f'\n[{doc_name}]')
        processar_documento(doc_name, pdf_filename, conn)

    conn.close()
    print('\nMapeamento concluído.')


if __name__ == '__main__':
    main()
