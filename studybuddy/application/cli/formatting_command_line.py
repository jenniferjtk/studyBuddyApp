from studybuddy.domain.domain_types import SessionStatus
from studybuddy.app_configs import INT_TO_WEEKDAY
from studybuddy.domain.time_parsers import minutes_to_hhmm

def print_users(users):
    if not users:
        print("no users.")
        return
    for u in users:
        print(f"- id {u.id} | {u.name}")

def print_match_suggestions(suggestions):
    if not suggestions:
        print("no overlaps found.")
        return
    print("suggested matches:")
    for s in suggestions:
        dow = INT_TO_WEEKDAY.get(s.day_of_week, str(s.day_of_week))
        print(f"- partner {s.partner_id} | {dow} | {minutes_to_hhmm(s.overlap_start_min)} - {minutes_to_hhmm(s.overlap_end_min)} ({s.minutes} min)")

def print_sessions(sessions):
    if not sessions:
        print("no confirmed sessions.")
        return
    for s in sessions:
        dow = INT_TO_WEEKDAY.get(s.day_of_week, str(s.day_of_week))
        print(f"- [{SessionStatus(s.status).value}] {s.course_code} | {dow} | {minutes_to_hhmm(s.start_min)} - {minutes_to_hhmm(s.end_min)} (id {s.id})")