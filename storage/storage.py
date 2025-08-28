# storage.py
import db as _db
from models import User, Course, StudySession, TimeSlot, SessionStatus

class Storage:
    def __init__(self, conn):
        self.conn = conn

    # ----- Users -----
    def save_user(self, user: User) -> None:
        _db.student_upsert(self.conn, {"id": user.id, "name": user.name, "email": user.email})
    def get_user(self, user_id: str) -> User:
        r = _db.student_get(self.conn, user_id)
        return User(id=r["id"], name=r["name"], email=r["email"])

    # ----- Courses / enrollment -----
    def ensure_course(self, code: str, title: str) -> Course:
        c = _db.course_ensure(self.conn, code, title)
        return Course(id=c["id"], code=c["code"], title=c["title"])
    def get_course_by_code(self, code: str) -> Course:
        c = _db.course_get_by_code(self.conn, code); return Course(**c)
    def enroll(self, student_id: str, course_id: str) -> None:
        _db.enrollment_add(self.conn, student_id, course_id)
    def unenroll(self, student_id: str, course_id: str) -> None:
        _db.enrollment_remove(self.conn, student_id, course_id)
    def courses_for_student(self, student_id: str) -> list[str]:
        return _db.courses_for_student(self.conn, student_id)
    def students_in_course(self, course_id: str) -> list[User]:
        rows = _db.students_in_course(self.conn, course_id)
        return [User(id=r["id"], name=r["name"], email=r["email"]) for r in rows]

    # ----- Availability -----
    def availability_list(self, student_id: str) -> list[TimeSlot]:
        return _db.availability_list(self.conn, student_id)
    def availability_add(self, student_id: str, slot: TimeSlot) -> None:
        _db.availability_add(self.conn, student_id, slot)
    def availability_remove(self, student_id: str, slot: TimeSlot) -> None:
        _db.availability_remove(self.conn, student_id, slot)

    # ----- Sessions -----
    def create_session(self, course_id: str, req: str, peer: str, day: int, s: int, e: int, status: SessionStatus) -> str:
        return _db.session_create(self.conn, course_id, req, peer, day, s, e, status.value)
    def get_session(self, session_id: str) -> StudySession:
        r = _db.session_get(self.conn, session_id)
        return StudySession(id=r["id"], course_id=r["course_id"], requester_id=r["requester_id"],
                            peer_id=r["peer_id"], day=r["day"], start_min=r["start_min"],
                            end_min=r["end_min"], status=SessionStatus(r["status"]))
    def update_session_status(self, session_id: str, status: SessionStatus) -> None:
        _db.session_update_status(self.conn, session_id, status.value)
    def list_sessions_for(self, student_id: str) -> list[StudySession]:
        rows = _db.session_list_for_student(self.conn, student_id)
        return [StudySession(id=r["id"], course_id=r["course_id"], requester_id=r["requester_id"],
                             peer_id=r["peer_id"], day=r["day"], start_min=r["start_min"],
                             end_min=r["end_min"], status=SessionStatus(r["status"])) for r in rows]
    def has_conflict(self, student_id: str, day: int, s: int, e: int) -> bool:
        return _db.session_conflicts(self.conn, student_id, day, s, e)