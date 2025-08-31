from studybuddy.application.services import StudyBuddyService
from studybuddy.domain.time_parsers import parse_range
from .formatting_command_line import print_users, print_match_suggestions, print_sessions

import re

# ---------------------------------------
# Robust input helpers & validators
# ---------------------------------------

COURSE_CODE_PATTERN = re.compile(r"^[A-Z]{3,4}-\d{4}$")

def prompt_int(label: str):
    """Prompt until a numeric integer is entered, or 'q' to cancel (returns None)."""
    while True:
        raw = input(label).strip()
        if raw.lower() in {"q", "quit", "exit"}:
            print("canceled.")
            return None
        try:
            return int(raw)
        except ValueError:
            print("Please enter a numeric id (or 'q' to cancel).")

def prompt_course_code(label: str):
    """Accept codes like 'CPSC-3720' or 'BIO-1220' (3–4 letters, hyphen, 4 digits)."""
    while True:
        raw = input(label).strip()
        if raw.lower() in {"q", "quit", "exit"}:
            print("canceled.")
            return None
        candidate = raw.upper()              # normalize case
        if COURSE_CODE_PATTERN.match(candidate):
            return candidate
        print("Invalid code. Use format like 'CPSC-3720' or 'BIO-1220' (3–4 letters, hyphen, 4 digits). Or 'q' to cancel.")

def prompt_range(label: str):
    """Prompt for 'Mon 13:00-15:00' with retries or cancel."""
    while True:
        raw = input(label).strip()
        if raw.lower() in {"q", "quit", "exit"}:
            print("canceled.")
            return None
        try:
            return parse_range(raw)
        except Exception:
            print('Invalid format. Example: Mon 13:00-15:30. Try again or "q" to cancel.')

def confirm(label: str) -> bool:
    """Ask for y/n confirmation. Default is No."""
    ans = input(f"{label} (y/N): ").strip().lower()
    return ans in {"y", "yes"}

def ensure_user_exists(svc: StudyBuddyService, user_id: int) -> bool:
    """
    Ensure a user id is real; print a hint if not.
    Requires: StudyBuddyService.user_exists(user_id) -> bool
    """
    if user_id is None:
        return False
    if not svc.user_exists(user_id):
        print(f"User id {user_id} not found. Create a user first (option 1).")
        return False
    return True

# ---------------------------------------
# Menu
# ---------------------------------------

def display_menu():
    print("""
studybuddy
1) create user (guided)
2) update user name
3) enroll course
4) drop course
5) add availability
6) remove availability
7) find classmates
8) suggest matches
9) request session
10) respond to request
11) my confirmed sessions
0) exit
""")

