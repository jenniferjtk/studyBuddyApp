from studybuddy.application.services import StudyBuddyService
from studybuddy.domain.time_parsers import parse_range
from .formatting_command_line import (
    print_users, print_match_suggestions, print_sessions,
    print_courses, pick_course_from_rows
)

# ---------- input helpers (no crashes on bad input) ----------

def prompt_int(label: str):
    while True:
        raw = input(f"{label}").strip()
        if raw.lower() in {"q", "quit", "exit"}:
            print("canceled.")
            return None
        try:
            return int(raw)
        except ValueError:
            print("please enter a numeric id (or 'q' to cancel).")

def prompt_range(label: str):
    while True:
        raw = input(label).strip()
        if raw.lower() in {"q", "quit", "exit"}:
            print("canceled.")
            return None
        try:
            return parse_range(raw)
        except Exception:
            print('invalid format. example: Mon 13:00-15:00. try again or "q" to cancel.')

def ensure_user_exists(svc: StudyBuddyService, user_id: int) -> bool:
    if user_id is None:
        return False
    if not svc.user_exists(user_id):
        print(f"user id {user_id} not found. create a user first (option 1).")
        return False
    return True

# ---------- menu ----------

def display_menu():
    print("""
studybuddy
1) create user
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
12) list all courses
13) list my courses
0) exit
""")

def handle_choice(svc: StudyBuddyService):
    while True:
        display_menu()
        choice = input("choice: ").strip()

        if choice == "1":
            name = input("name: ").strip()
            uid = svc.create_user(name)
            print(f"created user id {uid}")

        elif choice == "2":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            new = input("new name: ").strip()
            svc.update_user_name(uid, new)
            print("updated.")

        elif choice == "3":
            # Enroll: allow user to A) pick existing course from a numbered list OR B) type a new code
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            print("choose an existing course or press Enter to type a new code.")
            existing = svc.list_all_courses()
            if existing:
                selected = pick_course_from_rows(existing, "select number (or Enter to type new, q to cancel): ")
            else:
                selected = None

            if selected is None:
                # either canceled or user wants to type a new code
                raw = input("course code (e.g., CPSC-3600) or 'q' to cancel: ").strip()
                if raw.lower() in {"q", "quit", "exit"}:
                    print("canceled.")
                    continue
                course = raw
                title = input("course title (optional): ").strip() or None
            else:
                course = selected
                title = None  # already exists
            svc.enroll_course(uid, course, title)
            print(f"enrolled in {course}.")

        elif choice == "4":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            # drop: pick from *my* courses (numbered), avoids typos
            my = svc.list_courses_for_user(uid)
            if not my:
                print("you have no enrolled courses to drop.")
                continue
            course = pick_course_from_rows(my, "select course to drop (or q to cancel): ")
            if course is None:
                continue
            svc.drop_course(uid, course)
            print(f"dropped {course}.")

        elif choice == "5":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            rng = prompt_range('range like "Mon 13:00-15:00" (or q to cancel): ')
            if rng is None:
                continue
            dow, s, e = rng
            aid = svc.add_availability(uid, dow, s, e)
            print(f"availability id {aid} added.")

        elif choice == "6":
            aid = prompt_int("availability id (or 'q' to cancel): ")
            if aid is None:
                continue
            svc.remove_availability(aid)
            print("removed.")

        elif choice == "7":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            # ask which course to search within (from user’s courses)
            my = svc.list_courses_for_user(uid)
            if not my:
                print("you have no enrolled courses. enroll first (option 3).")
                continue
            course = pick_course_from_rows(my, "find classmates in which course? (or q to cancel): ")
            if course is None:
                continue
            users = svc.find_classmates(uid, course)
            print_users(users)

        elif choice == "8":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            my = svc.list_courses_for_user(uid)
            if not my:
                print("you have no enrolled courses. enroll first (option 3).")
                continue
            course = pick_course_from_rows(my, "suggest matches for which course? (or q to cancel): ")
            if course is None:
                continue
            mins_raw = input("min minutes overlap (default 30): ").strip()
            try:
                mins = int(mins_raw) if mins_raw else 30
            except ValueError:
                print("invalid number. using default 30.")
                mins = 30
            suggestions = svc.suggest_matches(uid, course, mins)
            print_match_suggestions(suggestions)

        elif choice == "9":
            requester = prompt_int("requester id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, requester):
                continue
            # pick course from requester’s courses
            my = svc.list_courses_for_user(requester)
            if not my:
                print("you have no enrolled courses. enroll first (option 3).")
                continue
            course = pick_course_from_rows(my, "course for the session (or q to cancel): ")
            if course is None:
                continue

            invitee = prompt_int("invitee id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, invitee):
                continue

            rng = prompt_range('time window like "Mon 13:00-15:00" (or q to cancel): ')
            if rng is None:
                continue
            dow, s, e = rng

            sid = svc.request_session(requester, invitee, course, dow, s, e)
            print(f"session id {sid} created (pending).")

        elif choice == "10":
            sid = prompt_int("session id (or 'q' to cancel): ")
            if sid is None:
                continue
            uid = prompt_int("your user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            decision = input("accept? (y/n): ").strip().lower().startswith("y")
            svc.respond_session(sid, uid, decision)
            print("response recorded.")

        elif choice == "11":
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            sessions = svc.list_confirmed_sessions_for_user(uid)
            print_sessions(sessions)

        elif choice == "12":
            # list all courses in the system
            courses = svc.list_all_courses()
            print_courses(courses)

        elif choice == "13":
            # list courses for a specific user (then optionally select one)
            uid = prompt_int("user id (or 'q' to cancel): ")
            if not ensure_user_exists(svc, uid):
                continue
            courses = svc.list_courses_for_user(uid)
            print_courses(courses)

        elif choice == "0":
            print("bye!")
            break

        else:
            print("invalid choice.")