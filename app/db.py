"""SQLiteへの接続とスキーマ初期化。"""
import os
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zipcode TEXT NOT NULL,
    prefecture TEXT NOT NULL,
    city TEXT NOT NULL,
    town TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS elections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    election_type TEXT NOT NULL,
    prefecture TEXT,
    city TEXT,
    announcement_date TEXT NOT NULL,
    vote_date TEXT NOT NULL,
    vote_start_time TEXT NOT NULL DEFAULT '07:00',
    vote_end_time TEXT NOT NULL DEFAULT '20:00',
    status TEXT NOT NULL DEFAULT 'scheduled',
    source_url TEXT NOT NULL,
    source_updated_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fetch_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL,
    success INTEGER NOT NULL,
    message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS polling_places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prefecture TEXT NOT NULL,
    city TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    open_time TEXT NOT NULL,
    close_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS early_voting_places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER NOT NULL REFERENCES elections(id),
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    open_time TEXT NOT NULL,
    close_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER NOT NULL REFERENCES elections(id),
    name TEXT NOT NULL,
    party TEXT,
    profile TEXT,
    source_url TEXT
);

CREATE TABLE IF NOT EXISTS election_gazettes (
    election_id INTEGER PRIMARY KEY REFERENCES elections(id),
    content TEXT NOT NULL,
    source_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS election_results (
    candidate_id INTEGER PRIMARY KEY REFERENCES candidates(id),
    votes INTEGER,
    elected INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS notification_settings (
    region_id INTEGER NOT NULL REFERENCES regions(id),
    election_type TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    days_before TEXT NOT NULL DEFAULT '7,1,0',
    PRIMARY KEY (region_id, election_type)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    election_id INTEGER NOT NULL REFERENCES elections(id),
    notify_type TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    message TEXT NOT NULL,
    UNIQUE (region_id, election_id, notify_type)
);

CREATE TABLE IF NOT EXISTS vote_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    election_id INTEGER NOT NULL REFERENCES elections(id),
    voted_at TEXT NOT NULL,
    UNIQUE (region_id, election_id)
);
"""


def get_db_path() -> str:
    return os.environ.get("VOTE_REMINDER_DB", "data/vote_reminder.db")


def connect() -> sqlite3.Connection:
    path = get_db_path()
    if path != ":memory:":
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
