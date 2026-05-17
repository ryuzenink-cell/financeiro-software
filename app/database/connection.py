import sqlite3
from app.config import DATA_DIR, DB_PATH


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection