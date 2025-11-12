import asyncio
import json
from typing import Any, Dict, Optional
import httpx
import os


class GitHubMCPClient:
    """Client to interact with GitHub Copilot MCP Server"""
    
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
        """Send a JSON-RPC message to the MCP server"""
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        
        if params is not None:
            message["params"] = params
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=message
                )
                
                print(f"\n📤 Request to {method}:")
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                # Try to parse as JSON
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print(f"   Raw response: {response.text[:500]}")
                    return {
                        "error": "Failed to parse JSON response",
                        "status_code": response.status_code,
                        "raw_text": response.text
                    }
                    
            except httpx.HTTPStatusError as e:
                print(f"   HTTP Error: {e.response.status_code}")
                print(f"   Response: {e.response.text}")
                raise
    
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
    
    async def initialized(self, github_token: str) -> Dict[str, Any]:
        """Send initialized notification"""
        return await self._send_message(github_token, "notifications/initialized", {})
    
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


async def test_basic_connection(github_token: str):
    """Test basic connection without MCP protocol"""
    print("\n🔍 Testing basic endpoint access...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/json"
        }
        
        # Try GET request
        print("\n   Trying GET request...")
        try:
            response = await client.get(
                "https://api.githubcopilot.com/mcp",
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
        except Exception as e:
            print(f"   GET Error: {e}")
        
        # Try OPTIONS request
        print("\n   Trying OPTIONS request...")
        try:
            response = await client.options(
                "https://api.githubcopilot.com/mcp",
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
        except Exception as e:
            print(f"   OPTIONS Error: {e}")


async def main():
    """Main test function"""
    # Load GitHub token from environment variable
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
        print("⚠️  Please set your GitHub token via GITHUB_TOKEN environment variable")
        print("\n📖 Instructions:")
        print("   1. Go to: https://github.com/settings/tokens")
        print("   2. Click 'Generate new token (classic)'")
        print("   3. Select scopes: repo, read:org, read:user")
        print("   4. Set environment variable: export GITHUB_TOKEN='your_token_here'")
        return
    
    print("=" * 70)
    print("Testing GitHub Copilot MCP Server")
    print("=" * 70)
    
    # First test basic connectivity
    await test_basic_connection(GITHUB_TOKEN)
    
    # Now test MCP protocol
    client = GitHubMCPClient()
    
    try:
        # 1. Initialize connection
        print("\n" + "=" * 70)
        print("1️⃣  Initializing MCP connection...")
        print("=" * 70)
        init_response = await client.initialize(GITHUB_TOKEN)
        print("\n📥 Response:")
        print(json.dumps(init_response, indent=2))
        
        # 2. Send initialized notification
        if "result" in init_response:
            print("\n" + "=" * 70)
            print("2️⃣  Sending initialized notification...")
            print("=" * 70)
            await client.initialized(GITHUB_TOKEN)
        
        # 3. List available tools
        print("\n" + "=" * 70)
        print("3️⃣  Listing available tools...")
        print("=" * 70)
        tools_response = await client.list_tools(GITHUB_TOKEN)
        print("\n📥 Response:")
        print(json.dumps(tools_response, indent=2))
        
        if "result" in tools_response and "tools" in tools_response["result"]:
            print("\n📋 Available Tools:")
            for tool in tools_response["result"]["tools"]:
                print(f"   • {tool.get('name', 'Unknown')}")
                print(f"     {tool.get('description', 'No description')}")
                print()
        
        # 4. List available resources
        print("\n" + "=" * 70)
        print("4️⃣  Listing available resources...")
        print("=" * 70)
        resources_response = await client.list_resources(GITHUB_TOKEN)
        print("\n📥 Response:")
        print(json.dumps(resources_response, indent=2))
        
        # 5. List available prompts
        print("\n" + "=" * 70)
        print("5️⃣  Listing available prompts...")
        print("=" * 70)
        prompts_response = await client.list_prompts(GITHUB_TOKEN)
        print("\n📥 Response:")
        print(json.dumps(prompts_response, indent=2))
        
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Status Error {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except httpx.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ Test completed")
    print("=" * 70)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
