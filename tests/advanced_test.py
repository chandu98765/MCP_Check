import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_multiple_calls():
    """Test multiple concurrent calls"""
    server_params = StdioServerParameters(
        command="python",
        args=["server/my_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Run multiple calls
            results = await asyncio.gather(
                # session.call_tool("add", {"a": 1, "b": 2}),
                # session.call_tool("add", {"a": 5, "b": 10}),
                # session.call_tool("greet", {"name": "Bob"})

                session.call_tool("get_weather", {"city": "France"}),
                session.call_tool("calculate", {"expression": "15 + 27"}),
                session.call_tool("save_note", {"title": "Test Note", "content": "This is a test note."})
            )
            
            for i, result in enumerate(results):
                print(f"Call {i+1}: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(test_multiple_calls())
