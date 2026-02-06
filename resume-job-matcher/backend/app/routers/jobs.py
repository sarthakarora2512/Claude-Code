from fastapi import APIRouter, HTTPException

from app.models.schemas import JobSearchRequest
from app.services.job_crawler import crawl_jobs
from app.routers.resume import resume_store

router = APIRouter()


@router.post("/search")
async def search_jobs(request: JobSearchRequest):
    jobs = await crawl_jobs(request)
    return {
        "total": len(jobs),
        "jobs": jobs,
        "filters_applied": {
            "skills": request.skills,
            "titles": request.job_titles,
            "location": request.location,
            "remote_only": request.remote_only,
        },
    }


@router.get("/search/{resume_id}")
async def search_jobs_for_resume(resume_id: str):
    if resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    data = resume_store[resume_id]

    request = JobSearchRequest(
        skills=data["skills"][:10],
        job_titles=data["job_titles"][:3] if data["job_titles"] else ["software engineer"],
        location="United States",
        remote_only=False,
    )

    jobs = await crawl_jobs(request)

    # Separate easy-apply jobs
    easy_apply = [j for j in jobs if j.is_easy_apply]
    other = [j for j in jobs if not j.is_easy_apply]

    return {
        "resume_id": resume_id,
        "total": len(jobs),
        "easy_apply_count": len(easy_apply),
        "easy_apply_jobs": easy_apply,
        "other_jobs": other,
    }
