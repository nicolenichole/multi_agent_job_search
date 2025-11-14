"""Agent construction and invocation functions for search, screening, and tailoring."""

import os
from typing import List, Dict, Optional
import json
from langchain.agents import create_agent
from tools import yc_search, parse_resume_pdf, write_tailored_resume_section
from utils import extract_agent_results, extract_json_from_markdown
from config import get_api_key

# Sync config variable to environment variable if set (for LangChain compatibility)
api_key = get_api_key()
if api_key and not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = api_key

# System prompts for each agent
SEARCH_SYSTEM = (
    """You are a job search agent. Given seed terms and optional location, call YCombinatorSearch to get job listings.
    After getting results, merge and return them as a single JSON array. You can expand on the seed terms and use multiple location information to find more relevant jobs.
    Make sure you output only the JSON array of jobs."""
)

SCREEN_SYSTEM = (
    """You are a screening agent. Use ParseResumePDF to load resume from path provided,
    then filter the relevant jobs based on the jobs and resume text. Return the relevant jobs as a single JSON array.
    Make sure you output only the JSON array of jobs"""
)

TAILOR_SYSTEM = (
    "You are a resume tailoring agent. Parse the resume (ParseResumePDF) then craft tailored content "
    "for each job, appending to a file via WriteTailoredResumeSection. Return a summary of actions taken."
)

# Build tool-calling agents using LangChain v1 create_agent API
search_tools = [yc_search]  # [linkedin_search, yc_search]
screen_tools = [parse_resume_pdf]
tailor_tools = [parse_resume_pdf, write_tailored_resume_section]

search_agent_executor = create_agent(
    model="openai:gpt-4o",
    tools=search_tools,
    system_prompt=SEARCH_SYSTEM,
)

screen_agent_executor = create_agent(
    model="openai:gpt-4o",
    tools=screen_tools,
    system_prompt=SCREEN_SYSTEM,
)

tailor_agent_executor = create_agent(
    model="openai:gpt-4o",
    tools=tailor_tools,
    system_prompt=TAILOR_SYSTEM,
)


def invoke_search(seed_terms: List[str], location: Optional[str] = None) -> List[Dict]:
    """Invoke the search agent to find jobs."""
    user_input = json.dumps({"terms": seed_terms, "location": location})
    result = search_agent_executor.invoke({
        "messages": [
            {"role": "user", "content": user_input}
        ]
    })
    jobs = extract_agent_results(result)
    return jobs if isinstance(jobs, list) else []


def invoke_screen(jobs: List[Dict], resume_path: str) -> List[Dict]:
    """Invoke the screen agent to filter relevant jobs."""
    print(f"[invoke_screen] Called with {len(jobs)} jobs, resume_path='{resume_path}'")
    if not jobs:
        return []

    prompt = (
        f"Given jobs={json.dumps(jobs)} and resume_path={resume_path}. "
        "Return the relevant jobs as a JSON array."
    )

    result = screen_agent_executor.invoke({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    filtered_jobs = extract_agent_results(result)
    return filtered_jobs


def invoke_tailor(selected_jobs: List[Dict], resume_path: str) -> Dict[str, str]:
    """
    Invoke the tailor agent to generate tailored resume content.
    
    Single-call tailoring: pass ALL selected_jobs in one prompt to the tailor_agent_executor.
    The agent should:
      1) Use ParseResumePDF to load the resume text.
      2) For EACH job, generate 4–6 bullets + a short summary.
      3) For EACH job, call WriteTailoredResumeSection(path='tailored_resume.txt', content=<tailored section>).
    Output requirement: Return ONLY a JSON array where each item has fields: id (job id) and preview (<=300 chars).

    Returns: Dict[job_id -> preview]
    """
    if not selected_jobs:
        return {}

    prompt = (
        "For the following jobs and the given resume path:\n"
        f"- Resume path: {resume_path or ''}\n"
        f"- Jobs: {json.dumps(selected_jobs)}\n\n"
        "Steps:\n"
        "1) Use ParseResumePDF to load the resume text.\n"
        "2) For each job, create 4-6 concise bullet points and a short summary aligning the resume to that job.\n"
        "3) For each job, call WriteTailoredResumeSection with path='tailored_resume.txt' and the tailored section.\n"
        "Output: Return ONLY a JSON array where each item is {{'id': <job id>, 'preview': <<=300 chars>}}. No prose."
    )

    try:
        result = tailor_agent_executor.invoke({
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
        msgs = result.get("messages", []) if isinstance(result, dict) else []
        final_text = ""
        if msgs:
            last = msgs[-1]
            final_text = getattr(last, "content", "") or ""
        
        arr = extract_json_from_markdown(final_text) if isinstance(final_text, str) else []
        if isinstance(arr, list):
            out: Dict[str, str] = {}
            for item in arr:
                jid = str((item or {}).get("id", "unknown"))
                prev = (item or {}).get("preview", "")
                out[jid] = prev
            return out
        return {}
    except Exception as e:
        return {"error": f"Tailor call failed: {e}"}

