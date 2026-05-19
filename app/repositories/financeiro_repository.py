from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from app.database.connection import get_connection
from app.database.schema import CATEGORIAS_PADRAO


TIPOS_LANCAMENTO = ["receita", "despesa", "custo", "transferencia"]
STATUS_LANCAMENTO = ["pago", "recebido", "pendente", "vencido", "cancelado"]
STATUS_REALIZADOS = ("pago", "recebido")


def _to_float(valor):
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(Decimal(texto or "0"))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Valor monetário inválido: {valor}")


def _today_iso():
    return date.today().isoformat()


def _normalizar_status(tipo, status):
    status = status or "pendente"
    if tipo == "receita" and status == "pago":
        return "recebido"
    if tipo in ("despesa", "custo") and status == "recebido":
        return "pago"
    if tipo == "transferencia" and status == "recebido":
        return "pago"
    return status


def _safe_int(value):
    if value in (None, "", 0, "0"):
        return None
    return int(value)


def _row_to_dict(row):
    return dict(row) if row is not None else None


def listar_pessoas(tipo=None, ativas_apenas=True):
    """Lista pessoas para vínculo do lançamento: clientes e/ou fornecedores."""
    conn = get_connection()
    cursor = conn.cursor()
    pessoas = []

    tabelas = []
    if tipo in (None, "cliente"):
        tabelas.append(("cliente", "clientes"))
    if tipo in (None, "fornecedor"):
        tabelas.append(("fornecedor", "fornecedores"))

    for pessoa_tipo, tabela in tabelas:
        where = "WHERE ativo = 1" if ativas_apenas else ""
        cursor.execute(f"""
            SELECT id, nome, documento, telefone, email, ativo, criado_em
            FROM {tabela}
            {where}
            ORDER BY nome ASC
        """)
        for row in cursor.fetchall():
            item = dict(row)
            item["pessoa_tipo"] = pessoa_tipo
            pessoas.append(item)

    conn.close()
    return sorted(pessoas, key=lambda p: (p["pessoa_tipo"], p["nome"] or ""))


def listar_contas_financeiras(ativas_apenas=False):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT
            cf.id,
            cf.nome,
            cf.tipo,
            cf.saldo_inicial,
            cf.data_saldo_inicial,
            cf.observacoes,
            cf.ativo,
            cf.criado_em,
            cf.saldo_inicial + COALESCE((
                SELECT SUM(valor_movimento)
                FROM (
                    SELECT
                        CASE
                            WHEN lf.tipo = 'receita' AND lf.status IN ('pago', 'recebido') THEN lf.valor
                            WHEN lf.tipo IN ('despesa', 'custo') AND lf.status IN ('pago', 'recebido') THEN -lf.valor
                            ELSE 0
                        END AS valor_movimento
                    FROM lancamentos_financeiros lf
                    WHERE lf.conta_financeira_id = cf.id
                      AND lf.status IN ('pago', 'recebido')
                      AND lf.tipo IN ('receita', 'despesa', 'custo')

                    UNION ALL

                    SELECT -lf.valor AS valor_movimento
                    FROM lancamentos_financeiros lf
                    WHERE lf.conta_origem_id = cf.id
                      AND lf.status IN ('pago', 'recebido')
                      AND lf.tipo = 'transferencia'

                    UNION ALL

                    SELECT lf.valor AS valor_movimento
                    FROM lancamentos_financeiros lf
                    WHERE lf.conta_destino_id = cf.id
                      AND lf.status IN ('pago', 'recebido')
                      AND lf.tipo = 'transferencia'
                ) movimentos
            ), 0) AS saldo_atual
        FROM contas_financeiras cf
    """

    params = []
    if ativas_apenas:
        sql += " WHERE cf.ativo = 1 "

    sql += " ORDER BY cf.nome ASC"

    cursor.execute(sql, params)
    contas = cursor.fetchall()
    conn.close()
    return contas


def buscar_contas_financeiras(termo):
    contas = listar_contas_financeiras(ativas_apenas=False)
    termo = (termo or "").lower()
    return [c for c in contas if termo in (c["nome"] or "").lower() or termo in (c["tipo"] or "").lower()]


def obter_saldo_conta(conta_id):
    conta_id = int(conta_id)
    for conta in listar_contas_financeiras():
        if conta["id"] == conta_id:
            return float(conta["saldo_atual"] or 0)
    return 0.0


def cadastrar_conta_financeira(nome, tipo="banco", saldo_inicial=0.0, data_saldo_inicial=None, observacoes="", ativo=1):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contas_financeiras (nome, tipo, saldo_inicial, data_saldo_inicial, observacoes, ativo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, tipo, _to_float(saldo_inicial), data_saldo_inicial, observacoes, int(ativo)))

    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_conta_financeira(id_conta, nome, tipo="banco", saldo_inicial=0.0, data_saldo_inicial=None, observacoes="", ativo=1):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE contas_financeiras
        SET nome = ?, tipo = ?, saldo_inicial = ?, data_saldo_inicial = ?, observacoes = ?, ativo = ?
        WHERE id = ?
    """, (nome, tipo, _to_float(saldo_inicial), data_saldo_inicial, observacoes, int(ativo), id_conta))

    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok


