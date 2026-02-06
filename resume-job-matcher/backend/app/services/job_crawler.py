import asyncio
import re
import urllib.parse
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.models.schemas import JobPosting, JobSearchRequest


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

GREENHOUSE_PATTERNS = [
    r"greenhouse\.io",
    r"boards\.greenhouse",
    r"grnh\.se",
]

EASY_APPLY_PLATFORMS = [
    "greenhouse",
    "lever",
    "workday",
    "ashbyhq",
    "rippling",
    "breezy",
    "jobvite",
    "smartrecruiters",
    "workable",
]


async def crawl_jobs(request: JobSearchRequest) -> list[JobPosting]:
    """Crawl job postings from multiple sources."""
    all_jobs = []

    search_queries = _build_search_queries(request)

    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
        tasks = []
        for query in search_queries[:3]:
            tasks.append(_crawl_indeed(client, query, request.location))
            tasks.append(_crawl_linkedin(client, query, request.location))
            tasks.append(_crawl_glassdoor(client, query, request.location))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)

    # Deduplicate by URL
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job.url not in seen_urls:
            seen_urls.add(job.url)
            unique_jobs.append(job)

    # Score jobs against skills
    scored_jobs = _score_jobs(unique_jobs, request.skills)

    # Sort: easy-apply/greenhouse first, then by score
    scored_jobs.sort(key=lambda j: (j.is_easy_apply, j.match_score), reverse=True)

    return scored_jobs[:50]


def _build_search_queries(request: JobSearchRequest) -> list[str]:
    queries = []
    for title in request.job_titles[:3]:
        queries.append(title)
    if not queries and request.skills:
        queries.append(" ".join(request.skills[:3]) + " developer")
    if not queries:
        queries.append("software engineer")
    return queries


async def _crawl_indeed(
    client: httpx.AsyncClient, query: str, location: Optional[str]
) -> list[JobPosting]:
    """Scrape Indeed job listings."""
    jobs = []
    try:
        params = {
            "q": query,
            "l": location or "United States",
            "sort": "date",
            "fromage": "7",
        }
        url = "https://www.indeed.com/jobs?" + urllib.parse.urlencode(params)
        response = await client.get(url)

        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.find_all("div", class_=re.compile(r"job_seen_beacon|cardOutline|resultContent"))
        if not job_cards:
            job_cards = soup.find_all("a", class_=re.compile(r"tapItem|result"))

        for card in job_cards[:15]:
            try:
                title_el = card.find(["h2", "span"], class_=re.compile(r"jobTitle|title"))
                company_el = card.find(["span", "a"], class_=re.compile(r"company|companyName"))
                location_el = card.find("div", class_=re.compile(r"companyLocation|location"))
                snippet_el = card.find("div", class_=re.compile(r"job-snippet|snippet"))

                title = title_el.get_text(strip=True) if title_el else None
                if not title:
                    continue

                company = company_el.get_text(strip=True) if company_el else "Unknown"
                loc = location_el.get_text(strip=True) if location_el else location or ""
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""

                link_el = card.find("a", href=True)
                href = link_el["href"] if link_el else ""
                if href.startswith("/"):
                    href = "https://www.indeed.com" + href

                is_easy, platform = _check_easy_apply(snippet + " " + href)

                jobs.append(JobPosting(
                    title=title,
                    company=company,
                    location=loc,
                    url=href,
                    source="Indeed",
                    apply_url=href,
                    is_easy_apply=is_easy,
                    platform=platform,
                    description_snippet=snippet[:300],
                ))
            except Exception:
                continue
    except Exception:
        pass

    return jobs


