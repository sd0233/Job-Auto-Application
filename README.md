# 🤖 Job Application Bot

iAn end-to-end automated job application system that scrapes, scores, and applies to jobs daily — without any manual effort.

## 🚀 What It Does

- Scrapes fresh job listings daily from Naukri, LinkedIn, Indeed
- Filters jobs by experience range (0-5 years) and keywords
- AI scores each job (1-10) against your resume using Groq LLaMA
- Auto-applies to shortlisted jobs (score ≥ 6) on Naukri
- Logs all applications to SQLite database
- Flask dashboard to view all applications with filters
- Runs automatically every morning at 9 AM via scheduler

## 📊 Results

- 700+ jobs scraped per run
- 30-40 applications sent daily automatically
- AI filtering removes irrelevant jobs before applying

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python, Selenium, BeautifulSoup |
| AI Scoring | Groq API (LLaMA 3.1) |
| Database | SQLite |
| Dashboard | Flask |
| Scheduler | Python Schedule |
| Version Control | Git |

## 📁 Project Structure
job-application-bot/
├── scrapers/          # Naukri, LinkedIn, Indeed scrapers
├── applicators/       # Auto-apply modules
├── ai_engine/         # Job scoring + cover letter generation
├── filters/           # Experience and keyword filters
├── database/          # SQLite setup and manager
├── dashboard/         # Flask web dashboard
├── utils/             # Logger, helpers
├── main.py            # Entry point
├── scheduler.py       # Daily automation
└── config.yaml        # Configuration
## ⚙️ Setup

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/job-application-bot.git
cd job-application-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in your credentials in .env

# Run bot
python main.py

# View dashboard
python dashboard/app.py
# Open http://localhost:5000
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
job_roles:
  - "Application Support"
  - "Production Support"
  - "Cloud Engineer"

locations:
  - "Pune"
  - "Mumbai"
  - "Bangalore"

experience:
  min: 0
  max: 5

apply_limit_per_day: 40
min_ai_score: 6
```

## 📈 Dashboard

- View all scraped and applied jobs
- Filter by platform, status, score
- Click job titles to open original listing
- Real-time stats cards

## ⚠️ Disclaimer

This tool is for personal use only. Use responsibly and follow each platform's terms of service.

## 📄 License

MIT License
