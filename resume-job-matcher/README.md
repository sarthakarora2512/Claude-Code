# Resume Job Matcher

A full-stack web application that analyzes resumes, matches them to roles, recommends improvements, modifies the PDF with one click, and crawls job postings from LinkedIn, Glassdoor, and Indeed — prioritizing easy-apply positions (Greenhouse, Lever, etc.).

## Features

- **Resume Upload & Parsing** — Upload a PDF resume; the app extracts skills, experience, education, and job titles
- **Role Matching** — Scores your resume against 16+ role profiles (Frontend, Backend, Data Scientist, DevOps, etc.)
- **Resume Recommendations** — Generates targeted suggestions for summary, skills, experience bullets, keywords, and formatting
- **One-Click PDF Modification** — Applies selected recommendations and generates a new downloadable PDF
- **Job Crawling** — Scrapes LinkedIn, Glassdoor, and Indeed for matching job postings
- **Easy Apply Filter** — Highlights jobs on Greenhouse, Lever, Workday, and other platforms that don't require account creation

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Frontend | React 18, Tailwind CSS, Vite, Axios |
| Backend  | Python, FastAPI, pdfplumber, ReportLab |
| Crawling | httpx, BeautifulSoup                |
| Infra    | Docker, Docker Compose              |

## Quick Start

### With Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Without Docker

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint                        | Description                       |
|--------|---------------------------------|-----------------------------------|
| POST   | `/api/resume/upload`            | Upload and parse a PDF resume     |
| GET    | `/api/resume/{id}`              | Get parsed resume data            |
| GET    | `/api/recommendations/{id}`     | Get resume improvement suggestions|
| POST   | `/api/recommendations/apply`    | Apply changes and generate new PDF|
| GET    | `/api/jobs/search/{id}`         | Crawl jobs matching the resume    |
| POST   | `/api/jobs/search`              | Search jobs with custom filters   |
| GET    | `/api/health`                   | Health check                      |

## Project Structure

```
resume-job-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── routers/
│   │   │   ├── resume.py           # Upload & parse endpoints
│   │   │   ├── recommendations.py  # Recommendation endpoints
│   │   │   └── jobs.py             # Job search endpoints
│   │   ├── services/
│   │   │   ├── resume_parser.py    # PDF text extraction & skill detection
│   │   │   ├── role_matcher.py     # Role matching engine
│   │   │   ├── recommendation_engine.py  # Resume improvement logic
│   │   │   ├── pdf_modifier.py     # PDF generation with changes
│   │   │   └── job_crawler.py      # LinkedIn/Glassdoor/Indeed crawler
│   │   └── models/
│   │       └── schemas.py          # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx
│   │   │   ├── ResultsPage.jsx
│   │   │   ├── RecommendationsPage.jsx
│   │   │   └── JobsPage.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ScoreBadge.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   └── services/
│   │       └── api.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Notes

- Job crawling results depend on the target sites' availability and rate limiting
- The app prioritizes jobs on Greenhouse, Lever, Workday, and similar platforms that support applying without creating an account
- Resume parsing works best with well-structured PDF resumes
- The in-memory store resets on server restart; for production use, add a database