def excluir_conta_financeira(id_conta):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM lancamentos_financeiros
        WHERE conta_financeira_id = ? OR conta_origem_id = ? OR conta_destino_id = ?
    """, (id_conta, id_conta, id_conta))
    possui_lancamentos = cursor.fetchone()[0] > 0

    if possui_lancamentos:
        cursor.execute("UPDATE contas_financeiras SET ativo = 0 WHERE id = ?", (id_conta,))
    else:
        cursor.execute("DELETE FROM contas_financeiras WHERE id = ?", (id_conta,))

    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok, possui_lancamentos


def listar_plano_contas(ativas_apenas=True):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT id, codigo, nome, tipo, codigo_pai, ativo, criado_em FROM plano_contas"
    if ativas_apenas:
        sql += " WHERE ativo = 1"
    sql += " ORDER BY codigo ASC"
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows


def listar_categorias_financeiras(tipo=None, ativas_apenas=False):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT id, nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza,
               plano_conta_id, incluir_relatorios, observacoes, ativo, criado_em
        FROM categorias_financeiras
        WHERE 1 = 1
    """
    params = []

    if tipo:
        sql += " AND tipo = ?"
        params.append(tipo)

    if ativas_apenas:
        sql += " AND ativo = 1"

    sql += " ORDER BY tipo ASC, nome ASC"

    cursor.execute(sql, params)
    categorias = cursor.fetchall()
    conn.close()
    return categorias


def buscar_categorias_financeiras(termo):
    conn = get_connection()
    cursor = conn.cursor()
    termo_busca = f"%{termo}%"

    cursor.execute("""
        SELECT id, nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza,
               plano_conta_id, incluir_relatorios, observacoes, ativo, criado_em
        FROM categorias_financeiras
        WHERE nome LIKE ? OR tipo LIKE ? OR grupo_dre LIKE ? OR grupo_dfc LIKE ? OR grupo_bp LIKE ?
        ORDER BY tipo ASC, nome ASC
    """, (termo_busca, termo_busca, termo_busca, termo_busca, termo_busca))

    categorias = cursor.fetchall()
    conn.close()
    return categorias


def cadastrar_categoria_financeira(nome, tipo, grupo_dre="", grupo_dfc="", grupo_bp="", natureza="neutra", plano_conta_id=None, incluir_relatorios=1, observacoes="", ativo=1):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO categorias_financeiras (
            nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza, plano_conta_id,
            incluir_relatorios, observacoes, ativo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza, _safe_int(plano_conta_id), int(incluir_relatorios), observacoes, int(ativo)))

    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_categoria_financeira(id_categoria, nome, tipo, grupo_dre="", grupo_dfc="", grupo_bp="", natureza="neutra", plano_conta_id=None, incluir_relatorios=1, observacoes="", ativo=1):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE categorias_financeiras
        SET nome = ?, tipo = ?, grupo_dre = ?, grupo_dfc = ?, grupo_bp = ?, natureza = ?,
            plano_conta_id = ?, incluir_relatorios = ?, observacoes = ?, ativo = ?
        WHERE id = ?
    """, (nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza, _safe_int(plano_conta_id), int(incluir_relatorios), observacoes, int(ativo), id_categoria))

    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok


def restaurar_categorias_padrao_financeiras():
    """Recria/reactiva as categorias padrão usadas por DRE, BP, DFC e fluxo de caixa."""
    conn = get_connection()
    cursor = conn.cursor()
    inseridas = 0
    reativadas_ou_atualizadas = 0

    for nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza in CATEGORIAS_PADRAO:
        cursor.execute("""
            SELECT id, ativo
            FROM categorias_financeiras
            WHERE nome = ? AND tipo = ?
            LIMIT 1
        """, (nome, tipo))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE categorias_financeiras
                SET grupo_dre = ?, grupo_dfc = ?, grupo_bp = ?, natureza = ?,
                    incluir_relatorios = 1, ativo = 1
                WHERE id = ?
            """, (grupo_dre, grupo_dfc, grupo_bp, natureza, row["id"]))
            reativadas_ou_atualizadas += 1
        else:
            cursor.execute("""
                INSERT INTO categorias_financeiras (
                    nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza, incluir_relatorios, ativo
                )
                VALUES (?, ?, ?, ?, ?, ?, 1, 1)
            """, (nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza))
            inseridas += 1

    conn.commit()
    conn.close()
    return inseridas, reativadas_ou_atualizadas


