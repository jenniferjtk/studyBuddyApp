# db.py
import sqlite3
from pathlib import Path
from contextlib import closing

ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "db" / "schema.sql"

def connect(db_path: str = "studybuddy.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma foreign_keys = on;")
    return conn

def init_db(conn: sqlite3.Connection) -> None:
    with open(SCHEMA, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

# ====== STUDENTS (implemented now) ==========================================
def student_get(conn: sqlite3.Connection, student_id: str) -> dict:
    with closing(conn.cursor()) as cur:
        cur.execute("select id, name, email from students where id = ?", (student_id,))
        row = cur.fetchone()
        if not row:
            raise KeyError(f"student {student_id} not found")
        return dict(row)

def student_upsert(conn: sqlite3.Connection, student: dict) -> None:
    with closing(conn.cursor()) as cur:
        cur.execute(
            """
            insert into students(id, name, email) values(?,?,?)
            on conflict(id) do update set name = excluded.name, email = excluded.email
            """,
            (student["id"], student["name"], student["email"]),
        )
        conn.commit()

# ====== COURSES (to add in loop-back step) ==================================
# def course_get_by_code(conn, code) -> dict: ...
# def course_ensure(conn, code, title) -> dict: ...
# def enrollment_add(conn, student_id, course_id) -> None: ...
# def enrollment_remove(conn, student_id, course_id) -> None: ...
# def students_in_course(conn, course_id) -> list[dict]: ...
# def courses_for_student(conn, student_id) -> list[str]: ...

# ====== AVAILABILITY (to add later) =========================================
# def availability_list(conn, student_id) -> list[TimeSlot]: ...
# def availability_add(conn, student_id, slot: TimeSlot) -> None: ...
# def availability_remove(conn, student_id, slot: TimeSlot) -> None: ...

# ====== SESSIONS (to add later) =============================================
# def session_create(conn, **fields) -> str: ...
# def session_get(conn, session_id) -> dict: ...
# def session_update_status(conn, session_id, status) -> None: ...
# def session_list_for_student(conn, student_id) -> list[dict]: ...
# def session_conflicts(conn, student_id, day, start_min, end_min) -> bool: ...