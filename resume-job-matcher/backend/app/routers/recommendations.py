import os
from fastapi import APIRouter, HTTPException

from app.models.schemas import ApplyRecommendationsRequest
from app.services.recommendation_engine import generate_recommendations
from app.services.role_matcher import match_roles
from app.services.pdf_modifier import apply_recommendations_to_pdf
from app.routers.resume import resume_store

router = APIRouter()

MODIFIED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "modified_resumes")


@router.get("/{resume_id}")
async def get_recommendations(resume_id: str):
    if resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    data = resume_store[resume_id]
    role_matches = match_roles(
        data["skills"],
        data["experience_years"],
        data["job_titles"],
    )

    recommendations = generate_recommendations(
        data["raw_text"],
        data["skills"],
        role_matches,
    )

    return {
        "resume_id": resume_id,
        "recommendations": recommendations,
        "target_role": role_matches[0].role_title if role_matches else "General",
    }


@router.post("/apply")
async def apply_recommendations(request: ApplyRecommendationsRequest):
    if request.resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    data = resume_store[request.resume_id]
    original_path = data["filepath"]

    output_filename = f"modified_{data['filename']}"
    output_path = os.path.join(MODIFIED_DIR, output_filename)

    try:
        apply_recommendations_to_pdf(
            original_path,
            request.recommendations,
            output_path,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to modify PDF: {str(e)}")

    return {
        "resume_id": request.resume_id,
        "modified_pdf_url": f"/modified_resumes/{output_filename}",
        "message": "Resume updated successfully with recommendations applied.",
    }
