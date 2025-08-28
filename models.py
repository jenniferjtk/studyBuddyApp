# models.py
from dataclasses import dataclass
from enum import Enum

class SessionStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"

@dataclass(frozen=True)
class TimeSlot:
    day: int
    start_min: int
    end_min: int
    def overlaps(self, other: "TimeSlot") -> bool:
        return self.day == other.day and not (self.end_min <= other.start_min or other.end_min <= self.start_min)
    def intersection(self, other: "TimeSlot") -> "TimeSlot | None":
        if not self.overlaps(other): return None
        return TimeSlot(self.day, max(self.start_min, other.start_min), min(self.end_min, other.end_min))

@dataclass
class Course:
    id: str
    code: str
    title: str

@dataclass
class User:
    id: str
    name: str
    email: str

@dataclass
class StudySession:
    id: str
    course_id: str
    requester_id: str
    peer_id: str
    day: int
    start_min: int
    end_min: int
    status: SessionStatus