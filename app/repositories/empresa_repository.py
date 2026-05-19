from app.database.connection import get_connection


CAMPOS_EMPRESA = [
    "razao_social",
    "nome_fantasia",
    "cnpj",
    "inscricao_estadual",
    "inscricao_municipal",
    "mei",
    "cnae",
    "atividade_principal",
    "responsavel",
    "cpf_responsavel",
    "telefone",
    "email",
    "cep",
    "endereco",
    "numero",
    "complemento",
    "bairro",
    "cidade",
    "uf",
    "observacoes",
    "ativo",
]


def obter_empresa_ativa():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM empresas_sistema
        WHERE ativo = 1
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_empresas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM empresas_sistema
        ORDER BY ativo DESC, nome_fantasia ASC, id DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def salvar_empresa(data):
    """Cria ou atualiza a empresa ativa do sistema.

    O software está preparado para MEI e pequenos negócios. Nesta etapa,
    trabalhamos com uma empresa ativa principal para alimentar cabeçalho,
    relatórios e configurações do sistema.
    """
    dados = {campo: data.get(campo) for campo in CAMPOS_EMPRESA}
    dados["nome_fantasia"] = (dados.get("nome_fantasia") or "").strip()
    dados["razao_social"] = (dados.get("razao_social") or "").strip()
    dados["mei"] = 1 if dados.get("mei") in (1, True, "1", "Sim", "sim") else 0
    dados["ativo"] = 1

    if not dados["nome_fantasia"]:
        raise ValueError("O nome fantasia é obrigatório.")

    empresa_id = data.get("id")
    conn = get_connection()
    cursor = conn.cursor()

    if empresa_id:
        set_clause = ", ".join([f"{campo} = ?" for campo in CAMPOS_EMPRESA])
        valores = [dados[campo] for campo in CAMPOS_EMPRESA]
        valores.append(empresa_id)
        cursor.execute(f"""
            UPDATE empresas_sistema
            SET {set_clause}, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, valores)
        novo_id = int(empresa_id)
    else:
        # Nesta versão, mantém apenas uma empresa ativa principal.
        cursor.execute("UPDATE empresas_sistema SET ativo = 0 WHERE ativo = 1")
        campos = ", ".join(CAMPOS_EMPRESA)
        placeholders = ", ".join(["?"] * len(CAMPOS_EMPRESA))
        valores = [dados[campo] for campo in CAMPOS_EMPRESA]
        cursor.execute(f"""
            INSERT INTO empresas_sistema ({campos})
            VALUES ({placeholders})
        """, valores)
        novo_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return novo_id


def limpar_empresa_ativa():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE empresas_sistema SET ativo = 0 WHERE ativo = 1")
    conn.commit()
    alteradas = cursor.rowcount
    conn.close()
    return alteradas