def excluir_categoria_financeira(id_categoria):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM lancamentos_financeiros WHERE categoria_id = ?", (id_categoria,))
    possui_lancamentos = cursor.fetchone()[0] > 0

    if possui_lancamentos:
        cursor.execute("UPDATE categorias_financeiras SET ativo = 0 WHERE id = ?", (id_categoria,))
    else:
        cursor.execute("DELETE FROM categorias_financeiras WHERE id = ?", (id_categoria,))

    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok, possui_lancamentos


def listar_lancamentos(limite=500, termo="", filtros=None):
    filtros = filtros or {}
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT
            lf.id,
            lf.descricao,
            lf.tipo,
            lf.valor,
            lf.data_competencia,
            lf.data_vencimento,
            lf.data_movimento,
            lf.status,
            CASE
                WHEN lf.status = 'pendente'
                 AND lf.data_vencimento IS NOT NULL
                 AND lf.data_vencimento < date('now', 'localtime') THEN 'vencido'
                ELSE lf.status
            END AS status_calculado,
            lf.categoria_id,
            lf.conta_financeira_id,
            lf.conta_origem_id,
            lf.conta_destino_id,
            lf.forma_pagamento,
            lf.pessoa_tipo,
            lf.pessoa_id,
            lf.observacoes,
            lf.conciliado,
            lf.recorrencia_grupo,
            lf.parcela_atual,
            lf.parcela_total,
            lf.criado_em,
            cf.nome AS conta_nome,
            origem.nome AS conta_origem_nome,
            destino.nome AS conta_destino_nome,
            cat.nome AS categoria_nome,
            cat.grupo_dre AS grupo_dre,
            cat.grupo_dfc AS grupo_dfc,
            cat.grupo_bp AS grupo_bp,
            CASE
                WHEN lf.pessoa_tipo = 'cliente' THEN cli.nome
                WHEN lf.pessoa_tipo = 'fornecedor' THEN forn.nome
                ELSE ''
            END AS pessoa_nome
        FROM lancamentos_financeiros lf
        LEFT JOIN contas_financeiras cf ON cf.id = lf.conta_financeira_id
        LEFT JOIN contas_financeiras origem ON origem.id = lf.conta_origem_id
        LEFT JOIN contas_financeiras destino ON destino.id = lf.conta_destino_id
        LEFT JOIN categorias_financeiras cat ON cat.id = lf.categoria_id
        LEFT JOIN clientes cli ON cli.id = lf.pessoa_id AND lf.pessoa_tipo = 'cliente'
        LEFT JOIN fornecedores forn ON forn.id = lf.pessoa_id AND lf.pessoa_tipo = 'fornecedor'
        WHERE 1 = 1
    """
    params = []

    if termo:
        termo_busca = f"%{termo}%"
        sql += """
           AND (
                lf.descricao LIKE ?
                OR lf.tipo LIKE ?
                OR lf.status LIKE ?
                OR COALESCE(cf.nome, '') LIKE ?
                OR COALESCE(origem.nome, '') LIKE ?
                OR COALESCE(destino.nome, '') LIKE ?
                OR COALESCE(cat.nome, '') LIKE ?
                OR COALESCE(cli.nome, '') LIKE ?
                OR COALESCE(forn.nome, '') LIKE ?
           )
        """
        params.extend([termo_busca] * 9)

    if filtros.get("tipo"):
        sql += " AND lf.tipo = ?"
        params.append(filtros["tipo"])

    if filtros.get("status"):
        status = filtros["status"]
        if status == "vencido":
            sql += """
                AND lf.status = 'pendente'
                AND lf.data_vencimento IS NOT NULL
                AND lf.data_vencimento < date('now', 'localtime')
            """
        else:
            sql += " AND lf.status = ?"
            params.append(status)

    if filtros.get("conta_id"):
        sql += " AND (lf.conta_financeira_id = ? OR lf.conta_origem_id = ? OR lf.conta_destino_id = ?)"
        conta_id = filtros["conta_id"]
        params.extend([conta_id, conta_id, conta_id])

    if filtros.get("categoria_id"):
        sql += " AND lf.categoria_id = ?"
        params.append(filtros["categoria_id"])

    if filtros.get("pessoa_tipo") and filtros.get("pessoa_id"):
        sql += " AND lf.pessoa_tipo = ? AND lf.pessoa_id = ?"
        params.extend([filtros["pessoa_tipo"], filtros["pessoa_id"]])

    campo_data = filtros.get("campo_data") or "data_competencia"
    if campo_data not in ("data_competencia", "data_vencimento", "data_movimento"):
        campo_data = "data_competencia"

    if filtros.get("data_inicio"):
        sql += f" AND lf.{campo_data} >= ?"
        params.append(filtros["data_inicio"])
    if filtros.get("data_fim"):
        sql += f" AND lf.{campo_data} <= ?"
        params.append(filtros["data_fim"])

    sql += f" ORDER BY lf.{campo_data} DESC, lf.id DESC LIMIT ?"
    params.append(int(limite))

    cursor.execute(sql, params)
    lancamentos = cursor.fetchall()
    conn.close()
    return lancamentos


def obter_lancamento(id_lancamento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lancamentos_financeiros WHERE id = ?", (id_lancamento,))
    row = cursor.fetchone()
    conn.close()
    return row


def cadastrar_lancamento(
    descricao,
    tipo,
    valor,
    data_competencia,
    data_vencimento=None,
    data_movimento=None,
    status="pendente",
    categoria_id=None,
    conta_financeira_id=None,
    conta_origem_id=None,
    conta_destino_id=None,
    forma_pagamento="",
    pessoa_tipo="",
    pessoa_id=None,
    observacoes="",
    conciliado=0,
    recorrencia_grupo=None,
    parcela_atual=None,
    parcela_total=None,
):
    tipo = tipo or "despesa"
    status = _normalizar_status(tipo, status)
    data_vencimento = data_vencimento or data_competencia
    valor = _to_float(valor)

    if status not in STATUS_REALIZADOS:
        data_movimento = None

    if tipo == "transferencia":
        conta_financeira_id = None
        pessoa_tipo = ""
        pessoa_id = None
    else:
        conta_origem_id = None
        conta_destino_id = None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lancamentos_financeiros (
            descricao, tipo, valor, data_competencia, data_vencimento, data_movimento, status,
            categoria_id, conta_financeira_id, conta_origem_id, conta_destino_id, forma_pagamento,
            pessoa_tipo, pessoa_id, observacoes, conciliado, recorrencia_grupo, parcela_atual, parcela_total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        descricao,
        tipo,
        valor,
        data_competencia,
        data_vencimento,
        data_movimento,
        status,
        _safe_int(categoria_id),
        _safe_int(conta_financeira_id),
        _safe_int(conta_origem_id),
        _safe_int(conta_destino_id),
        forma_pagamento,
        pessoa_tipo or "",
        _safe_int(pessoa_id),
        observacoes,
        int(conciliado or 0),
        recorrencia_grupo,
        parcela_atual,
        parcela_total,
    ))

    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_lancamento(
    id_lancamento,
    descricao,
    tipo,
    valor,
    data_competencia,
    data_vencimento=None,
    data_movimento=None,
    status="pendente",
    categoria_id=None,
    conta_financeira_id=None,
    conta_origem_id=None,
    conta_destino_id=None,
    forma_pagamento="",
    pessoa_tipo="",
    pessoa_id=None,
    observacoes="",
    conciliado=0,
    recorrencia_grupo=None,
    parcela_atual=None,
    parcela_total=None,
):
    tipo = tipo or "despesa"
    status = _normalizar_status(tipo, status)
    data_vencimento = data_vencimento or data_competencia
    valor = _to_float(valor)

    if status not in STATUS_REALIZADOS:
        data_movimento = None

    if tipo == "transferencia":
        conta_financeira_id = None
        pessoa_tipo = ""
        pessoa_id = None
    else:
        conta_origem_id = None
        conta_destino_id = None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE lancamentos_financeiros
        SET descricao = ?, tipo = ?, valor = ?, data_competencia = ?, data_vencimento = ?, data_movimento = ?,
            status = ?, categoria_id = ?, conta_financeira_id = ?, conta_origem_id = ?, conta_destino_id = ?,
            forma_pagamento = ?, pessoa_tipo = ?, pessoa_id = ?, observacoes = ?, conciliado = ?,
            recorrencia_grupo = ?, parcela_atual = ?, parcela_total = ?, atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        descricao,
        tipo,
        valor,
        data_competencia,
        data_vencimento,
        data_movimento,
        status,
        _safe_int(categoria_id),
        _safe_int(conta_financeira_id),
        _safe_int(conta_origem_id),
        _safe_int(conta_destino_id),
        forma_pagamento,
        pessoa_tipo or "",
        _safe_int(pessoa_id),
        observacoes,
        int(conciliado or 0),
        recorrencia_grupo,
        parcela_atual,
        parcela_total,
        id_lancamento,
    ))

    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok


def excluir_lancamento(id_lancamento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lancamentos_financeiros WHERE id = ?", (id_lancamento,))
    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok


def marcar_lancamento_realizado(id_lancamento, conta_financeira_id=None, data_movimento=None, forma_pagamento=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lancamentos_financeiros WHERE id = ?", (id_lancamento,))
    lancamento = cursor.fetchone()

    if not lancamento:
        conn.close()
        return False

    tipo = lancamento["tipo"]
    novo_status = "recebido" if tipo == "receita" else "pago"
    data_movimento = data_movimento or _today_iso()

    if tipo == "transferencia":
        cursor.execute("""
            UPDATE lancamentos_financeiros
            SET status = ?, data_movimento = ?, forma_pagamento = COALESCE(NULLIF(?, ''), forma_pagamento),
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, data_movimento, forma_pagamento or "", id_lancamento))
    else:
        cursor.execute("""
            UPDATE lancamentos_financeiros
            SET status = ?, data_movimento = ?, conta_financeira_id = COALESCE(?, conta_financeira_id),
                forma_pagamento = COALESCE(NULLIF(?, ''), forma_pagamento), atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_status, data_movimento, _safe_int(conta_financeira_id), forma_pagamento or "", id_lancamento))

    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok


def cancelar_lancamento(id_lancamento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE lancamentos_financeiros
        SET status = 'cancelado', data_movimento = NULL, atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (id_lancamento,))
    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok


def duplicar_lancamento(id_lancamento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lancamentos_financeiros WHERE id = ?", (id_lancamento,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    cursor.execute("""
        INSERT INTO lancamentos_financeiros (
            descricao, tipo, valor, data_competencia, data_vencimento, data_movimento, status,
            categoria_id, conta_financeira_id, conta_origem_id, conta_destino_id, forma_pagamento,
            pessoa_tipo, pessoa_id, observacoes, conciliado, recorrencia_grupo, parcela_atual, parcela_total
        ) VALUES (?, ?, ?, ?, ?, NULL, 'pendente', ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
    """, (
        f"Cópia de {row['descricao']}", row["tipo"], row["valor"], _today_iso(), _today_iso(),
        row["categoria_id"], row["conta_financeira_id"], row["conta_origem_id"], row["conta_destino_id"],
        row["forma_pagamento"], row["pessoa_tipo"], row["pessoa_id"], row["observacoes"],
        row["recorrencia_grupo"], row["parcela_atual"], row["parcela_total"]
    ))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def _add_months(iso_date, months):
    dt = datetime.strptime(iso_date, "%Y-%m-%d").date()
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    # último dia do mês alvo
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    day = min(dt.day, last_day)
    return date(year, month, day).isoformat()


def cadastrar_lancamento_parcelado(parcelas=1, **kwargs):
    parcelas = int(parcelas or 1)
    if parcelas <= 1:
        return [cadastrar_lancamento(**kwargs)]

    grupo = str(uuid4())
    ids = []
    valor_total = _to_float(kwargs.get("valor"))
    valor_parcela = round(valor_total / parcelas, 2)
    diferenca = round(valor_total - (valor_parcela * parcelas), 2)

    data_competencia_base = kwargs.get("data_competencia")
    data_vencimento_base = kwargs.get("data_vencimento") or data_competencia_base

    for i in range(parcelas):
        dados = dict(kwargs)
        dados["descricao"] = f"{kwargs.get('descricao')} ({i + 1}/{parcelas})"
        dados["valor"] = valor_parcela + (diferenca if i == parcelas - 1 else 0)
        dados["data_competencia"] = _add_months(data_competencia_base, i)
        dados["data_vencimento"] = _add_months(data_vencimento_base, i)
        dados["status"] = "pendente"
        dados["data_movimento"] = None
        dados["recorrencia_grupo"] = grupo
        dados["parcela_atual"] = i + 1
        dados["parcela_total"] = parcelas
        ids.append(cadastrar_lancamento(**dados))

    return ids


def listar_contas_a_pagar(termo="", dias_a_frente=None):
    filtros = {"campo_data": "data_vencimento"}
    if dias_a_frente is not None:
        filtros["data_inicio"] = "1900-01-01"
        # cálculo direto em SQL seria melhor, mas manteremos simples na tela.
    lancamentos = listar_lancamentos(limite=1000, termo=termo, filtros=filtros)
    return [l for l in lancamentos if l["tipo"] in ("despesa", "custo") and l["status"] == "pendente"]


def listar_contas_a_receber(termo=""):
    lancamentos = listar_lancamentos(limite=1000, termo=termo, filtros={"campo_data": "data_vencimento"})
    return [l for l in lancamentos if l["tipo"] == "receita" and l["status"] == "pendente"]


def obter_resumo_dashboard(ano=None, mes=None):
    hoje = date.today()
    ano = ano or hoje.year
    mes = mes or hoje.month
    inicio = f"{ano:04d}-{mes:02d}-01"
    fim = f"{ano + 1:04d}-01-01" if mes == 12 else f"{ano:04d}-{mes + 1:02d}-01"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN tipo = 'receita' AND status != 'cancelado' THEN valor ELSE 0 END), 0) AS receitas_competencia,
            COALESCE(SUM(CASE WHEN tipo = 'custo' AND status != 'cancelado' THEN valor ELSE 0 END), 0) AS custos_competencia,
            COALESCE(SUM(CASE WHEN tipo = 'despesa' AND status != 'cancelado' THEN valor ELSE 0 END), 0) AS despesas_competencia,
            COALESCE(SUM(CASE WHEN tipo = 'receita' AND status IN ('pago', 'recebido') THEN valor ELSE 0 END), 0) AS receitas_realizadas,
            COALESCE(SUM(CASE WHEN tipo IN ('despesa', 'custo') AND status IN ('pago', 'recebido') THEN valor ELSE 0 END), 0) AS saidas_realizadas,
            COALESCE(SUM(CASE WHEN tipo = 'receita' AND status = 'pendente' THEN valor ELSE 0 END), 0) AS receitas_pendentes,
            COALESCE(SUM(CASE WHEN tipo IN ('despesa', 'custo') AND status = 'pendente' THEN valor ELSE 0 END), 0) AS saidas_pendentes
        FROM lancamentos_financeiros
        WHERE data_competencia >= ? AND data_competencia < ?
          AND tipo != 'transferencia'
    """, (inicio, fim))
    resumo_mes = dict(cursor.fetchone())

    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN tipo = 'receita' AND status = 'pendente' AND data_vencimento < date('now', 'localtime') THEN valor ELSE 0 END), 0) AS receber_vencido,
            COALESCE(SUM(CASE WHEN tipo IN ('despesa', 'custo') AND status = 'pendente' AND data_vencimento < date('now', 'localtime') THEN valor ELSE 0 END), 0) AS pagar_vencido,
            COALESCE(SUM(CASE WHEN tipo = 'receita' AND status = 'pendente' AND data_vencimento BETWEEN date('now', 'localtime') AND date('now', '+7 day', 'localtime') THEN valor ELSE 0 END), 0) AS receber_7_dias,
            COALESCE(SUM(CASE WHEN tipo IN ('despesa', 'custo') AND status = 'pendente' AND data_vencimento BETWEEN date('now', 'localtime') AND date('now', '+7 day', 'localtime') THEN valor ELSE 0 END), 0) AS pagar_7_dias,
            COUNT(CASE WHEN status = 'pendente' THEN 1 END) AS total_pendentes
        FROM lancamentos_financeiros
        WHERE status != 'cancelado'
    """)
    resumo_pendencias = dict(cursor.fetchone())

    cursor.execute("SELECT COUNT(*) FROM contas_financeiras WHERE ativo = 1")
    total_contas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT cat.nome AS categoria_nome, SUM(lf.valor) AS total
        FROM lancamentos_financeiros lf
        LEFT JOIN categorias_financeiras cat ON cat.id = lf.categoria_id
        WHERE lf.tipo IN ('despesa', 'custo')
          AND lf.status != 'cancelado'
          AND lf.data_competencia >= ? AND lf.data_competencia < ?
        GROUP BY cat.nome
        ORDER BY total DESC
        LIMIT 1
    """, (inicio, fim))
    maior_categoria = _row_to_dict(cursor.fetchone()) or {"categoria_nome": "-", "total": 0}

    cursor.execute("""
        SELECT descricao, valor
        FROM lancamentos_financeiros
        WHERE tipo IN ('despesa', 'custo')
          AND status != 'cancelado'
          AND data_competencia >= ? AND data_competencia < ?
        ORDER BY valor DESC
        LIMIT 1
    """, (inicio, fim))
    maior_despesa = _row_to_dict(cursor.fetchone()) or {"descricao": "-", "valor": 0}

    conn.close()

    contas = listar_contas_financeiras(ativas_apenas=True)
    saldo_total = sum(float(c["saldo_atual"] or 0) for c in contas)

    receitas_comp = resumo_mes["receitas_competencia"]
    custos_comp = resumo_mes["custos_competencia"]
    despesas_comp = resumo_mes["despesas_competencia"]
    receitas_realizadas = resumo_mes["receitas_realizadas"]
    saidas_realizadas = resumo_mes["saidas_realizadas"]

    return {
        **resumo_mes,
        **resumo_pendencias,
        "resultado_competencia": receitas_comp - custos_comp - despesas_comp,
        "resultado_realizado": receitas_realizadas - saidas_realizadas,
        "lucro_bruto": receitas_comp - custos_comp,
        "saldo_total": saldo_total,
        "total_contas": total_contas,
        "periodo": f"{mes:02d}/{ano}",
        "maior_categoria_nome": maior_categoria.get("categoria_nome") or "-",
        "maior_categoria_total": maior_categoria.get("total") or 0,
        "maior_despesa_descricao": maior_despesa.get("descricao") or "-",
        "maior_despesa_valor": maior_despesa.get("valor") or 0,
    }


