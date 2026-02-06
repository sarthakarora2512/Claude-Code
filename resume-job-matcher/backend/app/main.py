import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import resume, jobs, recommendations

app = FastAPI(
    title="Resume Job Matcher",
    description="Upload resumes, get role recommendations, and find matching jobs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
MODIFIED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modified_resumes")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODIFIED_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/modified_resumes", StaticFiles(directory=MODIFIED_DIR), name="modified_resumes")

app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# Serve frontend static files — must be AFTER api routes
if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="frontend-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        """Serve the React SPA for all non-API routes."""
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
