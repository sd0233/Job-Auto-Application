from flask import Flask, render_template_string, jsonify
import sqlite3
import os

app = Flask(__name__)

# Initialize DB on startup
import sqlite3, os
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, '..', 'jobs.db')
try:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, company TEXT, location TEXT,
            platform TEXT, url TEXT, job_key TEXT UNIQUE,
            description TEXT, ai_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
except:
    pass
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'jobs.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status='shortlisted'")
    shortlisted = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status='skipped_low_score'")
    skipped = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status='scraped'")
    scraped = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE platform='naukri'")
    naukri = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE platform='linkedin'")
    linkedin = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE platform='indeed'")
    indeed = cursor.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "shortlisted": shortlisted,
        "skipped": skipped,
        "scraped": scraped,
        "naukri": naukri,
        "linkedin": linkedin,
        "indeed": indeed
    }

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Job Application Bot Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; }

        .header {
            background: linear-gradient(135deg, #1e3a8a, #3730a3);
            padding: 24px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 22px; font-weight: 700; }
        .header span { font-size: 13px; color: #93c5fd; }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            padding: 24px 32px;
        }
        .stat-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid #334155;
        }
        .stat-card .number {
            font-size: 36px;
            font-weight: 800;
            color: #60a5fa;
        }
        .stat-card .label {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-card.green .number { color: #34d399; }
        .stat-card.red .number   { color: #f87171; }
        .stat-card.yellow .number { color: #fbbf24; }

        .filters {
            padding: 0 32px 16px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .filters input, .filters select {
            background: #1e293b;
            border: 1px solid #334155;
            color: #e2e8f0;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            outline: none;
        }
        .filters input { width: 250px; }

        .table-wrap {
            padding: 0 32px 32px;
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        thead tr {
            background: #1e293b;
            color: #94a3b8;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }
        th, td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #1e293b;
        }
        tbody tr:hover { background: #1e293b; }
        tbody tr:nth-child(even) { background: #0f172a; }

        .badge {
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        .badge.shortlisted  { background: #064e3b; color: #34d399; }
        .badge.scraped      { background: #1e3a8a; color: #93c5fd; }
        .badge.skipped      { background: #450a0a; color: #f87171; }

        .platform-badge {
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        .platform-badge.naukri   { background: #422006; color: #fb923c; }
        .platform-badge.linkedin { background: #172554; color: #60a5fa; }
        .platform-badge.indeed   { background: #1a1a2e; color: #a78bfa; }

        .score-badge {
            font-weight: 700;
            font-size: 13px;
        }
        .score-high { color: #34d399; }
        .score-mid  { color: #fbbf24; }
        .score-low  { color: #f87171; }

        a.job-link {
            color: #60a5fa;
            text-decoration: none;
        }
        a.job-link:hover { text-decoration: underline; }

        .no-data {
            text-align: center;
            padding: 60px;
            color: #475569;
            font-size: 15px;
        }
    </style>
</head>
<body>

<div class="header">
    <h1>🤖 Job Application Bot Dashboard</h1>
    <span>Total in DB: {{ stats.total }} jobs</span>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <div class="number">{{ stats.total }}</div>
        <div class="label">Total Jobs</div>
    </div>
    <div class="stat-card green">
        <div class="number">{{ stats.shortlisted }}</div>
        <div class="label">Shortlisted</div>
    </div>
    <div class="stat-card red">
        <div class="number">{{ stats.skipped }}</div>
        <div class="label">Skipped</div>
    </div>
    <div class="stat-card yellow">
        <div class="number">{{ stats.scraped }}</div>
        <div class="label">Scraped</div>
    </div>
    <div class="stat-card">
        <div class="number">{{ stats.naukri }}</div>
        <div class="label">Naukri</div>
    </div>
    <div class="stat-card">
        <div class="number">{{ stats.linkedin }}</div>
        <div class="label">LinkedIn</div>
    </div>
    <div class="stat-card">
        <div class="number">{{ stats.indeed }}</div>
        <div class="label">Indeed</div>
    </div>
</div>

<div class="filters">
    <input type="text" id="searchInput" placeholder="🔍 Search title or company..." onkeyup="filterTable()">
    <select id="platformFilter" onchange="filterTable()">
        <option value="">All Platforms</option>
        <option value="naukri">Naukri</option>
        <option value="linkedin">LinkedIn</option>
        <option value="indeed">Indeed</option>
    </select>
    <select id="statusFilter" onchange="filterTable()">
        <option value="">All Status</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="scraped">Scraped</option>
        <option value="skipped_low_score">Skipped</option>
    </select>
</div>

<div class="table-wrap">
    {% if jobs %}
    <table id="jobTable">
        <thead>
            <tr>
                <th>#</th>
                <th>Title</th>
                <th>Company</th>
                <th>Location</th>
                <th>Platform</th>
                <th>Score</th>
                <th>Status</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
        {% for job in jobs %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>
                {% if job.url %}
                    <a class="job-link" href="{{ job.url }}" target="_blank">{{ job.title }}</a>
                {% else %}
                    {{ job.title }}
                {% endif %}
            </td>
            <td>{{ job.company or '-' }}</td>
            <td>{{ job.location or '-' }}</td>
            <td>
                <span class="platform-badge {{ job.platform }}">
                    {{ job.platform }}
                </span>
            </td>
            <td>
                {% if job.ai_score %}
                    <span class="score-badge
                        {% if job.ai_score >= 7 %}score-high
                        {% elif job.ai_score >= 5 %}score-mid
                        {% else %}score-low{% endif %}">
                        {{ job.ai_score }}/10
                    </span>
                {% else %}
                    <span style="color:#475569">-</span>
                {% endif %}
            </td>
            <td>
                <span class="badge {{ job.status }}">
                    {{ job.status }}
                </span>
            </td>
            <td style="color:#64748b">
                {{ job.applied_at[:10] if job.applied_at else '-' }}
            </td>
        </tr>
        {% endfor %}
        </tbody>
    </table>
    {% else %}
    <div class="no-data">No jobs in database yet. Run the bot first.</div>
    {% endif %}
</div>

<script>
function filterTable() {
    const search   = document.getElementById('searchInput').value.toLowerCase();
    const platform = document.getElementById('platformFilter').value.toLowerCase();
    const status   = document.getElementById('statusFilter').value.toLowerCase();
    const rows     = document.querySelectorAll('#jobTable tbody tr');

    rows.forEach(row => {
        const text     = row.innerText.toLowerCase();
        const matchSearch   = text.includes(search);
        const matchPlatform = platform === '' || text.includes(platform);
        const matchStatus   = status === ''   || text.includes(status);
        row.style.display = (matchSearch && matchPlatform && matchStatus) ? '' : 'none';
    });
}
</script>

</body>
</html>
"""

@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def index():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM applications ORDER BY applied_at DESC"
        )
        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        stats = get_stats()
    except Exception:
        jobs = []
        stats = {
            "total": 0, "shortlisted": 0, "skipped": 0,
            "scraped": 0, "naukri": 0, "linkedin": 0, "indeed": 0
        }
    return render_template_string(TEMPLATE, jobs=jobs, stats=stats)

@app.route("/api/jobs")
def api_jobs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY applied_at DESC")
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(jobs)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)