def handle_choice(svc: StudyBuddyService):
    while True:
        display_menu()
        choice = input("choice: ").strip()

        # ---------------------------
        # 1) CREATE USER (GUIDED)
        # ---------------------------
        if choice == "1":
            name = ""
            while not name:
                name = input("Your name: ").strip()
                if not name:
                    print("Name cannot be empty.")
            uid = svc.create_user(name)
            print(f"✅ Created user id {uid} for '{name}'")

            # Guided: immediately offer to enroll courses
            if confirm("Would you like to add your courses now?"):
                print("Enter each course code like 'CPSC-3720'. Type 'q' to stop.")
                while True:
                    course = prompt_course_code("Course code (or 'q' to finish): ")
                    if course is None:
                        break
                    title = input("Course title (optional): ").strip() or None
                    svc.enroll_course(uid, course, title)
                    print(f"Added {course} to your profile.")
                print("Done adding courses.")
            continue

        # ---------------------------
        # 2) UPDATE USER NAME
        # ---------------------------
        elif choice == "2":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            new = input("New name: ").strip()
            if not new:
                print("Name cannot be empty.")
                continue
            svc.update_user_name(uid, new)
            print("Updated.")

        # ---------------------------
        # 3) ENROLL COURSE
        # ---------------------------
        elif choice == "3":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            while True:
                course = prompt_course_code("Course code (e.g., CPSC-3720) or 'q' to cancel: ")
                if course is None:
                    break
                title = input("Course title (optional): ").strip() or None
                svc.enroll_course(uid, course, title)
                print(f"Enrolled in {course}.")

        # ---------------------------
        # 4) DROP COURSE  (confirm)
        # ---------------------------
        elif choice == "4":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            while True:
                course = prompt_course_code("Course code to drop (e.g., CPSC-3720) or 'q' to cancel: ")
                if course is None:
                    break
                if not confirm(f"Drop {course} for user {uid}?"):
                    print("Canceled.")
                    break
                # If user wasn't enrolled, this is a no-op (insert-or-ignore pattern elsewhere)
                svc.drop_course(uid, course)
                print("Dropped.")

        # ---------------------------
        # 5) ADD AVAILABILITY
        # ---------------------------
        elif choice == "5":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            while True:
                rng = prompt_range('Range like "Mon 13:00-15:00" (or q to cancel): ')
                if rng is None:
                    break
                dow, s, e = rng
                try:
                    aid = svc.add_availability(uid, dow, s, e)
                    print(f"Availability id {aid} added.")
                except ValueError as ex:
                    print(f"Invalid range: {ex}")

        # ---------------------------
        # 6) REMOVE AVAILABILITY  (confirm)
        # ---------------------------
        elif choice == "6":
            while True:
                aid = prompt_int("availability id (or 'q' to cancel): ")
                if aid is None:
                    break
                if not confirm(f"Remove availability id {aid}?"):
                    print("Canceled.")
                    break
                svc.remove_availability(aid)
                print("Removed.")

        # ---------------------------
        # 7) FIND CLASSMATES
        # ---------------------------
        elif choice == "7":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            course = prompt_course_code("Course code (e.g., CPSC-3720) or 'q' to cancel: ")
            if course is None:
                continue
            users = svc.find_classmates(uid, course)
            print_users(users)

        # ---------------------------
        # 8) SUGGEST MATCHES
        # ---------------------------
        elif choice == "8":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            course = prompt_course_code("Course code (e.g., CPSC-3720) or 'q' to cancel: ")
            if course is None:
                continue
            mins_raw = input("Min minutes overlap (default 30): ").strip()
            try:
                mins = int(mins_raw) if mins_raw else 30
            except ValueError:
                print("Invalid number. Using default 30.")
                mins = 30
            suggestions = svc.suggest_matches(uid, course, mins)
            print_match_suggestions(suggestions)

        # ---------------------------
        # 9) REQUEST SESSION
        # ---------------------------
        elif choice == "9":
            requester = prompt_int("requester id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, requester):
                continue
            invitee = prompt_int("invitee id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, invitee):
                continue
            course = prompt_course_code("Course code (e.g., CPSC-3720) or 'q' to cancel: ")
            if course is None:
                continue
            rng = prompt_range('Time window like "Mon 13:00-15:00" (or q to cancel): ')
            if rng is None:
                continue
            dow, s, e = rng
            sid = svc.request_session(requester, invitee, course, dow, s, e)
            print(f"Session id {sid} created (pending).")

        # ---------------------------
        # 10) RESPOND TO REQUEST
        # ---------------------------
        elif choice == "10":
            sid = prompt_int("session id (or 'q' to cancel): ")
            if sid is None:
                continue
            uid = prompt_int("your user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            decision = input("Accept? (y/n): ").strip().lower().startswith("y")
            # pass the decision into respond_session fxn 
            svc.respond_session(sid, uid, decision)
            print("Response recorded.")

        # ---------------------------
        # 11) MY CONFIRMED SESSIONS
        # ---------------------------
        elif choice == "11":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            sessions = svc.list_confirmed_sessions_for_user(uid)
            print_sessions(sessions)

        # ---------------------------
        # EXIT
        # ---------------------------
        elif choice == "0":
            print("bye!")
            break

        else:
            print("invalid choice.")