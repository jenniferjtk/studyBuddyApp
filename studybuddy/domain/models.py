from dataclasses import dataclass
from studybuddy.domain.domain_types import SessionStatus, ParticipantRole, ParticipantResponse

@dataclass
class User:
    id: int
    name: str

@dataclass
class Availability:
    id: int
    user_id: int
    day_of_week: int
    start_min: int
    end_min: int

@dataclass
class Session:
    id: int
    course_code: str
    day_of_week: int
    start_min: int
    end_min: int
    status: SessionStatus

@dataclass
class SessionParticipant:
    session_id: int
    user_id: int
    role: ParticipantRole
    response: ParticipantResponse

@dataclass
class MatchSuggestion:
    partner_id: int
    day_of_week: int
    overlap_start_min: int
    overlap_end_min: int
    minutes: int