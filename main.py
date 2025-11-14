"""Main entry point for the multi-agent job search workflow."""

import os
import sys
from langgraph.types import Command
from config import check_api_key, print_package_versions
from graph import get_graph


def main():
    """Main execution function."""
    # Check API key
    if not check_api_key():
        print("Please set OPENAI_API_KEY environment variable before running.")
        return
    
    # Print package versions
    print_package_versions()
    
    # Get resume path from command line or use default
    resume_path = sys.argv[1] if len(sys.argv) > 1 else "Jane Doe Resume.pdf"
    
    if not os.path.exists(resume_path):
        print(f"\n⚠️  Warning: Resume file '{resume_path}' not found!")
        print("The workflow will still run, but screening and tailoring will be limited.")
        print("To use a resume, either:")
        print(f"  1. Place your resume PDF at: {resume_path}")
        print(f"  2. Pass the path as an argument: python main.py /path/to/your/resume.pdf")
        response = input("\nContinue without resume? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please provide a resume file.")
            return
    
    # Build graph
    print("\nBuilding workflow graph...")
    graph_app = get_graph()
    
    # Execute graph
    print("\nExecuting workflow...")
    config = {"configurable": {"thread_id": "workshop-thread"}}
    initial_state = {
        "seed_terms": ["python", "full stack", "ml"],
        "location": "San Francisco",
        "resume_pdf_path": resume_path
    }
    
    first_result = graph_app.invoke(initial_state, config=config)
    print(f"First result keys: {list(first_result.keys())}")
    print(f"Has interrupt: {'__interrupt__' in first_result}")
    
    # Handle interrupt (human selection)
    interrupts = first_result.get("__interrupt__", [])
    if interrupts:
        payload = interrupts[0].value
        print("\nInstruction:", payload.get("instruction"))
        print("Payload keys:", list(payload.keys()))
        jobs = payload.get("shortlisted_jobs", []) or payload.get("ranked_jobs", [])
        print("Shortlisted count:", len(jobs))
        preview = [j.get("id") for j in jobs[:5]]
        print("Preview IDs:", preview)
        
        # Simulate human selection (selecting first 2 jobs)
        if jobs:
            ids = [j.get("id") for j in jobs[:2]]
            print(f"\nResuming with selected job IDs: {ids}")
            final_result = graph_app.invoke(Command(resume=ids), config=config)
        else:
            print("\n⚠️  No jobs available to tailor. Skipping tailoring step.")
            final_result = first_result
    else:
        final_result = first_result
    
    # Display results
    print("\n" + "="*50)
    print("Final Results")
    print("="*50)
    print("Final result keys:", list(final_result.keys()))
    print("\nTailored resumes keys:", list(final_result.get("tailored_resumes", {}).keys()))
    print("\nSample tailored content preview:")
    for job_id, content in list(final_result.get("tailored_resumes", {}).items())[:2]:
        print(f"\n{job_id}:")
        print(content[:300] + "..." if len(content) > 300 else content)


if __name__ == "__main__":
    main()

