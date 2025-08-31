from typing import List
from studybuddy.database.sql_storage import Storage
from studybuddy.domain.models import User, Session, MatchSuggestion
from studybuddy.domain.domain_types import SessionStatus
from studybuddy.app_configs import MIN_MATCH_MINUTES

class StudyBuddyService:

    def __init__(self, db: Storage):
        self.db = db

    # quick existence check for guardrails in CLI
    def user_exists(self, user_id: int) -> bool:
        row = self.db.query_one("select 1 as ok from users where id = :u", {"u": user_id})
        return row is not None

    # navigation helpers for courses
    def list_all_courses(self):
        return self.db.query_all(
            "select code, coalesce(title, '') as title from courses order by code"
        )

    def list_courses_for_user(self, user_id: int):
        return self.db.query_all(
            """
            select c.code, coalesce(c.title,'') as title
            from enrollments e
            join courses c on c.code = e.course_code
            where e.user_id = :u
            order by c.code
            """,
            {"u": user_id}
        )
    # -------- Profiles & Courses (FR1, FR2) --------
    def create_user(self, name: str) -> int:
        self.db.execute("insert into users(name) values(:name)", {"name": name})
        return int(self.db.query_one("select last_insert_rowid() as id")["id"])

    def update_user_name(self, user_id: int, new_name: str) -> None:
        self.db.execute("update users set name = :n where id = :u", {"n": new_name, "u": user_id})

    def delete_user(self, user_id: int) -> None:
        self.db.execute("delete from users where id = :u", {"u": user_id})

    def enroll_course(self, user_id: int, course_code: str, title: str | None = None) -> None:
        if title is not None:
            self.db.execute("insert or ignore into courses(code,title) values(:c,:t)", {"c":course_code, "t":title})
        else:
            self.db.execute("insert or ignore into courses(code) values(:c)", {"c":course_code})
        self.db.execute("""
            insert or ignore into enrollments(user_id, course_code)
            values(:u, :c)
        """, {"u": user_id, "c": course_code})

    def drop_course(self, user_id: int, course_code: str) -> None:
        self.db.execute("delete from enrollments where user_id=:u and course_code=:c", {"u": user_id, "c": course_code})

    # -------- Availability
    # This function adds a user's availability time slots to the database by
   
    def add_availability(self, user_id: int, day_of_week: int, start_min: int, end_min: int) -> int:
        #check if the value for day of week is valid ( aka 0-6) and that the time
        #range is valid within 1 24 hr day ( aka 0-1440)
        if not (0 <= day_of_week <= 6) or not (0 <= start_min < end_min <= 1440):
            raise ValueError("invalid day/time range")
        #creates a new time slot in the availability table telling when the user is available

        self.db.execute("""
            insert into availability(user_id, day_of_week, start_min, end_min)
            values(:user_id,:day_of_week,:start_min,:end_min)
        """, {"user_id":user_id,"day_of_week":day_of_week,"start_min":start_min,"end_min":end_min})
        # return the ID of the new availability slot or row so we can reference it later 
        return int(self.db.query_one("select last_insert_rowid() as id")["id"])

    def remove_availability(self, availability_id: int) -> None:
        self.db.execute("delete from availability where id = :id", {"id": availability_id})

    # -------- Classmates 
    # This function uses the tables "users" and "enrollments" to find classmates
    def find_classmates(self, user_id: int, course_code: str) -> List[User]:
        # Selects classmate id and name from enrollment table for both user
        # Defined classmate as a user who is shares the same course code 
        # as the user who is currently looking (line 89). Exclude user with <> so 
        # They are not included in this select
        rows = self.db.query_all("""
            select users_classmate.id, users_classmate.name
            from enrollments as enrollments_for_me
            join enrollments as enrollments_for_classmate
              on enrollments_for_classmate.course_code = enrollments_for_me.course_code
            join users as users_classmate
              on users_classmate.id = enrollments_for_classmate.user_id
            where enrollments_for_me.user_id = :u
              and enrollments_for_me.course_code = :c
              and enrollments_for_classmate.user_id <> :u
            group by users_classmate.id, users_classmate.name
        """, {"u": user_id, "c": course_code})
        # Create a list of users with their id and names as the classmates for that
        # course code 
        return [User(id=r["id"], name=r["name"]) for r in rows]

    # Suggest Matches
    # Parameters: user_id, course_code, min_minutes
    def suggest_matches(self, user_id: int, course_code: str, min_minutes: int = MIN_MATCH_MINUTES) -> List[MatchSuggestion]:
        # 1 step: Find my availability 2: Find classmates' availability 3: Find overlapping time slots
        # 4: Filter by min_minutes (30) this is a constant defined in app_config
        # (Re-use the same query structure as find_classmates)
        rows = self.db.query_all("""
            with my as (
                select day_of_week, start_min, end_min
                from availability where user_id = :me
            ),
            classmates as (
                select availability.user_id, availability.day_of_week, availability.start_min, availability.end_min
                from availability
                where availability.user_id in (
                    select users_classmate.id
                    from enrollments as enrollments_for_me
                    join enrollments as enrollments_for_classmate
                        on enrollments_for_classmate.course_code = enrollments_for_me.course_code
                    join users as users_classmate
                        on users_classmate.id = enrollments_for_classmate.user_id
                    where enrollments_for_me.user_id = :me
                        and enrollments_for_me.course_code = :course
                        and enrollments_for_classmate.user_id <> :me
                )
            )
            select
                classmates.user_id as partner_id,
                classmates.day_of_week as day_of_week,
                max(my.start_min, classmates.start_min) as overlap_start_min,
                min(my.end_min, classmates.end_min) as overlap_end_min,
                (min(my.end_min, classmates.end_min) - max(my.start_min, classmates.start_min)) as minutes
            from my
            join classmates on my.day_of_week = classmates.day_of_week
            where my.start_min < classmates.end_min
                and classmates.start_min < my.end_min
            group by partner_id, classmates.day_of_week, overlap_start_min, overlap_end_min
            having minutes >= :min
            order by minutes desc, classmates.day_of_week, overlap_start_min
        """, {"me": user_id, "course": course_code, "min": min_minutes})
        return [
            MatchSuggestion(
                partner_id=r["partner_id"],
                day_of_week=r["day_of_week"],
                overlap_start_min=r["overlap_start_min"],
                overlap_end_min=r["overlap_end_min"],
                minutes=r["minutes"],
            ) for r in rows
        ]

    # -------- Sessions
    # This function creates a new study session request between 2 users
    # Parameters: requester_id, invitee_id, course_code, day_of_week, start_min, end_min
    # requester_id: the user who is requesting the session
    # invitee_id: the user who is invited to the session
    # course_code: the course for which the session is being requested
    # day_of_week: the day of the week for the session (0= Monday, 6= Sunday)
    # start_min: the start time of the session in minutes since midnight
    # end_min: the end time of the session in minutes since midnight
    def request_session(self, requester_id: int, invitee_id: int, course_code: str,
                        day_of_week: int, start_min: int, end_min: int) -> int:
        #insert a row into the sessions table with status pending for a potential
        # session with it's date and time 
        self.db.execute("""
            insert into sessions(course_code, day_of_week, start_min, end_min, status)
            values(:c,:d,:s,:e,'pending')
        """, {"c":course_code,"d":day_of_week,"s":start_min,"e":end_min})
        # use the last_insert_rowid function that will grab the last successful
        # row id from the insert and assign it to sid (session id)
        sid = int(self.db.query_one("select last_insert_rowid() as id")["id"])
        # insert a row into the session_participants table with the Requester user 
        # if their response is accepted. Using same session_id
        self.db.execute("""
            insert into session_participants(session_id, user_id, role, response)
            values(:sid,:u,'requester','accepted')
        """, {"sid":sid,"u":requester_id})
       # insert a row into the session_participants table with the Invitee user
       # and their response is pending (awaiting confirmation)
        self.db.execute("""
            insert into session_participants(session_id, user_id, role, response)
            values(:sid,:u,'invitee','pending')
        """, {"sid":sid,"u":invitee_id})
        return sid
