from dataclasses import dataclass
from studybuddy.domain.domain_types import SessionStatus, ParticipantRole, ParticipantResponse

# This file defines the data models used throughout the application using dataclasses
# Each class represents one of the main functions ie User, Avail. Sesion, Session Particpant etc.
# These are used to mirror the database schema (in schema.sql
# encorporate the enums defined earlier 
# 
@dataclass
class User:
    #Represents a student in the system (row in users table)
    # Comes directly from the users table in the database
    #The service layer will create User objects after reading rows from the database.
    id: int
    name: str

@dataclass
class Availability:
    #Represents one weekly availability block for a user (row in availability table)
    # This comes directly from the availability table in the database
    id: int
    user_id: int
    day_of_week: int
    start_min: int
    end_min: int

@dataclass
class Session:
    #Represents a proposed or confirmed study session (row in sessions table)
    # course_code links it to the relevant course, and status comes from the SessionStatus enum.
    id: int
    course_code: str
    day_of_week: int
    start_min: int
    end_min: int
    status: SessionStatus

@dataclass
class SessionParticipant:
    #Represents a user's role and response in a session (row in session_participants table)
    session_id: int
    user_id: int
    role: ParticipantRole
    response: ParticipantResponse

@dataclass
class MatchSuggestion:
    #Represents a suggested study partner and overlapping availability (computed, not stored)
    # this is a helper object for the suggestions 
    partner_id: int
    day_of_week: int
    overlap_start_min: int
    overlap_end_min: int
    minutes: int