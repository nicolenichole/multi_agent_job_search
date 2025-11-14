"""Configuration and environment setup for the multi-agent job search workflow."""

import os
import importlib.metadata as md
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI

# Module-level variable for API key (can be set directly or via environment variable)
OPENAI_API_KEY: Optional[str] = None


def set_api_key(api_key: str) -> None:
    """Set the OpenAI API key programmatically.
    
    Args:
        api_key: Your OpenAI API key (starts with 'sk-')
    """
    global OPENAI_API_KEY
    OPENAI_API_KEY = api_key


def get_api_key() -> Optional[str]:
    """Get the OpenAI API key from variable or environment.
    
    Returns:
        API key string if found, None otherwise
    """
    # Check module variable first, then environment variable
    return OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")


def check_api_key() -> bool:
    """Check if OPENAI_API_KEY is set (via variable or environment)."""
    key_set = bool(get_api_key())
    print("OPENAI_API_KEY is set" if key_set else "OPENAI_API_KEY NOT set")
    return key_set


def get_llm(api_key: Optional[str] = None):
    """Set up and return the OpenAI GPT-4o LLM.
    
    Args:
        api_key: Optional API key. If not provided, uses module variable or environment variable.
    
    Returns:
        ChatOpenAI instance configured with GPT-4o
    """
    # Lazy import to avoid import errors if package isn't installed
    from langchain_openai import ChatOpenAI
    
    # Use provided key, or get from variable/environment
    openai_api_key = api_key or get_api_key()
    if not openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Set it via: config.set_api_key('sk-...') or export OPENAI_API_KEY=sk-..."
        )
    
    return ChatOpenAI(model="gpt-4o", api_key=openai_api_key, temperature=0.2)


def check_package_version(pkg: str) -> str:
    """Check if a package is installed and return its version."""
    try:
        return md.version(pkg)
    except Exception:
        return "not installed"


def print_package_versions():
    """Print versions of key packages."""
    print("LangChain:", check_package_version("langchain"))
    print("LangGraph:", check_package_version("langgraph"))
    print("OpenAI:", check_package_version("openai"))
    print("langchain-openai:", check_package_version("langchain-openai"))

