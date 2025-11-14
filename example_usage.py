"""Example usage of the multi-agent job search workflow with variable API key."""

# Example 1: Using the config variable (set BEFORE importing agents/graph)
from config import set_api_key, check_api_key

# Set API key using the function (must be done before importing agents)
set_api_key("sk-your-api-key-here")

# Or set it directly
# import config
# config.OPENAI_API_KEY = "sk-your-api-key-here"

# Verify it's set
if check_api_key():
    print("✓ API key is set")
    
    # Now you can import and use the workflow
    # The agents module will automatically sync the config variable to the environment
    from graph import get_graph
    
    graph_app = get_graph()
    
    # Execute workflow
    config_dict = {"configurable": {"thread_id": "example-thread"}}
    initial_state = {
        "seed_terms": ["python", "ml"],
        "location": "San Francisco",
        "resume_pdf_path": "Jane Doe Resume.pdf"
    }
    
    result = graph_app.invoke(initial_state, config=config_dict)
    print("Workflow executed successfully!")
else:
    print("✗ API key not set")


# Example 2: Using environment variable (alternative)
# Just set: export OPENAI_API_KEY=sk-... in your shell
# Then the code will automatically pick it up

