import asyncio
import sys
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

# Create server instance
app = Server("my-test-server")

def log_to_file(message, data=None):
    """Log to file (since stdout is used for MCP protocol)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("mcp_server.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
        if data:
            f.write(f"  Data: {json.dumps(data, indent=2)}\n")
        f.write("-" * 80 + "\n")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    log_to_file("🔍 LIST_TOOLS called by LLM")
    
    tools = [
        Tool(
            name="get_weather",
            description="Get current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="calculate",
            description="Perform mathematical calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate (e.g., '2 + 2')"
                    }
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="save_note",
            description="Save a note with a title",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["title", "content"]
            }
        )
    ]
    
    log_to_file(f"📤 Returning {len(tools)} tools to LLM", 
                {"tool_names": [t.name for t in tools]})
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from LLM"""
    log_to_file(f"⚡ TOOL_CALL received from LLM", {
        "tool_name": name,
        "arguments": arguments
    })
    
    try:
        if name == "get_weather":
            city = arguments["city"]
            # Simulate weather data
            weather_data = {
                "temperature": 72,
                "condition": "Sunny",
                "humidity": 45
            }
            result = f"Weather in {city}: {weather_data['temperature']}°F, {weather_data['condition']}, Humidity: {weather_data['humidity']}%"
            
            log_to_file(f"✅ TOOL_RESULT for {name}", {
                "city": city,
                "weather": weather_data
            })
            
        elif name == "calculate":
            expression = arguments["expression"]
            # Safe evaluation (be careful in production!)
            try:
                calc_result = eval(expression, {"__builtins__": {}}, {})
                result = f"Result of '{expression}' = {calc_result}"
                log_to_file(f"✅ TOOL_RESULT for {name}", {
                    "expression": expression,
                    "result": calc_result
                })
            except Exception as e:
                result = f"Error calculating: {str(e)}"
                log_to_file(f"❌ TOOL_ERROR for {name}", {
                    "expression": expression,
                    "error": str(e)
                })
                
        elif name == "save_note":
            title = arguments["title"]
            content = arguments["content"]
            
            # Save to file
            with open("notes.txt", "a", encoding="utf-8") as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Title: {title}\n")
                f.write(f"Date: {datetime.now()}\n")
                f.write(f"Content: {content}\n")
            
            result = f"Note '{title}' saved successfully!"
            log_to_file(f"✅ TOOL_RESULT for {name}", {
                "title": title,
                "content_length": len(content)
            })
            
        else:
            result = f"Unknown tool: {name}"
            log_to_file(f"❌ Unknown tool requested: {name}")
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        log_to_file(f"❌ EXCEPTION in {name}", {"error": str(e)})
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Run the server"""
    log_to_file("🚀 MCP Server starting...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
