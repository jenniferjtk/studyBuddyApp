# app.py
from types import SimpleNamespace
from db import connect, init_db, student_upsert, student_get
from services import StudyBuddyService

# ===== helpers for future steps (kept minimal) ===============================
DAYS = ["mon","tue","wed","thu","fri","sat","sun"]
def day_to_int(d: str) -> int:
    return DAYS.index(d.lower())

def mins(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

# ===== dependency wiring =====================================================
def make_service():
    conn = connect()
    init_db(conn)

    # bind db helpers into a tiny namespace so service can call them as methods
    db_helpers = SimpleNamespace(
        student_upsert=lambda s: student_upsert(conn, s),
        student_get=lambda sid: student_get(conn, sid),

        # placeholders for later steps; add as you implement in db.py
        # course_get_by_code=lambda code: ...,
        # course_ensure=lambda code, title: ...,
        # enrollment_add=lambda sid, cid: ...,
        # availability_list=lambda sid: ...,
        # etc.
    )
    return StudyBuddyService(db_helpers)

# ===== interactive loop ======================================================
def interactive_loop(svc: StudyBuddyService):
    while True:
        print("\nStudyBuddy Menu")
        print("1) Create/Update Profile")
        print("2) View Profile")
        print("— upcoming —")
        print("3) Add/Remove Course")
        print("4) Add/Remove Availability")
        print("5) Suggest Matches")
        print("6) Request/Respond Session")
        print("0) Exit")
        choice = input("Choose option: ").strip()

        try:
            if choice == "1":
                sid = input("Student ID: ").strip()
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                svc.create_or_update_profile(sid, name, email)
                print("Profile saved.")
            elif choice == "2":
                sid = input("Student ID: ").strip()
                prof = svc.get_profile(sid)
                print(f"ID: {prof['id']}  Name: {prof['name']}  Email: {prof['email']}")
            elif choice == "3":
                print("Coming soon (next build step).")
            elif choice == "4":
                print("Coming soon (next build step).")
            elif choice == "5":
                print("Coming soon (next build step).")
            elif choice == "6":
                print("Coming soon (next build step).")
            elif choice == "0":
                break
            else:
                print("Invalid choice. Try again.")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    svc = make_service()
    interactive_loop(svc)