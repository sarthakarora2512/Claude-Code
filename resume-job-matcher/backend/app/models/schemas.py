from pydantic import BaseModel
from typing import Optional


class ResumeData(BaseModel):
    filename: str
    raw_text: str
    skills: list[str]
    experience_years: float
    education: list[str]
    job_titles: list[str]
    summary: str


class RoleMatch(BaseModel):
    role_title: str
    match_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    description: str


class ResumeRecommendation(BaseModel):
    section: str
    original_text: str
    recommended_text: str
    reason: str


class ApplyRecommendationsRequest(BaseModel):
    resume_id: str
    recommendations: list[ResumeRecommendation]


class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    url: str
    source: str
    apply_url: Optional[str] = None
    is_easy_apply: bool
    platform: Optional[str] = None
    description_snippet: str
    match_score: float = 0.0


class JobSearchRequest(BaseModel):
    skills: list[str]
    job_titles: list[str]
    location: Optional[str] = "United States"
    remote_only: bool = False
