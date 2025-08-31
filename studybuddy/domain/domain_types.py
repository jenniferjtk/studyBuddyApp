from enum import Enum

'''
This file defines enums that represent the allowed values for different pieces of the Study Buddy system. 
Each enum is built on top of str so its members act like both strings and constants
So we can pass SessionStatus.confirmed directly into SQL and it will be 
stored as the string "confirmed" in the database, and when you read 
rows back from the database you can normalize into enums again by calling 
SessionStatus(row["status"]). Ensures the data you get from the database is 
always a valid state (pending, confirmed, declined, canceled etc) The enums 
line up directly with the database schema check constraints: 
SessionStatus matches the status column in the sessions table, ParticipantRole matches 
the role column in session_participants, and 
ParticipantResponse matches the response column in session_participants
'''
class SessionStatus(str, Enum):
    pending   = "pending"
    confirmed = "confirmed"
    declined  = "declined"
    canceled  = "canceled"

class ParticipantRole(str, Enum):
    requester = "requester"
    invitee   = "invitee"

class ParticipantResponse(str, Enum):
    accepted = "accepted"
    pending  = "pending"
    declined = "declined"