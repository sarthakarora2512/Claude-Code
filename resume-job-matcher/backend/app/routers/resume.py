import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.schemas import ResumeData
from app.services.resume_parser import parse_resume
from app.services.role_matcher import match_roles

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

# In-memory store for parsed resume data (keyed by resume_id)
resume_store: dict[str, dict] = {}


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    resume_id = str(uuid.uuid4())
    filename = f"{resume_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    with open(filepath, "wb") as f:
        f.write(content)

    try:
        parsed = parse_resume(filepath)
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(status_code=422, detail=f"Failed to parse resume: {str(e)}")

    resume_data = {
        "resume_id": resume_id,
        "filepath": filepath,
        **parsed,
    }
    resume_store[resume_id] = resume_data

    role_matches = match_roles(
        parsed["skills"],
        parsed["experience_years"],
        parsed["job_titles"],
    )

    return {
        "resume_id": resume_id,
        "resume_data": ResumeData(**parsed),
        "role_matches": role_matches,
    }


@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    if resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found")
    data = resume_store[resume_id]
    role_matches = match_roles(
        data["skills"],
        data["experience_years"],
        data["job_titles"],
    )
    return {
        "resume_id": resume_id,
        "resume_data": ResumeData(
            filename=data["filename"],
            raw_text=data["raw_text"],
            skills=data["skills"],
            experience_years=data["experience_years"],
            education=data["education"],
            job_titles=data["job_titles"],
            summary=data["summary"],
        ),
        "role_matches": role_matches,
    }
