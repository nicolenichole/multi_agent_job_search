"""LangGraph workflow definition for the multi-agent job search process."""

from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List, Dict, Any, Optional
from agents import invoke_search, invoke_screen, invoke_tailor


class State(TypedDict, total=False):
    """State schema for the LangGraph workflow."""
    seed_terms: List[str]
    location: Optional[str]
    resume_pdf_path: str
    jobs: List[Dict]
    needs_enrichment: bool
    enriched_jobs: List[Dict]
    ranked_jobs: List[Dict]
    shortlisted_jobs: List[Dict]
    selected_jobs: List[Dict]
    tailored_resumes: Dict[str, str]


def build_graph():
    """Build and compile the LangGraph workflow."""
    g = StateGraph(State)

    def n_search(s: State) -> State:
        """Search node: find jobs based on seed terms and location."""
        terms = s.get("seed_terms", ["python", "ml"])
        location = s.get("location")
        jobs = invoke_search(terms, location)
        # Fallback if agent returns nothing
        if not jobs:
            jobs = [
                {"id": "stub_li_0", "source": "linkedin", "title": "Python Engineer", "company": "EnterpriseCo", "location": location or "Remote", "description": "Looking for python engineers with cloud and data experience."},
                {"id": "stub_li_1", "source": "linkedin", "title": "Backend Engineer", "company": "ScaleUp", "location": location or "Remote", "description": "Looking for backend engineers with cloud and data experience."},
                {"id": "stub_yc_0", "source": "ycombinator", "title": "Python Engineer", "company": "StartupCo", "location": location or "Remote", "description": "Seeking python engineer to build MVP features across stack."},
            ]
        print(f"[n_search] jobs count: {len(jobs)}")
        return {
            **s,
            "jobs": jobs,
            "needs_enrichment": len(jobs) > 12
        }

    def n_enrich(s: State) -> State:
        """Enrich node: add heuristic tags to jobs."""
        enriched = []
        for j in s.get("jobs", []):
            j = dict(j)
            j["enriched_tag"] = "long-desc" if len(j.get("description", "")) > 50 else "short-desc"
            enriched.append(j)
        print(f"[n_enrich] enriched_jobs count: {len(enriched)}")
        return {
            **s,
            "enriched_jobs": enriched
        }

    def n_screen(s: State) -> State:
        """Screen node: filter relevant jobs based on resume."""
        base_jobs = s.get("enriched_jobs") or s.get("jobs", [])
        print(f"[n_screen] base_jobs count: {len(base_jobs)}")
        resume_path = s.get("resume_pdf_path", "")
        ranked = invoke_screen(base_jobs, resume_path)
        print(f"[n_screen] ranked_jobs count: {len(ranked)}")
        return {
            **s,
            "ranked_jobs": ranked[:10],
            "shortlisted_jobs": ranked[:10]
        }

    def n_select(s: State) -> State:
        """Human selection node: interrupt for user to select jobs."""
        if "selected_jobs" not in s:
            payload = {
                "instruction": "Select top 2 job IDs or objects to tailor.",
                "ranked_jobs": s.get("ranked_jobs", []),
            }
            selection = interrupt(payload)
            chosen = []
            if isinstance(selection, list):
                if selection and isinstance(selection[0], str):
                    id_set = set(selection)
                    for j in s.get("ranked_jobs", []):
                        if j.get("id") in id_set and len(chosen) < 2:
                            chosen.append(j)
                elif selection and isinstance(selection[0], dict):
                    chosen = selection[:2]
            if not chosen:
                chosen = s.get("ranked_jobs", [])[:2]
            return {
                **s,
                "selected_jobs": chosen
            }
        return s

    def n_tailor(s: State) -> State:
        """Tailor node: generate tailored resume content for selected jobs."""
        selected = s.get("selected_jobs", [])
        resume_path = s.get("resume_pdf_path", "")
        tailored = invoke_tailor(selected, resume_path)
        return {
            **s,
            "tailored_resumes": tailored
        }

    # Add nodes
    g.add_node("search_agent", n_search)
    g.add_node("enrich_node", n_enrich)
    g.add_node("screen_agent", n_screen)
    g.add_node("human_select_interrupt", n_select)
    g.add_node("tailor_agent", n_tailor)

    # Set entry point
    g.set_entry_point("search_agent")

    # Add edges
    def route_from_search(s: State):
        """Route from search: enrich if needed, otherwise go to screen."""
        return "enrich" if s.get("needs_enrichment") else "screen"

    g.add_conditional_edges("search_agent", route_from_search, {"enrich": "enrich_node", "screen": "screen_agent"})
    g.add_edge("enrich_node", "screen_agent")
    g.add_edge("screen_agent", "human_select_interrupt")
    g.add_edge("human_select_interrupt", "tailor_agent")
    g.add_edge("tailor_agent", END)

    return g.compile(checkpointer=MemorySaver())


def get_graph():
    """Get the compiled graph instance."""
    return build_graph()

