from app.database.connection import get_connection


CATEGORIAS_PADRAO = [
    ("Vendas de produtos", "receita", "Receita Bruta", "Operacional", "Resultado", "credito"),
    ("Prestação de serviços", "receita", "Receita Bruta", "Operacional", "Resultado", "credito"),
    ("Outras receitas", "receita", "Outras Receitas", "Operacional", "Resultado", "credito"),
    ("Compra de mercadorias", "custo", "CMV/CSP", "Operacional", "Estoque/Resultado", "debito"),
    ("Embalagens", "custo", "CMV/CSP", "Operacional", "Resultado", "debito"),
    ("Frete sobre compras", "custo", "CMV/CSP", "Operacional", "Resultado", "debito"),
    ("Aluguel", "despesa", "Despesas Fixas", "Operacional", "Resultado", "debito"),
    ("Energia elétrica", "despesa", "Despesas Fixas", "Operacional", "Resultado", "debito"),
    ("Internet e telefone", "despesa", "Despesas Fixas", "Operacional", "Resultado", "debito"),
    ("Marketing", "despesa", "Despesas Comerciais", "Operacional", "Resultado", "debito"),
    ("Taxa de maquininha", "despesa", "Despesas Variáveis", "Operacional", "Resultado", "debito"),
    ("DAS MEI", "despesa", "Deduções/Impostos", "Operacional", "Impostos a pagar", "debito"),
    ("Retirada do empreendedor", "despesa", "Retiradas", "Financiamento", "Patrimônio Líquido", "debito"),
    ("Transferência entre contas", "transferencia", "Não se aplica", "Não se aplica", "Caixa/Bancos", "neutra"),
]


CONTAS_FINANCEIRAS_PADRAO = [
    ("Caixa", "caixa", 0.0),
    ("Conta bancária", "banco", 0.0),
    ("Carteira digital", "carteira_digital", 0.0),
]


PLANO_CONTAS_PADRAO = [
    ("1", "Ativo", "ativo", None),
    ("1.1", "Caixa e equivalentes", "ativo", "1"),
    ("1.2", "Contas a receber", "ativo", "1"),
    ("1.3", "Estoque", "ativo", "1"),
    ("1.4", "Imobilizado", "ativo", "1"),
    ("2", "Passivo", "passivo", None),
    ("2.1", "Contas a pagar", "passivo", "2"),
    ("2.2", "Impostos a pagar", "passivo", "2"),
    ("2.3", "Empréstimos", "passivo", "2"),
    ("3", "Patrimônio líquido", "patrimonio", None),
    ("3.1", "Capital inicial", "patrimonio", "3"),
    ("3.2", "Lucros acumulados", "patrimonio", "3"),
    ("3.3", "Retiradas", "patrimonio", "3"),
    ("4", "Receitas", "resultado", None),
    ("4.1", "Receita bruta", "resultado", "4"),
    ("4.2", "Outras receitas", "resultado", "4"),
    ("5", "Custos e despesas", "resultado", None),
    ("5.1", "Custos", "resultado", "5"),
    ("5.2", "Despesas", "resultado", "5"),
    ("5.3", "Impostos", "resultado", "5"),
]


