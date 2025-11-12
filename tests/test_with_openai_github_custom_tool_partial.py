import asyncio
import os
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
# from mcp.client.http import http_client, HttpServerParameters
import httpx

console = Console()
# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not OPENAI_API_KEY:
    print("⚠️  OPENAI_API_KEY environment variable is not set")
    print("   Set it: export OPENAI_API_KEY='sk-...'")
    exit(1)

if not GITHUB_TOKEN:
    print("⚠️  GITHUB_TOKEN environment variable is not set")
    print("   Set it: export GITHUB_TOKEN='ghp_...'")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# Define GitHub Copilot tool
GITHUB_TOOL = {
    "name": "github_copilot_search",
    "description": "Search GitHub repositories using GitHub Copilot MCP",
    "inputSchema": {
        "type": "object",
        "properties": {
            "repo": {"type": "string", "description": "Repository (owner/repo)"},
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["repo", "query"]
    }
}

class OpenAILLM:
    def __init__(self):
        self.conversation_history = []
        self.tool_calls = []

    def decide_tool_usage(self, user_query, tools):
        prompt = (
            "You are an AI agent. You MUST use one of the available tools to answer EVERY user query. "
            "Do NOT answer directly or use your own knowledge. "
            "Always select the most relevant tool and provide arguments. "
            "If no tool seems relevant, select the closest tool and explain your reasoning. "
            "You are NEVER allowed to say 'no tool needed'. "
            f"Tools: {json.dumps(tools)}\n"
            f"User Query: {user_query}\n"
            "Respond ONLY in JSON: {\"tool_name\": str, \"arguments\": dict, \"reasoning\": str}"
        )
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0,
        )
        content = response.choices[0].message.content
        try:
            decision = json.loads(content)
            if not decision.get("tool_name"):
                decision = {
                    "tool_name": tools[0]["name"],
                    "arguments": {},
                    "reasoning": "LLM did not select a tool; defaulting to first tool."
                }
        except Exception:
            decision = {
                "tool_name": tools[0]["name"],
                "arguments": {},
                "reasoning": "Could not parse response; defaulting to first tool."
            }
        self.tool_calls.append({"query": user_query, "decision": decision})
        return decision

    def generate_response(self, user_query, tool_result):
        prompt = (
            "You are an AI agent. ONLY use the tool result below to answer the user. "
            "Do NOT use your own knowledge or provide any information not present in the tool result. "
            "Summarize or rephrase the tool result for the user in a helpful, concise way.\n"
            f"User Query: {user_query}\n"
            f"Tool Result: {tool_result}\n"
            "Respond ONLY using information from the tool result."
        )
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=128,
            temperature=0.2,
        )
        reply = response.choices[0].message.content
        self.conversation_history.append({"query": user_query, "response": reply})
        return reply

    def log_interaction(self, user_query, tool_decision, tool_result, llm_response):
        pass
