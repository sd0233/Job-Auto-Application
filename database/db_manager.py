import sqlite3

DB_PATH = "jobs.db"

def save_job(job: dict):
    """Insert a job into DB. Skip if already exists (job_key unique)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO applications 
            (title, company, location, platform, url, job_key, description, ai_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("platform"),
            job.get("url"),
            job.get("job_key"),
            job.get("description", ""),
            job.get("ai_score", 0),
            job.get("status", "pending")
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # already exists
    finally:
        conn.close()

def get_applied_keys():
    """Return set of all job_keys already in DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT job_key FROM applications")
    keys = {row[0] for row in cursor.fetchall()}
    conn.close()
    return keys

def update_status(job_key, status):
    """Update application status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE applications SET status=? WHERE job_key=?",
        (status, job_key)
    )
    conn.commit()
    conn.close()

def get_all_jobs():
    """Return all applications for dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM applications ORDER BY applied_at DESC"
    )
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs

def get_stats():
    """Return summary stats."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    stats = dict(cursor.fetchall())
    conn.close()
    return stats