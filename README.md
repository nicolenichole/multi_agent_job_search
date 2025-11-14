# Multi-Agent Job Search Workflow

A production-ready multi-agent system using LangGraph, LangChain, and OpenAI's GPT-4o for intelligent job searching, automated screening, and AI-powered resume tailoring.

## 🚀 Quick Demo

```bash
# Activate environment
source venv/bin/activate

# Set API key
export OPENAI_API_KEY=sk-...

# Run demo
python demo.py
```

For detailed demo instructions, see [DEMO.md](DEMO.md)

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
├── config.py              # Environment setup and LLM configuration
├── tools.py               # Tool definitions (YC search, PDF parsing, etc.)
├── agents.py              # Agent construction and invocation functions
├── utils.py               # Utility functions (JSON extraction, etc.)
├── graph.py               # LangGraph workflow definition
├── main.py                # Main entry point (production use)
├── demo.py                # Demo script (presentation-ready)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── DEMO.md                # Demo guide and talking points
└── .gitignore             # Git ignore rules
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

### Demo Mode (Recommended for Presentations)

Run the polished demo script:
```bash
python demo.py
```

The demo script provides:
- ✅ Clean, formatted output
- ✅ Progress indicators
- ✅ Automatic job selection
- ✅ Summary statistics
- ✅ Professional presentation format

### Production Mode

Run the main script for full control:
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

### Workflow Diagram
```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌──────────────┐     ┌─────────┐
│ Search  │────▶│  Enrich  │────▶│ Screen  │────▶│ Human Select │────▶│ Tailor  │
│ Agent   │     │  (opt.)   │     │ Agent   │     │  (interrupt) │     │ Agent   │
└─────────┘     └──────────┘     └─────────┘     └──────────────┘     └─────────┘
    │                                 │                    │                  │
    ▼                                 ▼                    ▼                  ▼
[YC Search]                    [Resume PDF]         [User Choice]    [Tailored Output]
```

### Agents
- **Search Agent**: Expands search terms and retrieves jobs from Y Combinator "Who's hiring?" board
- **Screen Agent**: Analyzes resume and filters jobs by relevance using semantic matching
- **Tailor Agent**: Generates job-specific resume bullets aligned with job requirements

### Tools
- **YCombinatorSearch**: Searches Hacker News "Who's hiring?" threads via `yc_search.py`
- **ParseResumePDF**: Extracts and parses text from resume PDFs using PyMuPDF
- **WriteTailoredResumeSection**: Writes generated content to `tailored_resume.txt`

### Key Features
- 🔄 **Stateful Workflow**: LangGraph maintains state across workflow steps
- 🤝 **Human-in-the-Loop**: Interactive job selection with workflow interruption
- 🧠 **LLM-Powered**: Uses GPT-4o for intelligent job matching and content generation
- 🔧 **Modular Design**: Easy to extend with new agents, tools, or data sources

## Output

Tailored resume content is written to `tailored_resume.txt` in the current directory.

## Demo Presentation

### Quick Demo Commands
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Set API key
export OPENAI_API_KEY=sk-...

# 3. Run demo
python demo.py
```

### Demo Highlights
- **Search**: Finds 3-50 jobs based on search terms
- **Screen**: Filters to top 10 most relevant jobs
- **Tailor**: Generates customized resume bullets for 2 selected jobs
- **Time**: ~2-3 minutes total runtime

See [DEMO.md](DEMO.md) for detailed demo guide, talking points, and troubleshooting.

## Troubleshooting

- **OPENAI_API_KEY not set**: Set it in your shell before running
- **Package import errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
- **Network issues (YC search)**: The script uses HN Algolia and may rate-limit briefly
- **Agent returned non-JSON**: Re-run the execution; prompts request JSON-only output

## Disclaimer

All views expressed are our own and do not represent those of JPMorgan Chase & Co. References to any companies, brands, tools, or packages are for educational purposes only and do not imply endorsement or affiliation.

