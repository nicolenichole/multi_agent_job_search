"""Tool definitions for job search, resume parsing, and resume tailoring."""

from typing import List, Dict, Optional
import json
import os
from langchain_core.tools import tool


@tool("linkedInSearch")  # Not used in this workshop
def linkedin_search(params, headers, terms: List[str], location: Optional[str] = None) -> List[Dict]:
    """
    Search LinkedIn jobs using BrightData API.

    Args:
        params: API query parameters.
        headers: API authorization headers.
        terms (List[str]): List of search keywords or job titles.
        location (Optional[str]): Job location; defaults to 'Remote'.

    Returns:
        List[Dict]: List of job postings as dictionaries.
    """
    import requests
    import time
    
    location = location or "Remote"
    jobs = []

    try:
        for term in terms or []:
            data = [{
                "location": location,
                "keyword": term,
                "country": "US",
                "time_range": "Past month",
                "job_type": "Full-time",
                "experience_level": "Entry level",
                "remote": "On-site",
                "company": "",
                "location_radius": ""
            }]

            # Trigger dataset creation
            trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
            trigger_response = requests.post(trigger_url, headers=headers, params=params, data=json.dumps(data))

            if trigger_response.status_code != 200:
                print(f"Failed to trigger dataset for '{term}'. Status: {trigger_response.status_code}")
                continue

            trigger_data = trigger_response.json()
            snapshot_id = trigger_data.get("snapshot_id")
            print(f"Triggered snapshot for '{term}' — ID: {snapshot_id}")

            # Poll for dataset readiness
            progress_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
            while True:
                progress_response = requests.get(progress_url, headers=headers)
                if progress_response.status_code != 200:
                    print(f"Failed to check progress for '{term}'.")
                    break

                status = progress_response.json().get("status")
                print(f"Status for '{term}': {status}")

                if status == "ready":
                    break
                elif status == "running":
                    time.sleep(10)
                else:
                    print(f"Unexpected status '{status}' for '{term}'.")
                    break

            # Retrieve dataset when ready
            snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
            snapshot_response = requests.get(snapshot_url, headers=headers)
            if snapshot_response.status_code != 200:
                print(f"Failed to fetch snapshot for '{term}'.")
                continue

            results = snapshot_response.json()
            for job in results:
                jobs.append({
                    "id": f"li_{job['job_posting_id']}",
                    "source": "linkedin",
                    "title": job.get("job_title", ""),
                    "company": job.get("company_name", ""),
                    "location": job.get("job_location", ""),
                    "summary": job.get("job_summary", ""),
                    "job_url": job.get("url", "")
                })

    except Exception as e:
        print(f"Exception occurred: {e}")
        # Fallback example
        jobs.append({
            "id": "fallback_1",
            "source": "linkedin",
            "title": "Fallback Product Manager",
            "company": "Example Corp",
            "location": location,
            "summary": "Example summary for fallback case.",
            "job_url": "https://www.linkedin.com/jobs/"
        })

    return jobs


@tool("YCombinatorSearch")
def yc_search(terms: List[str], location: Optional[str] = None) -> List[Dict]:
    """Search Y Combinator (HN 'Who is hiring?') posts via helper script.

    Returns normalized job dicts: id, source, title, company, location, description, url
    """
    try:
        # Import the real implementation from the script we added to the workspace
        from yc_search import yc_search as yc_search_real
        results = yc_search_real(terms or [], location, limit=50)
        cleaned: List[Dict] = []
        for j in results or []:
            cleaned.append({
                "id": str(j.get("id") or ""),
                "source": "ycombinator",
                "title": j.get("title") or "",
                "company": j.get("company") or "",
                "location": j.get("location") or (location or ""),
                "description": j.get("description") or "",
                "url": j.get("url") or "",
            })
        return cleaned
    except Exception as e:
        # Fallback stub to avoid breaking the graph if import/network fails
        location = location or "Remote"
        jobs = []
        for i, t in enumerate(terms or []):
            jobs.append({
                "id": f"yc_{i}",
                "source": "ycombinator",
                "title": f"{t.title()} Engineer",
                "company": "StartupCo",
                "location": location,
                "description": f"Seeking {t} engineer to build MVP features across stack.",
            })
        return jobs


@tool("ParseResumePDF")
def parse_resume_pdf(path: str) -> str:
    """Parse resume PDF at path. Args: path (str). Returns extracted text or empty string."""
    try:
        import pymupdf
        if not os.path.exists(path):
            return ""
        doc = pymupdf.open(path)
        text = "\n".join(p.get_text() for p in doc)
        doc.close()
        return text
    except Exception:
        return ""


@tool("WriteTailoredResumeSection")
def write_tailored_resume_section(path: str, content: str) -> str:
    """Write tailored resume content to txt file. Args: path (str), content (str). Returns a status string."""
    try:
        path = path or "tailored_resume.txt"
        with open(path, "a", encoding="utf-8") as f:
            f.write(content + "\n\n")
        return f"Wrote content to {path}"
    except Exception as e:
        return f"Failed to write: {e}"