def relatorio_por_categoria(data_inicio=None, data_fim=None, tipo=None):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT lf.tipo, COALESCE(cat.nome, 'Sem categoria') AS categoria, COALESCE(cat.grupo_dre, '') AS grupo_dre,
               COALESCE(cat.grupo_dfc, '') AS grupo_dfc, SUM(lf.valor) AS total, COUNT(*) AS quantidade
        FROM lancamentos_financeiros lf
        LEFT JOIN categorias_financeiras cat ON cat.id = lf.categoria_id
        WHERE lf.status != 'cancelado' AND lf.tipo != 'transferencia'
    """
    params = []
    if tipo:
        sql += " AND lf.tipo = ?"
        params.append(tipo)
    if data_inicio:
        sql += " AND lf.data_competencia >= ?"
        params.append(data_inicio)
    if data_fim:
        sql += " AND lf.data_competencia <= ?"
        params.append(data_fim)
    sql += " GROUP BY lf.tipo, cat.nome, cat.grupo_dre, cat.grupo_dfc ORDER BY lf.tipo, total DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def relatorio_saldo_contas():
    return listar_contas_financeiras(ativas_apenas=False)


def relatorio_fluxo_caixa(data_inicio=None, data_fim=None, projetado=False):
    campo_data = "data_vencimento" if projetado else "data_movimento"
    conn = get_connection()
    cursor = conn.cursor()
    sql = f"""
        SELECT
            lf.id,
            lf.descricao,
            lf.tipo,
            lf.valor,
            lf.{campo_data} AS data_fluxo,
            lf.status,
            cf.nome AS conta_nome,
            origem.nome AS conta_origem_nome,
            destino.nome AS conta_destino_nome,
            cat.nome AS categoria_nome,
            CASE
                WHEN lf.tipo = 'receita' THEN lf.valor
                WHEN lf.tipo IN ('despesa', 'custo') THEN -lf.valor
                WHEN lf.tipo = 'transferencia' THEN 0
                ELSE 0
            END AS impacto_caixa
        FROM lancamentos_financeiros lf
        LEFT JOIN contas_financeiras cf ON cf.id = lf.conta_financeira_id
        LEFT JOIN contas_financeiras origem ON origem.id = lf.conta_origem_id
        LEFT JOIN contas_financeiras destino ON destino.id = lf.conta_destino_id
        LEFT JOIN categorias_financeiras cat ON cat.id = lf.categoria_id
        WHERE lf.status != 'cancelado'
          AND lf.tipo != 'transferencia'
    """
    params = []

    if projetado:
        sql += " AND lf.status = 'pendente'"
    else:
        sql += " AND lf.status IN ('pago', 'recebido')"

    if data_inicio:
        sql += f" AND lf.{campo_data} >= ?"
        params.append(data_inicio)
    if data_fim:
        sql += f" AND lf.{campo_data} <= ?"
        params.append(data_fim)

    sql += f" ORDER BY lf.{campo_data} ASC, lf.id ASC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def calcular_nfc(dias=30, reserva_percentual=20.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN tipo IN ('despesa', 'custo') AND status = 'pendente' THEN valor ELSE 0 END), 0) AS saidas,
            COALESCE(SUM(CASE WHEN tipo = 'receita' AND status = 'pendente' THEN valor ELSE 0 END), 0) AS entradas
        FROM lancamentos_financeiros
        WHERE status = 'pendente'
          AND data_vencimento BETWEEN date('now', 'localtime') AND date('now', ? || ' day', 'localtime')
          AND status != 'cancelado'
    """, (int(dias),))
    row = dict(cursor.fetchone())
    conn.close()

    saldo_total = sum(float(c["saldo_atual"] or 0) for c in listar_contas_financeiras(ativas_apenas=True))
    saidas = float(row["saidas"] or 0)
    entradas = float(row["entradas"] or 0)
    reserva = saidas * (float(reserva_percentual or 0) / 100)
    nfc = max(0, saidas + reserva - saldo_total - entradas)
    return {
        "dias": dias,
        "saidas_previstas": saidas,
        "entradas_confirmadas": entradas,
        "saldo_total": saldo_total,
        "reserva_seguranca": reserva,
        "nfc": nfc,
    }


