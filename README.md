# Multi-Agent Job Search Workflow

A multi-step workflow using LangGraph, LangChain, and OpenAI's GPT-4o model for job searching, screening, and resume tailoring.

## Overview

This workflow includes:
1. **Search** - Expand and retrieve jobs from Y Combinator "Who's hiring?" board
2. **Enrich** (optional) - Add heuristic tags to jobs
3. **Screen** - Filter relevant jobs based on your resume
4. **Human in the loop** - Select jobs for resume tailoring
5. **Tailor** - Generate LLM-powered tailored resume bullets

## Project Structure

```
.
├── config.py          # Environment setup and LLM configuration
├── tools.py           # Tool definitions (YC search, PDF parsing, etc.)
├── agents.py          # Agent construction and invocation functions
├── utils.py           # Utility functions (JSON extraction, etc.)
├── graph.py           # LangGraph workflow definition
├── main.py            # Main entry point
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Setup

1. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your OpenAI API key** (choose one method):
   
   **Option A: Environment variable (recommended for production):**
   ```bash
   export OPENAI_API_KEY=sk-...
   ```
   
   **Option B: Set programmatically in Python:**
   ```python
   from config import set_api_key
   set_api_key("sk-...")
   ```
   
   **Option C: Direct variable assignment:**
   ```python
   import config
   config.OPENAI_API_KEY = "sk-..."
   ```

4. **Prepare your resume (optional but recommended):**
   - The workflow works best with a resume PDF for job screening and tailoring
   - You can either:
     - Place your resume PDF in the project directory (default name: "Jane Doe Resume.pdf")
     - Pass the resume path as a command-line argument: `python main.py /path/to/resume.pdf`
   - If no resume is provided, the workflow will still run but screening/tailoring will be limited
   - **Note**: The resume is used by the Screen Agent to filter relevant jobs and by the Tailor Agent to generate customized resume bullets

## Usage

### Basic Usage

Run the main script:
```bash
# With default resume path ("Jane Doe Resume.pdf")
python main.py

# With custom resume path
python main.py /path/to/your/resume.pdf
```

### Programmatic Usage

```python
from config import set_api_key, check_api_key, get_llm
from graph import get_graph

# Set API key (if not using environment variable)
set_api_key("sk-...")

# Check API key
if not check_api_key():
    raise ValueError("OPENAI_API_KEY not set")

# Get the compiled graph
graph_app = get_graph()

# Execute with initial state
config = {"configurable": {"thread_id": "workshop-thread"}}
initial_state = {
    "seed_terms": ["python", "full stack", "ml"],
    "location": "San Francisco",
    "resume_pdf_path": "Jane Doe Resume.pdf"
}

result = graph_app.invoke(initial_state, config=config)

# Handle interrupt for human selection
interrupts = result.get("__interrupt__", [])
if interrupts:
    # Select job IDs
    selected_ids = ["job_id_1", "job_id_2"]
    final_result = graph_app.invoke(Command(resume=selected_ids), config=config)
```

## Architecture

### Agents
- **Search agent**: Calls YCombinatorSearch to fetch jobs and outputs a JSON array
- **Screen agent**: Uses ParseResumePDF to read resume, then returns relevant jobs
- **Tailor agent**: Generates tailored resume bullets for selected jobs

### Tools
- **YCombinatorSearch**: Searches HN "Who's hiring?" via `yc_search.py`
- **ParseResumePDF**: Extracts text from resume PDF using PyMuPDF
- **WriteTailoredResumeSection**: Appends generated content to `tailored_resume.txt`

### Workflow
The LangGraph workflow follows: `search → (optional enrich) → screen → human_select (interrupt) → tailor → END`

## Output

Tailored resume content is written to `tailored_resume.txt` in the current directory.

## Troubleshooting

- **OPENAI_API_KEY not set**: Set it in your shell before running
- **Package import errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
- **Network issues (YC search)**: The script uses HN Algolia and may rate-limit briefly
- **Agent returned non-JSON**: Re-run the execution; prompts request JSON-only output

## Disclaimer

All views expressed are our own and do not represent those of JPMorgan Chase & Co. References to any companies, brands, tools, or packages are for educational purposes only and do not imply endorsement or affiliation.

