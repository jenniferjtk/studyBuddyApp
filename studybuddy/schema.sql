-- enable foreign key enforcement in sqlite
pragma foreign_keys = on;

-- ========== core tables ==========

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

-- ========== indexes for speed ==========

create index if not exists idx_availability_user_day
  on availability(user_id, day_of_week, start_min, end_min);

create index if not exists idx_sessions_lookup
  on sessions(status, course_code, day_of_week, start_min);

create index if not exists idx_session_participants_user
  on session_participants(user_id);

-- optional: quick lookup of classmates by course
create index if not exists idx_enrollments_course_user
  on enrollments(course_code, user_id);