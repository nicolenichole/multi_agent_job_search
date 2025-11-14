#!/usr/bin/env python3
"""
Demo script for Multi-Agent Job Search Workflow
Run this for a clean, presentation-ready demo
"""

import os
import sys
from config import check_api_key, print_package_versions, set_api_key
from graph import get_graph
from langgraph.types import Command


def print_header():
    """Print demo header."""
    print("=" * 70)
    print("  Multi-Agent Job Search Workflow - Demo")
    print("=" * 70)
    print()


def print_section(title):
    """Print section header."""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}\n")


def demo_setup():
    """Setup and verify environment."""
    print_section("Setup & Verification")
    
    # Check API key
    if not check_api_key():
        print("ERROR: OPENAI_API_KEY not set!")
        print("\nPlease set it using one of these methods:")
        print("  1. export OPENAI_API_KEY=sk-...")
        print("  2. python -c \"from config import set_api_key; set_api_key('sk-...')\"")
        return False
    
    print("SUCCESS: API key configured")
    
    # Print package versions
    print_package_versions()
    return True


def demo_workflow(resume_path=None):
    """Run the main workflow demo."""
    print_section("Building Workflow Graph")
    graph_app = get_graph()
    print("SUCCESS: Workflow graph compiled successfully")
    
    print_section("Executing Workflow")
    
    # Configure initial state
    config = {"configurable": {"thread_id": "demo-thread"}}
    initial_state = {
        "seed_terms": ["python", "full stack", "ml"],
        "location": "San Francisco",
        "resume_pdf_path": resume_path or "Jane Doe Resume.pdf"
    }
    
    print(f"Search terms: {', '.join(initial_state['seed_terms'])}")
    print(f"Location: {initial_state['location']}")
    print(f"Resume: {initial_state['resume_pdf_path']}")
    print("\nRunning workflow...")
    
    # Execute workflow
    first_result = graph_app.invoke(initial_state, config=config)
    
    # Display results
    jobs_found = len(first_result.get("jobs", []))
    jobs_screened = len(first_result.get("ranked_jobs", []))
    
    print_section("Search Results")
    print(f"SUCCESS: Found {jobs_found} jobs")
    print(f"SUCCESS: Screened to {jobs_screened} most relevant jobs")
    
    # Handle interrupt
    interrupts = first_result.get("__interrupt__", [])
    if interrupts:
        payload = interrupts[0].value
        jobs = payload.get("shortlisted_jobs", []) or payload.get("ranked_jobs", [])
        
        print_section("Job Selection")
        print(f"Top {min(5, len(jobs))} jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"   {i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
        
        # Auto-select first 2 for demo
        if jobs:
            selected = jobs[:2]
            selected_ids = [j.get("id") for j in selected]
            print(f"\nSUCCESS: Auto-selecting top 2 jobs for tailoring...")
            
            print_section("Resume Tailoring")
            print("Generating tailored resume bullets...")
            
            final_result = graph_app.invoke(Command(resume=selected_ids), config=config)
            
            tailored = final_result.get("tailored_resumes", {})
            print(f"SUCCESS: Generated tailored content for {len(tailored)} jobs")
            
            print_section("Demo Complete")
            print("Tailored resume content written to: tailored_resume.txt")
            print("\nNext steps:")
            print("   - Review tailored_resume.txt for generated content")
            print("   - Try different search terms or locations")
            print("   - Customize agents in agents.py")
        else:
            print("WARNING: No jobs available for tailoring")
    else:
        print("SUCCESS: Workflow completed without interruption")
    
    return True


def main():
    """Main demo function."""
    print_header()
    
    # Get resume path from command line
    resume_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Setup
    if not demo_setup():
        sys.exit(1)
    
    # Run workflow
    try:
        demo_workflow(resume_path)
    except KeyboardInterrupt:
        print("\n\nWARNING: Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: Error during demo: {e}")
        print("\nTroubleshooting:")
        print("  - Check your API key is valid")
        print("  - Ensure resume file exists (if provided)")
        print("  - Check internet connection for job search")
        sys.exit(1)


if __name__ == "__main__":
    main()