def registrar_conciliacao(conta_financeira_id, data_conciliacao, saldo_real, observacoes=""):
    saldo_sistema = obter_saldo_conta(conta_financeira_id)
    saldo_real = _to_float(saldo_real)
    diferenca = saldo_real - saldo_sistema
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conciliacoes_financeiras (
            conta_financeira_id, data_conciliacao, saldo_sistema, saldo_real, diferenca, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (conta_financeira_id, data_conciliacao, saldo_sistema, saldo_real, diferenca, observacoes))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def listar_conciliacoes(conta_financeira_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT c.*, cf.nome AS conta_nome
        FROM conciliacoes_financeiras c
        LEFT JOIN contas_financeiras cf ON cf.id = c.conta_financeira_id
        WHERE 1 = 1
    """
    params = []
    if conta_financeira_id:
        sql += " AND c.conta_financeira_id = ?"
        params.append(conta_financeira_id)
    sql += " ORDER BY c.data_conciliacao DESC, c.id DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def adicionar_anexo_lancamento(lancamento_id, caminho_arquivo, tipo="", observacoes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO anexos_lancamentos (lancamento_id, caminho_arquivo, tipo, observacoes)
        VALUES (?, ?, ?, ?)
    """, (lancamento_id, caminho_arquivo, tipo, observacoes))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def listar_anexos_lancamento(lancamento_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, lancamento_id, caminho_arquivo, tipo, observacoes, criado_em
        FROM anexos_lancamentos
        WHERE lancamento_id = ?
        ORDER BY criado_em DESC
    """, (lancamento_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