def _table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def _add_column_if_missing(cursor, table_name, column_name, definition):
    if column_name not in _table_columns(cursor, table_name):
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            documento TEXT,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            observacoes TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            documento TEXT,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            observacoes TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresas_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razao_social TEXT,
            nome_fantasia TEXT NOT NULL,
            cnpj TEXT,
            inscricao_estadual TEXT,
            inscricao_municipal TEXT,
            mei INTEGER NOT NULL DEFAULT 1,
            cnae TEXT,
            atividade_principal TEXT,
            responsavel TEXT,
            cpf_responsavel TEXT,
            telefone TEXT,
            email TEXT,
            cep TEXT,
            endereco TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT,
            observacoes TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plano_contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            codigo_pai TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_financeiras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'banco',
            saldo_inicial REAL NOT NULL DEFAULT 0,
            data_saldo_inicial TEXT,
            observacoes TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias_financeiras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            grupo_dre TEXT,
            grupo_dfc TEXT,
            grupo_bp TEXT,
            natureza TEXT DEFAULT 'neutra',
            plano_conta_id INTEGER,
            incluir_relatorios INTEGER NOT NULL DEFAULT 1,
            observacoes TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plano_conta_id) REFERENCES plano_contas(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos_financeiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            data_competencia TEXT NOT NULL,
            data_vencimento TEXT,
            data_movimento TEXT,
            status TEXT NOT NULL DEFAULT 'pendente',
            categoria_id INTEGER,
            conta_financeira_id INTEGER,
            conta_origem_id INTEGER,
            conta_destino_id INTEGER,
            forma_pagamento TEXT,
            pessoa_tipo TEXT,
            pessoa_id INTEGER,
            observacoes TEXT,
            conciliado INTEGER NOT NULL DEFAULT 0,
            recorrencia_grupo TEXT,
            parcela_atual INTEGER,
            parcela_total INTEGER,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TEXT,
            FOREIGN KEY (categoria_id) REFERENCES categorias_financeiras(id),
            FOREIGN KEY (conta_financeira_id) REFERENCES contas_financeiras(id),
            FOREIGN KEY (conta_origem_id) REFERENCES contas_financeiras(id),
            FOREIGN KEY (conta_destino_id) REFERENCES contas_financeiras(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anexos_lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lancamento_id INTEGER NOT NULL,
            caminho_arquivo TEXT NOT NULL,
            tipo TEXT,
            observacoes TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lancamento_id) REFERENCES lancamentos_financeiros(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conciliacoes_financeiras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_financeira_id INTEGER NOT NULL,
            data_conciliacao TEXT NOT NULL,
            saldo_sistema REAL NOT NULL DEFAULT 0,
            saldo_real REAL NOT NULL DEFAULT 0,
            diferenca REAL NOT NULL DEFAULT 0,
            observacoes TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conta_financeira_id) REFERENCES contas_financeiras(id)
        )
    """)

    # Tabelas legadas mantidas para compatibilidade com o projeto inicial.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_pagar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fornecedor_id INTEGER,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_vencimento TEXT NOT NULL,
            data_pagamento TEXT,
            status TEXT DEFAULT 'aberto',
            categoria TEXT,
            forma_pagamento TEXT,
            observacoes TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_receber (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_vencimento TEXT NOT NULL,
            data_recebimento TEXT,
            status TEXT DEFAULT 'aberto',
            categoria TEXT,
            forma_pagamento TEXT,
            observacoes TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fluxo_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_movimento TEXT NOT NULL,
            origem TEXT,
            origem_id INTEGER,
            categoria TEXT,
            forma_pagamento TEXT,
            observacoes TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    migrate_existing_database(cursor)
    create_indexes(cursor)
    seed_defaults(cursor)

    connection.commit()
    connection.close()


def migrate_existing_database(cursor):
    # Migrações idempotentes para bancos criados pelas versões anteriores.
    for tabela in ["fornecedores", "clientes"]:
        for column_name, definition in [
            ("endereco", "TEXT"),
            ("observacoes", "TEXT"),
            ("ativo", "INTEGER DEFAULT 1"),
            ("criado_em", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ]:
            _add_column_if_missing(cursor, tabela, column_name, definition)

    for column_name, definition in [
        ("razao_social", "TEXT"),
        ("nome_fantasia", "TEXT"),
        ("cnpj", "TEXT"),
        ("inscricao_estadual", "TEXT"),
        ("inscricao_municipal", "TEXT"),
        ("mei", "INTEGER NOT NULL DEFAULT 1"),
        ("cnae", "TEXT"),
        ("atividade_principal", "TEXT"),
        ("responsavel", "TEXT"),
        ("cpf_responsavel", "TEXT"),
        ("telefone", "TEXT"),
        ("email", "TEXT"),
        ("cep", "TEXT"),
        ("endereco", "TEXT"),
        ("numero", "TEXT"),
        ("complemento", "TEXT"),
        ("bairro", "TEXT"),
        ("cidade", "TEXT"),
        ("uf", "TEXT"),
        ("observacoes", "TEXT"),
        ("ativo", "INTEGER NOT NULL DEFAULT 1"),
        ("criado_em", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ("atualizado_em", "TEXT"),
    ]:
        _add_column_if_missing(cursor, "empresas_sistema", column_name, definition)

    for column_name, definition in [
        ("grupo_dfc", "TEXT"),
        ("grupo_bp", "TEXT"),
        ("natureza", "TEXT DEFAULT 'neutra'"),
        ("plano_conta_id", "INTEGER"),
        ("incluir_relatorios", "INTEGER NOT NULL DEFAULT 1"),
    ]:
        _add_column_if_missing(cursor, "categorias_financeiras", column_name, definition)

    for column_name, definition in [
        ("data_vencimento", "TEXT"),
        ("conta_origem_id", "INTEGER"),
        ("conta_destino_id", "INTEGER"),
        ("conciliado", "INTEGER NOT NULL DEFAULT 0"),
        ("recorrencia_grupo", "TEXT"),
        ("parcela_atual", "INTEGER"),
        ("parcela_total", "INTEGER"),
    ]:
        _add_column_if_missing(cursor, "lancamentos_financeiros", column_name, definition)

    # Se um lançamento antigo não tiver vencimento, assume competência como vencimento inicial.
    cursor.execute("""
        UPDATE lancamentos_financeiros
        SET data_vencimento = COALESCE(data_vencimento, data_competencia)
        WHERE data_vencimento IS NULL OR data_vencimento = ''
    """)

    cursor.execute("INSERT OR IGNORE INTO schema_migrations (version) VALUES ('001_financeiro_core_v2')")


def create_indexes(cursor):
    indexes = [
        ("idx_lancamentos_data_competencia", "lancamentos_financeiros", "data_competencia"),
        ("idx_lancamentos_data_vencimento", "lancamentos_financeiros", "data_vencimento"),
        ("idx_lancamentos_data_movimento", "lancamentos_financeiros", "data_movimento"),
        ("idx_lancamentos_status", "lancamentos_financeiros", "status"),
        ("idx_lancamentos_tipo", "lancamentos_financeiros", "tipo"),
        ("idx_lancamentos_conta", "lancamentos_financeiros", "conta_financeira_id"),
        ("idx_lancamentos_categoria", "lancamentos_financeiros", "categoria_id"),
        ("idx_lancamentos_pessoa", "lancamentos_financeiros", "pessoa_tipo, pessoa_id"),
    ]
    for name, table, columns in indexes:
        cursor.execute(f"CREATE INDEX IF NOT EXISTS {name} ON {table}({columns})")


def restaurar_categorias_padrao(cursor):
    """Recria categorias financeiras padrão sem duplicar as que já existem.

    Essa rotina é usada tanto na inicialização do sistema quanto quando o
    usuário exclui categorias padrão por engano. Ela procura por nome + tipo e:
    - reativa categorias inativas;
    - completa grupos DRE/DFC/BP e natureza vazios;
    - insere categorias que não existem mais.
    """
    for nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza in CATEGORIAS_PADRAO:
        cursor.execute("""
            SELECT id
            FROM categorias_financeiras
            WHERE nome = ? AND tipo = ?
            LIMIT 1
        """, (nome, tipo))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE categorias_financeiras
                SET grupo_dre = COALESCE(NULLIF(grupo_dre, ''), ?),
                    grupo_dfc = COALESCE(NULLIF(grupo_dfc, ''), ?),
                    grupo_bp = COALESCE(NULLIF(grupo_bp, ''), ?),
                    natureza = COALESCE(NULLIF(natureza, ''), ?),
                    incluir_relatorios = 1,
                    ativo = 1
                WHERE id = ?
            """, (grupo_dre, grupo_dfc, grupo_bp, natureza, row["id"]))
        else:
            cursor.execute("""
                INSERT INTO categorias_financeiras (nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza, incluir_relatorios, ativo)
                VALUES (?, ?, ?, ?, ?, ?, 1, 1)
            """, (nome, tipo, grupo_dre, grupo_dfc, grupo_bp, natureza))


def seed_defaults(cursor):
    for codigo, nome, tipo, codigo_pai in PLANO_CONTAS_PADRAO:
        cursor.execute("""
            INSERT OR IGNORE INTO plano_contas (codigo, nome, tipo, codigo_pai)
            VALUES (?, ?, ?, ?)
        """, (codigo, nome, tipo, codigo_pai))

    restaurar_categorias_padrao(cursor)

    cursor.execute("SELECT COUNT(*) FROM contas_financeiras")
    total_contas = cursor.fetchone()[0]

    if total_contas == 0:
        cursor.executemany("""
            INSERT INTO contas_financeiras (nome, tipo, saldo_inicial)
            VALUES (?, ?, ?)
        """, CONTAS_FINANCEIRAS_PADRAO)