async def _crawl_linkedin(
    client: httpx.AsyncClient, query: str, location: Optional[str]
) -> list[JobPosting]:
    """Scrape LinkedIn job listings (public, no auth required)."""
    jobs = []
    try:
        params = {
            "keywords": query,
            "location": location or "United States",
            "f_TPR": "r604800",  # Past week
            "position": "1",
            "pageNum": "0",
        }
        url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)
        response = await client.get(url)

        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.find_all("div", class_=re.compile(r"base-card|job-search-card"))
        if not job_cards:
            job_cards = soup.find_all("li", class_=re.compile(r"result-card"))

        for card in job_cards[:15]:
            try:
                title_el = card.find(["h3", "span"], class_=re.compile(r"base-search-card__title|title"))
                company_el = card.find(["h4", "a"], class_=re.compile(r"base-search-card__subtitle|company"))
                location_el = card.find("span", class_=re.compile(r"job-search-card__location|location"))

                title = title_el.get_text(strip=True) if title_el else None
                if not title:
                    continue

                company = company_el.get_text(strip=True) if company_el else "Unknown"
                loc = location_el.get_text(strip=True) if location_el else location or ""

                link_el = card.find("a", href=True)
                href = link_el["href"] if link_el else ""

                is_easy, platform = _check_easy_apply("")
                # LinkedIn Easy Apply detection
                easy_apply_el = card.find(string=re.compile(r"Easy Apply", re.I))
                if easy_apply_el:
                    is_easy = True
                    platform = "LinkedIn Easy Apply"

                jobs.append(JobPosting(
                    title=title,
                    company=company,
                    location=loc,
                    url=href,
                    source="LinkedIn",
                    apply_url=href,
                    is_easy_apply=is_easy,
                    platform=platform,
                    description_snippet="",
                ))
            except Exception:
                continue
    except Exception:
        pass

    return jobs


async def _crawl_glassdoor(
    client: httpx.AsyncClient, query: str, location: Optional[str]
) -> list[JobPosting]:
    """Scrape Glassdoor job listings."""
    jobs = []
    try:
        params = {
            "sc.keyword": query,
            "locT": "N",
            "locId": "1",  # US
        }
        url = "https://www.glassdoor.com/Job/jobs.htm?" + urllib.parse.urlencode(params)
        response = await client.get(url)

        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.find_all("li", class_=re.compile(r"react-job-listing|JobsList_jobListItem"))
        if not job_cards:
            job_cards = soup.find_all("div", class_=re.compile(r"jobCard|job-listing"))

        for card in job_cards[:15]:
            try:
                title_el = card.find(["a", "div"], class_=re.compile(r"jobTitle|job-title"))
                company_el = card.find(["div", "span"], class_=re.compile(r"EmployerProfile|employer"))
                location_el = card.find(["span", "div"], class_=re.compile(r"location|loc"))

                title = title_el.get_text(strip=True) if title_el else None
                if not title:
                    continue

                company = company_el.get_text(strip=True) if company_el else "Unknown"
                loc = location_el.get_text(strip=True) if location_el else location or ""

                link_el = card.find("a", href=True)
                href = link_el["href"] if link_el else ""
                if href.startswith("/"):
                    href = "https://www.glassdoor.com" + href

                is_easy, platform = _check_easy_apply(href)

                jobs.append(JobPosting(
                    title=title,
                    company=company,
                    location=loc,
                    url=href,
                    source="Glassdoor",
                    apply_url=href,
                    is_easy_apply=is_easy,
                    platform=platform,
                    description_snippet="",
                ))
            except Exception:
                continue
    except Exception:
        pass

    return jobs


def _check_easy_apply(text: str) -> tuple[bool, Optional[str]]:
    """Check if a job posting uses an easy-apply platform."""
    text_lower = text.lower()
    for platform in EASY_APPLY_PLATFORMS:
        if platform in text_lower:
            return True, platform
    for pattern in GREENHOUSE_PATTERNS:
        if re.search(pattern, text_lower):
            return True, "greenhouse"
    return False, None


def _score_jobs(jobs: list[JobPosting], skills: list[str]) -> list[JobPosting]:
    """Score jobs based on skill match."""
    skills_lower = {s.lower() for s in skills}
    for job in jobs:
        searchable = (job.title + " " + job.description_snippet).lower()
        matches = sum(1 for s in skills_lower if s in searchable)
        job.match_score = round(matches / max(len(skills_lower), 1), 2)
    return jobs