# This function handles the response to a session request
# Parameters: session_id, user_id, accept
# session_id: the ID of the session
# user_id: the ID of the user responding to the session
# accept: whether the user accepts or declines the session
# The boolean is taken from the CLI if the user types 'y' then is true else 
# false. Accept is either T or F (boolean) and that's determined by the 
# choice == 10 if statement from the menu. IF the accept == T, then the sessions
# _participants table is updated accordingly with the user and user id
    def respond_session(self, session_id: int, user_id: int, accept: bool) -> None:
        new_resp = "accepted" if accept else "declined"
        self.db.execute("""
            update session_participants
            set response = :r
            where session_id = :sid and user_id = :u
        """, {"r": new_resp, "sid": session_id, "u": user_id})
        if not accept:
            self.db.execute("update sessions set status='declined' where id=:sid", {"sid": session_id})
            return
        # confirm if all accepted by counting all participants (count(*)) if 
        # their response = 1 = accepted. Select '1' because we don't care about
        # column name just if a row exists at all that meets the conditions. Then
        # update the status to confirmed
        self.db.execute("""
            update sessions
            set status = 'confirmed'
            where id = :sid
              and exists (
                select 1 from session_participants
                where session_id = :sid
                group by session_id
                having sum(case when response='accepted' then 1 else 0 end) = count(*)
              )
        """, {"sid": session_id})
# This function lists all confirmed sessions for a given user 
# Parameters: user_id
# Looks at all the sessions join on only sessions where 
# the user is a participant and status is confirmed (all users accepted)
# orders sessions by day_of_week and start_min
# returns a 'dictionary' mapping session IDs to session details. 
# For loop: builds a session object for each row and creates a list of those
# akak List[Session]
    def list_confirmed_sessions_for_user(self, user_id: int) -> List[Session]:
        rows = self.db.query_all("""
            select s.id, s.course_code, s.day_of_week, s.start_min, s.end_min, s.status
            from sessions s
            join session_participants sp on sp.session_id = s.id
            where sp.user_id = :u and s.status = 'confirmed'
            order by s.day_of_week, s.start_min
        """, {"u": user_id})
        return [Session(
            id=r["id"], course_code=r["course_code"], day_of_week=r["day_of_week"],
            start_min=r["start_min"], end_min=r["end_min"], status=SessionStatus(r["status"])
        ) for r in rows]