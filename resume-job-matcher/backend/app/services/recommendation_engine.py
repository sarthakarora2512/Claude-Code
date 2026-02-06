import re
from app.models.schemas import ResumeRecommendation, RoleMatch


def generate_recommendations(
    raw_text: str,
    skills: list[str],
    role_matches: list[RoleMatch],
) -> list[ResumeRecommendation]:
    recommendations = []

    if not role_matches:
        return recommendations

    top_role = role_matches[0]

    # 1. Recommend adding missing skills to skills section
    if top_role.missing_skills:
        skills_section = _find_section(raw_text, ["skills", "technical skills", "core competencies"])
        if skills_section:
            missing_display = [s.title() for s in top_role.missing_skills[:5]]
            recommendations.append(ResumeRecommendation(
                section="Skills",
                original_text=skills_section.strip(),
                recommended_text=(skills_section.strip() + ", " + ", ".join(missing_display)),
                reason=f"Add missing skills for {top_role.role_title}: {', '.join(missing_display)}. "
                       f"These are required skills you should highlight if you have any experience with them.",
            ))

    # 2. Improve summary/objective
    summary_section = _find_section(raw_text, ["summary", "objective", "professional summary", "profile"])
    if summary_section:
        improved = _improve_summary(summary_section, top_role)
        if improved != summary_section.strip():
            recommendations.append(ResumeRecommendation(
                section="Professional Summary",
                original_text=summary_section.strip(),
                recommended_text=improved,
                reason=f"Tailor your summary to better target {top_role.role_title} positions "
                       f"by highlighting relevant skills and experience.",
            ))
    else:
        recommendations.append(ResumeRecommendation(
            section="Professional Summary",
            original_text="(No summary section found)",
            recommended_text=_generate_summary(skills, top_role),
            reason="Add a professional summary section to immediately communicate your value proposition.",
        ))

    # 3. Quantify achievements
    experience_section = _find_section(raw_text, ["experience", "work experience", "professional experience"])
    if experience_section:
        bullets = _find_weak_bullets(experience_section)
        for original, improved in bullets[:3]:
            recommendations.append(ResumeRecommendation(
                section="Experience",
                original_text=original,
                recommended_text=improved,
                reason="Quantify achievements with metrics and action verbs to demonstrate impact.",
            ))

    # 4. Keyword optimization across top 3 roles
    all_missing = set()
    for role in role_matches[:3]:
        all_missing.update(role.missing_skills)
    common_missing = all_missing - set(s.lower() for s in skills)
    if common_missing:
        keywords = sorted(common_missing)[:6]
        recommendations.append(ResumeRecommendation(
            section="Keywords",
            original_text="(ATS optimization)",
            recommended_text=f"Consider incorporating these keywords throughout your resume: {', '.join(k.title() for k in keywords)}",
            reason="Many companies use Applicant Tracking Systems (ATS) that scan for specific keywords. "
                   "Including these terms can improve your resume's visibility.",
        ))

    # 5. Formatting suggestions
    if len(raw_text) > 4000:
        recommendations.append(ResumeRecommendation(
            section="Formatting",
            original_text="(Resume length)",
            recommended_text="Consider condensing your resume to 1-2 pages by removing older or less relevant experience.",
            reason="Recruiters typically spend 6-7 seconds on initial resume scans. "
                   "A concise resume ensures your strongest qualifications are seen first.",
        ))

    return recommendations


def _find_section(text: str, section_names: list[str]) -> str | None:
    lines = text.split("\n")
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        for name in section_names:
            if name in line_lower and len(line.strip()) < 60:
                # Grab content until next section header
                content_lines = []
                for j in range(i + 1, min(i + 15, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and len(next_line) < 40 and next_line.upper() == next_line and len(next_line) > 3:
                        break
                    if next_line:
                        content_lines.append(next_line)
                return "\n".join(content_lines) if content_lines else None
    return None


def _improve_summary(summary: str, top_role: RoleMatch) -> str:
    matching = top_role.matching_skills[:5]
    role = top_role.role_title

    if not matching:
        return summary.strip()

    skills_str = ", ".join(s.title() for s in matching)
    improved = (
        f"Results-driven {role} with expertise in {skills_str}. "
        f"{summary.strip().split('.')[0]}. "
        f"Passionate about delivering high-quality solutions and driving technical excellence."
    )
    return improved


def _generate_summary(skills: list[str], top_role: RoleMatch) -> str:
    matching = top_role.matching_skills[:5]
    skills_str = ", ".join(s.title() for s in matching) if matching else ", ".join(s.title() for s in skills[:5])
    return (
        f"Results-driven {top_role.role_title} with strong expertise in {skills_str}. "
        f"Proven track record of delivering impactful solutions. "
        f"Seeking to leverage technical skills and experience in a challenging {top_role.role_title} role."
    )


def _find_weak_bullets(experience_text: str) -> list[tuple[str, str]]:
    """Find bullet points without metrics and suggest improvements."""
    lines = experience_text.split("\n")
    results = []

    action_verbs = {
        "responsible for": "Spearheaded",
        "worked on": "Developed",
        "helped with": "Contributed to",
        "did": "Executed",
        "made": "Engineered",
        "used": "Leveraged",
        "managed": "Directed",
    }

    for line in lines:
        stripped = line.strip().lstrip("•-–▪◦○● ")
        if len(stripped) < 20 or len(stripped) > 200:
            continue

        has_numbers = bool(re.search(r"\d+%|\d+x|\$\d+|\d+\s*(users|clients|projects|applications)", stripped))

        if not has_numbers:
            improved = stripped
            for weak, strong in action_verbs.items():
                if improved.lower().startswith(weak):
                    improved = strong + improved[len(weak):]
                    break

            if not improved[0].isupper():
                improved = improved[0].upper() + improved[1:]

            if not any(m in improved for m in ["%", "x ", "$"]):
                improved = improved.rstrip(".")
                improved += ", resulting in measurable improvements in efficiency and quality."

            if improved != stripped:
                results.append((stripped, improved))

    return results
