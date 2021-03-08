drop table if exists users;
CREATE TABLE users (
  email TEXT PRIMARY KEY,
  password TEXT NOT NULL,
  firstname TEXT NOT NULL,
  familyname TEXT NOT NULL,
  gender TEXT NOT NULL,
  city TEXT NOT NULL,
  country TEXT NOT NULL
);

drop table if exists messages;
CREATE TABLE messages (
  id INTEGER PRIMARY KEY autoincrement,
  message TEXT NOT NULL,
  fromUser TEXT NOT NULL,
  toUser TEXT NOT NULL,
  FOREIGN KEY (fromUser) REFERENCES users(id),
  FOREIGN KEY (toUser) REFERENCES users(id)
);

drop table if exists signedInUsers;
CREATE TABLE signedInUsers (
  email TEXT,
  token TEXT NOT NULL PRIMARY KEY


);
