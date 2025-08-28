-- db/schema.sql
pragma foreign_keys = on;

create table if not exists students(
  id    text primary key,
  name  text not null,
  email text not null unique
);

create table if not exists courses(
  id    text primary key,
  code  text not null unique,
  title text
);

create table if not exists student_courses(
  student_id text not null,
  course_id  text not null,
  primary key(student_id, course_id),
  foreign key(student_id) references students(id) on delete cascade,
  foreign key(course_id)  references courses(id)  on delete cascade
);

create table if not exists availability(
  id         text primary key,
  student_id text not null,
  day        integer not null check(day between 0 and 6),
  start_min  integer not null check(start_min between 0 and 1439),
  end_min    integer not null check(end_min between 1 and 1440),
  foreign key(student_id) references students(id) on delete cascade,
  check(end_min > start_min)
);

create table if not exists sessions(
  id           text primary key,
  course_id    text not null,
  requester_id text not null,
  peer_id      text not null,
  day          integer not null check(day between 0 and 6),
  start_min    integer not null check(start_min between 0 and 1439),
  end_min      integer not null check(end_min between 1 and 1440),
  status       text not null check(status in ('PENDING','ACCEPTED','DECLINED')),
  foreign key(course_id) references courses(id) on delete cascade,
  foreign key(requester_id) references students(id) on delete cascade,
  foreign key(peer_id) references students(id) on delete cascade,
  check(end_min > start_min)
);

-- helpful indexes
create index if not exists idx_sc_course on student_courses(course_id);
create index if not exists idx_avail_student_day on availability(student_id, day);
create index if not exists idx_sess_req_day on sessions(requester_id, day);
create index if not exists idx_sess_peer_day on sessions(peer_id, day);