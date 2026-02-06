from app.models.schemas import RoleMatch

ROLE_DATABASE = [
    {
        "title": "Frontend Developer",
        "required_skills": ["javascript", "react", "html", "css", "typescript"],
        "nice_to_have": ["next.js", "tailwind", "vue", "angular", "figma", "ui/ux"],
        "min_experience": 1,
        "description": "Build and maintain user-facing web applications with modern JavaScript frameworks.",
    },
    {
        "title": "Backend Developer",
        "required_skills": ["python", "sql", "rest api", "git"],
        "nice_to_have": ["django", "flask", "fastapi", "postgresql", "docker", "redis", "kafka"],
        "min_experience": 1,
        "description": "Design and implement server-side logic, APIs, and database integrations.",
    },
    {
        "title": "Full Stack Developer",
        "required_skills": ["javascript", "python", "react", "sql", "git"],
        "nice_to_have": ["node.js", "typescript", "docker", "aws", "mongodb", "postgresql"],
        "min_experience": 2,
        "description": "Work across the entire stack, from frontend UI to backend services and databases.",
    },
    {
        "title": "Data Scientist",
        "required_skills": ["python", "machine learning", "sql", "pandas"],
        "nice_to_have": ["tensorflow", "pytorch", "scikit-learn", "deep learning", "nlp", "r", "tableau"],
        "min_experience": 1,
        "description": "Analyze complex data sets and build ML models to drive business decisions.",
    },
    {
        "title": "Data Engineer",
        "required_skills": ["python", "sql", "etl", "data engineering"],
        "nice_to_have": ["spark", "hadoop", "kafka", "aws", "airflow", "docker", "postgresql"],
        "min_experience": 2,
        "description": "Build and maintain data pipelines and infrastructure for analytics and ML systems.",
    },
    {
        "title": "DevOps Engineer",
        "required_skills": ["docker", "linux", "ci/cd", "git"],
        "nice_to_have": ["kubernetes", "terraform", "aws", "jenkins", "ansible", "nginx", "devops"],
        "min_experience": 2,
        "description": "Automate infrastructure, manage CI/CD pipelines, and ensure system reliability.",
    },
    {
        "title": "Machine Learning Engineer",
        "required_skills": ["python", "machine learning", "deep learning"],
        "nice_to_have": ["tensorflow", "pytorch", "scikit-learn", "docker", "aws", "mlops", "nlp", "computer vision"],
        "min_experience": 2,
        "description": "Build, deploy, and optimize ML models in production environments.",
    },
    {
        "title": "Cloud Engineer",
        "required_skills": ["aws", "docker", "linux"],
        "nice_to_have": ["kubernetes", "terraform", "azure", "gcp", "ci/cd", "networking", "devops"],
        "min_experience": 2,
        "description": "Design and manage cloud infrastructure across major cloud platforms.",
    },
    {
        "title": "Mobile Developer",
        "required_skills": ["mobile development"],
        "nice_to_have": ["react native", "flutter", "ios", "android", "swift", "kotlin", "typescript"],
        "min_experience": 1,
        "description": "Build cross-platform or native mobile applications for iOS and Android.",
    },
    {
        "title": "Security Engineer",
        "required_skills": ["cybersecurity", "linux"],
        "nice_to_have": ["penetration testing", "network security", "python", "aws", "docker"],
        "min_experience": 2,
        "description": "Protect systems and data through security assessments, monitoring, and incident response.",
    },
    {
        "title": "Product Manager",
        "required_skills": ["product management", "agile"],
        "nice_to_have": ["jira", "confluence", "data analysis", "sql", "strategic planning", "communication"],
        "min_experience": 3,
        "description": "Define product vision, manage roadmaps, and collaborate with engineering and design.",
    },
    {
        "title": "UX/UI Designer",
        "required_skills": ["figma", "ui/ux"],
        "nice_to_have": ["sketch", "adobe xd", "html", "css", "communication", "tailwind"],
        "min_experience": 1,
        "description": "Design intuitive, accessible user interfaces through research and prototyping.",
    },
    {
        "title": "QA Engineer",
        "required_skills": ["python", "git"],
        "nice_to_have": ["ci/cd", "agile", "sql", "javascript", "docker", "jira"],
        "min_experience": 1,
        "description": "Ensure software quality through manual and automated testing strategies.",
    },
    {
        "title": "Solutions Architect",
        "required_skills": ["system design", "aws"],
        "nice_to_have": ["microservices", "docker", "kubernetes", "api design", "azure", "gcp"],
        "min_experience": 5,
        "description": "Design end-to-end technical solutions that meet complex business requirements.",
    },
    {
        "title": "Business Analyst",
        "required_skills": ["business analysis", "excel"],
        "nice_to_have": ["sql", "tableau", "power bi", "jira", "communication", "financial modeling"],
        "min_experience": 1,
        "description": "Bridge business needs and technology through requirements analysis and stakeholder management.",
    },
    {
        "title": "Site Reliability Engineer",
        "required_skills": ["linux", "docker", "python"],
        "nice_to_have": ["kubernetes", "terraform", "aws", "ci/cd", "sre", "devops", "nginx"],
        "min_experience": 3,
        "description": "Ensure system uptime and performance through automation and reliability engineering.",
    },
]


def match_roles(skills: list[str], experience_years: float, job_titles: list[str]) -> list[RoleMatch]:
    skills_lower = {s.lower() for s in skills}
    titles_lower = {t.lower() for t in job_titles}
    matches = []

    for role in ROLE_DATABASE:
        required = set(role["required_skills"])
        nice_to_have = set(role["nice_to_have"])
        all_role_skills = required | nice_to_have

        matching = skills_lower & all_role_skills
        required_matching = skills_lower & required
        missing = required - skills_lower

        # Score calculation
        if not required:
            required_score = 0.5
        else:
            required_score = len(required_matching) / len(required)

        if not nice_to_have:
            bonus_score = 0
        else:
            bonus_score = len(skills_lower & nice_to_have) / len(nice_to_have) * 0.3

        # Title match bonus
        title_bonus = 0
        role_title_lower = role["title"].lower()
        for t in titles_lower:
            if t in role_title_lower or role_title_lower in t:
                title_bonus = 0.15
                break

        # Experience factor
        exp_factor = 1.0
        if experience_years < role["min_experience"]:
            exp_factor = 0.85

        score = min((required_score * 0.55 + bonus_score + title_bonus) * exp_factor, 1.0)

        if score >= 0.15:
            matches.append(RoleMatch(
                role_title=role["title"],
                match_score=round(score, 2),
                matching_skills=sorted(matching),
                missing_skills=sorted(missing),
                description=role["description"],
            ))

    matches.sort(key=lambda x: x.match_score, reverse=True)
    return matches[:10]
