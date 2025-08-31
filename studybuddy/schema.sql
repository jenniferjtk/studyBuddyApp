-- enable foreign key enforcement in sqlite
pragma foreign_keys = on;
'''
This schema defines the core data model for the StudyBuddy system
Users are stored in the users table, each with a unique int id
Availability also uses a unique int id to track each time slot
Courses are stored in the courses table identified by their course
code string, which is the primary key (PK)
 The enrollments table ties users -> courses, Primary key is the combination
of user_id + course_code so that the same student cannot be enrolled
in the same course more than once. Study sessions are stored in the
sessions table, each with a unique integer id, and participants are
tracked in session_participants, where the combination of session_id
+ user_id ensures a user can only appear once per session
'''
--Cascade ensures that when a user or session is deleted, their related data is also removed
-- Extra constraints ensure data is valid: days of the week must be
-- between 0 and 6, time slots must be within a 24-hour range with start
-- earlier than end, session statuses can only be pending, confirmed,
-- declined, or canceled, participant roles must be requester or invitee,
-- and responses must be accepted, pending, or declined.


-- MAIN TABLES:

create table if not exists users (
  id integer primary key,
  name text not null
);

create table if not exists courses (
  code text primary key,
  title text
);

-- many-to-many between users and courses
create table if not exists enrollments (
  user_id integer not null,
  course_code text not null,
  primary key (user_id, course_code),
  foreign key (user_id) references users(id) on delete cascade,
  foreign key (course_code) references courses(code) on delete cascade
);

-- per-user weekly availability windows
create table if not exists availability (
  id integer primary key,
  user_id integer not null,
  day_of_week integer not null,  -- 0=mon … 6=sun
  start_min integer not null,    -- minutes after midnight (e.g., 13:00 -> 780)
  end_min integer not null,      -- must be > start_min
  foreign key (user_id) references users(id) on delete cascade,
  check (day_of_week between 0 and 6),
  check (start_min >= 0 and end_min <= 1440 and start_min < end_min)
);

-- study sessions (proposed or confirmed time slots)
create table if not exists sessions (
  id integer primary key,
  course_code text not null,
  day_of_week integer not null,
  start_min integer not null,
  end_min integer not null,
  status text not null check (status in ('pending','confirmed','declined','canceled')),
  foreign key (course_code) references courses(code) on delete cascade,
  check (day_of_week between 0 and 6),
  check (start_min >= 0 and end_min <= 1440 and start_min < end_min)
);

-- participants and their responses per session
create table if not exists session_participants (
  session_id integer not null,
  user_id integer not null,
  role text not null check (role in ('requester','invitee')),
  response text not null check (response in ('accepted','pending','declined')),
  primary key (session_id, user_id),
  foreign key (session_id) references sessions(id) on delete cascade,
  foreign key (user_id) references users(id) on delete cascade
);

