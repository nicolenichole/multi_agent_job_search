"""Utility functions for JSON extraction and agent result processing."""

import json
import re
from typing import List, Dict, Any


def extract_json_from_markdown(text: str) -> list:
    """
    Extract JSON array from a string that may contain markdown code blocks.

    Args:
        text: String that may contain JSON in markdown ```json blocks or plain text

    Returns:
        Parsed JSON array, or empty list if parsing fails
    """
    # Try to find JSON in markdown code block
    match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Try to find JSON array directly in the text
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            return []

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return []


def extract_agent_results(result: Dict[str, Any]) -> List[Dict]:
    """
    Extract JSON array from agent's final message content.
    
    Args:
        result: Agent execution result dictionary
        
    Returns:
        Parsed JSON array, or empty list if parsing fails
    """
    # Take agent's final AI message content and extract JSON array from it
    try:
        msgs = result.get('messages', []) if isinstance(result, dict) else []
        if not msgs:
            return []
        answer = msgs[-1].content if hasattr(msgs[-1], 'content') else None
        print("Intermediate messages:")
        for m in msgs:
            # Check if it's a ToolMessage
            msg_type = type(m).__name__ if hasattr(m, '__class__') else None
            content = getattr(m, "content", None) if hasattr(m, "content") else m.get("content") if isinstance(m, dict) else None
            print(f"- Message type: {msg_type}, content: {str(content)}")

        print("Agent answer:", answer)
        if isinstance(answer, str):
            return extract_json_from_markdown(answer)
        return []
    except Exception:
        return []

