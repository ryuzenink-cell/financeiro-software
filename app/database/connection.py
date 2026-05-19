import sqlite3
from app.config import DATA_DIR, DB_PATH


def get_connection():
    """Abre uma conexão SQLite já preparada para uso financeiro.

    O SQLite não ativa chaves estrangeiras por padrão. Como o sistema
    depende de relacionamento entre contas, categorias e lançamentos,
    ativamos o PRAGMA em toda conexão.
    """
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
