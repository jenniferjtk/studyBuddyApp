import sqlite3
from pathlib import Path
# This class defines the interface for interacting with the SQLite database
# It is a helper of sorts so that the StudyBuddy app doesn't ever directly call
# sqlite3 functions so that the DB could be changed later on if necessary 

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
# Runs a SELECT query and fetches all rows at once. Returns a list of sqlite3.Row 
# objects (behave like dicts)
    def query_all(self, sql: str, params: dict = {}):
        cur = self.conn.execute(sql, params)
        return cur.fetchall()
 #Runs a SELECT and fetches only the first row
    def query_one(self, sql: str, params: dict = {}):
        cur = self.conn.execute(sql, params)
        return cur.fetchone()