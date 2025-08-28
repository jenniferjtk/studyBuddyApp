# services.py
from typing import Protocol
from models import TimeSlot, SessionStatus  # (import now so file stays stable)

# lightweight “protocol” types just to hint what db.py must provide
class _StudentDB(Protocol):
    def student_upsert(self, student: dict) -> None: ...
    def student_get(self, student_id: str) -> dict: ...

class StudyBuddyService:
    """
    Use-case layer: one method per feature. Start with profiles only.
    Later you’ll add course/availability/sessions using db.py helpers.
    """
    def __init__(self, db):
        # db is a simple object with the helper functions from db.py bound in.
        self.db = db

    # ---- Profile ----
    def create_or_update_profile(self, student_id: str, name: str, email: str) -> None:
        self.db.student_upsert({"id": student_id, "name": name, "email": email})

    def get_profile(self, student_id: str) -> dict:
        return self.db.student_get(student_id)

    # ---- Courses (add later) ----
    # def add_course(self, student_id, course_code, title): ...
    # def remove_course(self, student_id, course_code): ...

    # ---- Availability (add later) ----
    # def add_availability(self, student_id, day, start_min, end_min): ...
    # def remove_availability(self, student_id, day, start_min, end_min): ...

    # ---- Matching (add later) ----
    # def suggest_matches(self, student_id): ...

    # ---- Sessions (add later) ----
    # def request_session(self, requester_id, peer_id, course_code, day, start_min, end_min): ...
    # def respond_session(self, session_id, status: SessionStatus): ...
    # def list_my_sessions(self, student_id): ...