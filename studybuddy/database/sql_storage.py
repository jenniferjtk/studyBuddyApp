import sqlite3
from pathlib import Path

class Storage:
    """Thin SQLite wrapper used by the service layer."""
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row

    def execute_script(self, sql_text: str) -> None:
        self.conn.executescript(sql_text)
        self.conn.commit()

    def execute(self, sql: str, params: dict = {}) -> None:
        self.conn.execute(sql, params)
        self.conn.commit()

    def query_all(self, sql: str, params: dict = {}):
        cur = self.conn.execute(sql, params)
        return cur.fetchall()

    def query_one(self, sql: str, params: dict = {}):
        cur = self.conn.execute(sql, params)
        return cur.fetchone()