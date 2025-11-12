import asyncio
import json
from typing import Any, Dict, Optional
import httpx
from httpx_sse import aconnect_sse
import os

class GitHubMCPClient:
    """Client to interact with GitHub Copilot MCP Server using SSE"""
    
    def __init__(self, base_url: str = "https://api.githubcopilot.com/mcp"):
        self.base_url = base_url
        self.message_id = 0
        
    def _next_id(self) -> int:
        """Generate next message ID"""
        self.message_id += 1
        return self.message_id
    
    async def _send_message(
        self, 
        github_token: str, 
        method: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a message to the MCP server via SSE"""
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        
        if params:
            message["params"] = params
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with aconnect_sse(
                client, 
                "POST", 
                self.base_url,
                headers=headers,
                json=message
            ) as event_source:
                
                responses = []
                async for sse in event_source.aiter_sse():
                    if sse.data:
                        try:
                            data = json.loads(sse.data)
                            responses.append(data)
                            
                            # Check if this is the final response
                            if "result" in data or "error" in data:
                                return data
                        except json.JSONDecodeError:
                            print(f"Failed to parse SSE data: {sse.data}")
                
                # Return the last response if we didn't find result/error
                return responses[-1] if responses else {}
    
    async def initialize(self, github_token: str) -> Dict[str, Any]:
        """Initialize connection to MCP server"""
        return await self._send_message(
            github_token,
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "python-mcp-client",
                    "version": "1.0.0"
                }
            }
        )
    
    async def list_tools(self, github_token: str) -> Dict[str, Any]:
        """List available tools from the MCP server"""
        return await self._send_message(github_token, "tools/list", {})
    
    async def call_tool(
        self, 
        github_token: str, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a specific tool on the MCP server"""
        return await self._send_message(
            github_token,
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments
            }
        )
    
    async def list_resources(self, github_token: str) -> Dict[str, Any]:
        """List available resources from the MCP server"""
        return await self._send_message(github_token, "resources/list", {})
    
    async def list_prompts(self, github_token: str) -> Dict[str, Any]:
        """List available prompts from the MCP server"""
        return await self._send_message(github_token, "prompts/list", {})


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
    
    print("=" * 70)
    print("Testing GitHub Copilot MCP Server (SSE)")
    print("=" * 70)
    
    try:
        # 1. Initialize connection
        print("\n1️⃣  Initializing connection...")
        init_response = await client.initialize(GITHUB_TOKEN)
        print(json.dumps(init_response, indent=2))
        
        # 2. List available tools
        print("\n2️⃣  Listing available tools...")
        tools_response = await client.list_tools(GITHUB_TOKEN)
        print(json.dumps(tools_response, indent=2))
        
        if "result" in tools_response and "tools" in tools_response["result"]:
            print("\n📋 Available Tools:")
            for tool in tools_response["result"]["tools"]:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        
        # 3. List available resources
        print("\n3️⃣  Listing available resources...")
        resources_response = await client.list_resources(GITHUB_TOKEN)
        print(json.dumps(resources_response, indent=2))
        
        # 4. List available prompts
        print("\n4️⃣  Listing available prompts...")
        prompts_response = await client.list_prompts(GITHUB_TOKEN)
        print(json.dumps(prompts_response, indent=2))
        
        # 5. Example: Call a tool (uncomment and modify based on available tools)
        print("\n5️⃣  Example tool call (commented out):")
        print("   Uncomment the code below and modify based on available tools")
        print("   Example:")
        print("   tool_response = await client.call_tool(")
        print("       GITHUB_TOKEN,")
        print("       'search_repositories',")
        print("       {'query': 'machine learning', 'limit': 5}")
        print("   )")
        
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Error {e.response.status_code}: {e.response.text}")
    except httpx.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Test completed")
    print("=" * 70)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
