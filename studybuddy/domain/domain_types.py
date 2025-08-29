from enum import Enum

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