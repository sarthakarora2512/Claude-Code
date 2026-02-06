import os
import re
import pdfplumber

SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "nosql",
    "react", "angular", "vue", "next.js", "node.js", "express", "django",
    "flask", "fastapi", "spring", "rails", ".net", "laravel",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "ci/cd", "git", "linux", "nginx", "apache",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
    "dynamodb", "firebase", "graphql", "rest api", "grpc",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "data analysis", "data engineering", "etl", "spark", "hadoop", "kafka",
    "html", "css", "sass", "tailwind", "bootstrap",
    "figma", "sketch", "adobe xd", "ui/ux",
    "agile", "scrum", "jira", "confluence", "project management",
    "communication", "leadership", "problem solving", "teamwork",
    "product management", "business analysis", "strategic planning",
    "financial modeling", "excel", "powerpoint", "tableau", "power bi",
    "salesforce", "hubspot", "sap", "oracle",
    "cybersecurity", "penetration testing", "network security",
    "blockchain", "web3", "solidity",
    "ios", "android", "react native", "flutter", "mobile development",
    "devops", "sre", "microservices", "api design", "system design",
]

JOB_TITLE_PATTERNS = [
    r"(?:senior|junior|lead|principal|staff|associate)?\s*software\s+(?:engineer|developer)",
    r"(?:senior|junior|lead)?\s*(?:frontend|front-end|backend|back-end|fullstack|full-stack)\s+(?:engineer|developer)",
    r"(?:senior|junior|lead)?\s*data\s+(?:scientist|analyst|engineer)",
    r"(?:senior|junior|lead)?\s*(?:ml|machine learning)\s+engineer",
    r"(?:senior|junior|lead)?\s*devops\s+engineer",
    r"(?:senior|junior|lead)?\s*(?:cloud|platform)\s+engineer",
    r"(?:senior|junior|lead)?\s*product\s+manager",
    r"(?:senior|junior|lead)?\s*project\s+manager",
    r"(?:senior|junior|lead)?\s*(?:ux|ui|ui/ux)\s+designer",
    r"(?:senior|junior|lead)?\s*(?:qa|quality assurance|test)\s+engineer",
    r"(?:senior|junior|lead)?\s*business\s+analyst",
    r"(?:senior|junior|lead)?\s*(?:systems?|solutions?)\s+architect",
    r"(?:senior|junior|lead)?\s*(?:technical|engineering)\s+manager",
    r"(?:senior|junior|lead)?\s*(?:security|cybersecurity)\s+engineer",
    r"(?:senior|junior|lead)?\s*(?:mobile|ios|android)\s+(?:engineer|developer)",
    r"(?:senior|junior|lead)?\s*site\s+reliability\s+engineer",
    r"cto|cio|vp\s+of\s+engineering|director\s+of\s+engineering",
]

EDUCATION_PATTERNS = [
    r"(?:bachelor|b\.?s\.?|b\.?a\.?|b\.?sc\.?|b\.?eng\.?)[\s\w]*(?:in\s+[\w\s]+)?",
    r"(?:master|m\.?s\.?|m\.?a\.?|m\.?sc\.?|m\.?eng\.?|mba)[\s\w]*(?:in\s+[\w\s]+)?",
    r"(?:ph\.?d\.?|doctorate|doctoral)[\s\w]*(?:in\s+[\w\s]+)?",
    r"(?:associate|a\.?s\.?|a\.?a\.?)[\s\w]*(?:in\s+[\w\s]+)?",
]


def extract_text_from_pdf(filepath: str) -> str:
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found_skills = []
    for skill in SKILL_KEYWORDS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return sorted(set(found_skills))


def extract_experience_years(text: str) -> float:
    patterns = [
        r"(\d+)\+?\s*years?\s*(?:of\s+)?(?:experience|exp)",
        r"(?:experience|exp)\s*:?\s*(\d+)\+?\s*years?",
        r"(\d+)\+?\s*(?:yrs?|years?)\s*(?:of\s+)?(?:professional|work|industry)",
    ]
    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        years.extend(int(m) for m in matches)

    if years:
        return float(max(years))

    # Fallback: count date ranges like "2018 - 2023"
    date_ranges = re.findall(r"(20\d{2})\s*[-–—to]+\s*(20\d{2}|present|current)", text.lower())
    total = 0
    for start, end in date_ranges:
        start_year = int(start)
        end_year = 2024 if end in ("present", "current") else int(end)
        total += max(0, end_year - start_year)
    return float(total) if total else 0.0


def extract_education(text: str) -> list[str]:
    found = []
    for pattern in EDUCATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            cleaned = m.strip()
            if len(cleaned) > 3:
                found.append(cleaned)
    return list(set(found))


def extract_job_titles(text: str) -> list[str]:
    found = []
    for pattern in JOB_TITLE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            cleaned = m.strip().title()
            if cleaned:
                found.append(cleaned)
    return list(set(found))


def generate_summary(text: str, skills: list[str], years: float, titles: list[str]) -> str:
    parts = []
    if titles:
        parts.append(f"Professional with experience as {', '.join(titles[:3])}")
    if years > 0:
        parts.append(f"{years:.0f} years of experience")
    if skills:
        top_skills = skills[:8]
        parts.append(f"skilled in {', '.join(top_skills)}")
    return ". ".join(parts) + "." if parts else "Resume uploaded successfully."


def parse_resume(filepath: str) -> dict:
    text = extract_text_from_pdf(filepath)
    skills = extract_skills(text)
    years = extract_experience_years(text)
    education = extract_education(text)
    titles = extract_job_titles(text)
    summary = generate_summary(text, skills, years, titles)

    return {
        "filename": os.path.basename(filepath),
        "raw_text": text,
        "skills": skills,
        "experience_years": years,
        "education": education,
        "job_titles": titles,
        "summary": summary,
    }
