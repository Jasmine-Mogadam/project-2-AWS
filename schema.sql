DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    firstname TEXT,
    lastname TEXT,
    email TEXT,
    address TEXT,
    word_count INTEGER DEFAULT 0
);