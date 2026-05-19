from app.database.connection import get_connection


def listar_clientes(limite=1000, offset=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, documento, telefone, email, endereco, observacoes, ativo, criado_em
        FROM clientes
        ORDER BY nome ASC
        LIMIT ? OFFSET ?
    """, (limite, offset))
    rows = cursor.fetchall()
    conn.close()
    return rows


def buscar_clientes(termo, limite=1000, offset=0):
    conn = get_connection()
    cursor = conn.cursor()
    termo_busca = f"%{termo}%"
    cursor.execute("""
        SELECT id, nome, documento, telefone, email, endereco, observacoes, ativo, criado_em
        FROM clientes
        WHERE nome LIKE ? OR documento LIKE ? OR telefone LIKE ? OR email LIKE ?
        ORDER BY nome ASC
        LIMIT ? OFFSET ?
    """, (termo_busca, termo_busca, termo_busca, termo_busca, limite, offset))
    rows = cursor.fetchall()
    conn.close()
    return rows


def cadastrar_cliente(nome, documento="", telefone="", email="", endereco="", observacoes="", ativo=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (nome, documento, telefone, email, endereco, observacoes, ativo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, documento, telefone, email, endereco, observacoes, int(ativo)))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_cliente(id_cliente, nome, documento="", telefone="", email="", endereco="", observacoes="", ativo=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clientes
        SET nome = ?, documento = ?, telefone = ?, email = ?, endereco = ?, observacoes = ?, ativo = ?
        WHERE id = ?
    """, (nome, documento, telefone, email, endereco, observacoes, int(ativo), id_cliente))
    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok


def excluir_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM lancamentos_financeiros WHERE pessoa_tipo = 'cliente' AND pessoa_id = ?", (id_cliente,))
    possui_lancamentos = cursor.fetchone()[0] > 0
    if possui_lancamentos:
        cursor.execute("UPDATE clientes SET ativo = 0 WHERE id = ?", (id_cliente,))
    else:
        cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok, possui_lancamentos
