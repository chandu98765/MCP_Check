import asyncio
import json
from typing import Any, Dict
import httpx
import os

class GitHubMCPClient:
    """Client to interact with GitHub Copilot MCP Server"""
    
    def __init__(self, base_url: str = "https://api.githubcopilot.com/mcp"):
        self.base_url = base_url
        self.session_id = None
        
    async def initialize(self, github_token: str) -> Dict[str, Any]:
        """Initialize connection to MCP server"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await client.post(
                f"{self.base_url}/session",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            print('Response from initialize:')
            print(response)
            return response.json()

    async def list_tools(self, github_token: str) -> Dict[str, Any]:
        """List available tools from the MCP server"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await client.post(
                f"{self.base_url}",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            print('Response from list_tools:')
            print(response)
            return response.json()

    async def call_tool(self, github_token: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool on the MCP server"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await client.post(
                f"{self.base_url}/session",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            return response.json()

    async def list_resources(self, github_token: str) -> Dict[str, Any]:
        """List available resources from the MCP server"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "resources/list",
                "params": {}
            }
            
            response = await client.post(
                f"{self.base_url}/session",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            return response.json()


async def main():
    """Main test function"""
    # Load GitHub token from environment variable
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
        print("⚠️  Please set your GitHub token via GITHUB_TOKEN environment variable")
        print("Get a token from: https://github.com/settings/tokens")
        print("Required scopes: repo, read:org, read:user")
        return
    
    client = GitHubMCPClient()
    
    print("=" * 60)
    print("Testing GitHub Copilot MCP Server")
    print("=" * 60)
    
    try:
        # 1. Initialize connection
        print("\n1. Initializing connection...")
        init_response = await client.initialize(GITHUB_TOKEN)
        print(json.dumps(init_response, indent=2))
        
        # 2. List available tools
        print("\n2. Listing available tools...")
        tools_response = await client.list_tools(GITHUB_TOKEN)
        print(json.dumps(tools_response, indent=2))
        
        # 3. List available resources
        print("\n3. Listing available resources...")
        resources_response = await client.list_resources(GITHUB_TOKEN)
        print(json.dumps(resources_response, indent=2))
        
        # 4. Example: Call a tool (adjust based on available tools)
        print("\n4. Calling a tool (example)...")
        # Uncomment and modify based on available tools
        # tool_response = await client.call_tool(
        #     GITHUB_TOKEN,
        #     "search_repositories",
        #     {"query": "machine learning"}
        # )
        # print(json.dumps(tool_response, indent=2))
        
    except httpx.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
