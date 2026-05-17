from app.database.connection import get_connection


def listar_fornecedores(limite=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, documento, telefone, email, criado_em
        FROM fornecedores
        ORDER BY nome ASC
        LIMIT ? OFFSET ?
    """, (limite, offset))

    fornecedores = cursor.fetchall()
    conn.close()

    return fornecedores


def buscar_fornecedores(termo, limite=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    termo_busca = f"%{termo}%"

    cursor.execute("""
        SELECT id, nome, documento, telefone, email, criado_em
        FROM fornecedores
        WHERE nome LIKE ?
           OR documento LIKE ?
           OR telefone LIKE ?
           OR email LIKE ?
        ORDER BY nome ASC
        LIMIT ? OFFSET ?
    """, (termo_busca, termo_busca, termo_busca, termo_busca, limite, offset))

    fornecedores = cursor.fetchall()
    conn.close()

    return fornecedores


def contar_fornecedores():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM fornecedores")
    total = cursor.fetchone()[0]

    conn.close()

    return total


def contar_fornecedores_por_busca(termo):
    conn = get_connection()
    cursor = conn.cursor()

    termo_busca = f"%{termo}%"

    cursor.execute("""
        SELECT COUNT(*)
        FROM fornecedores
        WHERE nome LIKE ?
           OR documento LIKE ?
           OR telefone LIKE ?
           OR email LIKE ?
    """, (termo_busca, termo_busca, termo_busca, termo_busca))

    total = cursor.fetchone()[0]
    conn.close()

    return total


def cadastrar_fornecedor(nome, documento="", telefone="", email=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO fornecedores (nome, documento, telefone, email)
        VALUES (?, ?, ?, ?)
    """, (nome, documento, telefone, email))

    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return novo_id


def atualizar_fornecedor(id_fornecedor, nome, documento="", telefone="", email=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE fornecedores
        SET nome = ?, documento = ?, telefone = ?, email = ?
        WHERE id = ?
    """, (nome, documento, telefone, email, id_fornecedor))

    conn.commit()
    linhas_afetadas = cursor.rowcount
    conn.close()

    return linhas_afetadas > 0


def excluir_fornecedor(id_fornecedor):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM fornecedores
        WHERE id = ?
    """, (id_fornecedor,))

    conn.commit()
    linhas_afetadas = cursor.rowcount
    conn.close()

    return linhas_afetadas > 0