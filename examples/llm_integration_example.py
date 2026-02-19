"""
Example: Using the Universal Data Connector with OpenAI or Anthropic.
Run the API first: uvicorn app.main:app --reload
"""

import json
import os
import sys
from pathlib import Path

# Add project root so imports work when run from examples/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

BASE_URL = os.getenv("UDC_API_URL", "http://127.0.0.1:8000")


def get_tools(provider: str = "openai") -> list:
    """Fetch tool definitions from the API."""
    r = requests.get(f"{BASE_URL}/llm/tools", params={"provider": provider})
    r.raise_for_status()
    return r.json()["tools"]


def execute_tool(tool: str, arguments: dict) -> dict:
    """Execute a tool call and return the result."""
    r = requests.post(
        f"{BASE_URL}/llm/query",
        json={"tool": tool, "arguments": arguments},
    )
    r.raise_for_status()
    return r.json()


def main():
    print("=== Universal Data Connector - LLM Integration Example ===\n")

    # 1. Get tool definitions (use these when calling OpenAI/Anthropic)
    tools = get_tools("openai")
    print("Available tools:", [t["function"]["name"] for t in tools])
    print()

    # 2. Simulate LLM tool call - e.g. user asked "How many active customers do we have?"
    tool_name = "get_crm_data"
    tool_args = {"status": "active", "voice": True}

    print(f"Simulated LLM tool call: {tool_name}({json.dumps(tool_args)})")
    result = execute_tool(tool_name, tool_args)
    print(f"\nResult metadata: {result['metadata']}")
    print(f"Voice summary: {result['metadata'].get('voice_summary')}")
    print(f"Data count: {len(result['data'])} items")
    print()

    # 3. Another example - "Show me open high-priority tickets"
    result2 = execute_tool(
        "get_support_tickets",
        {"status": "open", "priority": "high", "voice": True},
    )
    print("Open high-priority tickets:", result2["metadata"]["context_message"])
    print(f"Returned: {len(result2['data'])} tickets")
    print()

    # 4. Analytics - "What's our daily active user trend?"
    result3 = execute_tool("get_analytics", {"voice": True})
    print("Analytics result:", result3["metadata"]["context_message"])
    if result3["data"] and isinstance(result3["data"][0], dict):
        print("Summary:", result3["data"][0].get("summary", result3["data"][0]))


if __name__ == "__main__":
    main()
