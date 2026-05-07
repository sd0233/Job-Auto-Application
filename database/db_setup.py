import sqlite3
import os

DB_PATH = "jobs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT NOT NULL,
            company       TEXT,
            location      TEXT,
            platform      TEXT,
            url           TEXT,
            job_key       TEXT UNIQUE,
            description   TEXT,
            ai_score      INTEGER DEFAULT 0,
            status        TEXT DEFAULT 'pending',
            applied_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")

if __name__ == "__main__":
    init_db()