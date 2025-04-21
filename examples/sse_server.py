#!/usr/bin/env python3
"""
Example of how to run Shihan MCP as an SSE server and connect to it.

This script demonstrates how to:
1. Start Shihan MCP as an SSE server
2. Connect to it using the MCP client
3. Call its tools
"""

import asyncio
import json
import subprocess
import time
import sys
from mcp.client.sse import sse_client
from mcp import ClientSession, SSEServerParameters

async def start_sse_server():
    """
    Start Shihan MCP as an SSE server.
    
    Returns:
        The subprocess object representing the server process.
    """
    print("🚀 Starting Shihan MCP as an SSE server...")
    
    # Start the server
    process = subprocess.Popen(
        ["shihan-mcp", "--serve", "--host", "localhost", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    return process

async def call_shihan_tools():
    """
    Connect to the Shihan MCP SSE server and call its tools.
    """
    # Set up server parameters
    params = SSEServerParameters(
        url="http://localhost:8000"
    )
    
    print("🔌 Connecting to Shihan MCP SSE server...")
    
    # Connect to the server
    async with sse_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            # Initialize the session
            await s.initialize()
            
            # List available tools
            tools = await s.list_tools()
            print(f"🔧 Available tools: {', '.join(tool.name for tool in tools.tools)}")
            
            # Example 1: Tail the log
            print("\n📋 Example 1: Tailing the log")
            resp = await s.call_tool(
                name="tail_log",
                arguments={"args": {"tail_lines": 100}},
            )
            log_result = json.loads(resp.content[0].text)
            print(f"Log Summary: {log_result.get('summary')}")
            
            # Example 2: Supervise a cycle
            print("\n🔄 Example 2: Supervising a cycle")
            resp = await s.call_tool(
                name="supervise_cycle",
                arguments={"args": {"event": "manual_check"}},
            )
            cycle_result = json.loads(resp.content[0].text)
            print(f"Status: {cycle_result.get('status')}")
            print("Actions taken:")
            for action in cycle_result.get('actions_taken', []):
                print(f"  - {action}")

async def main():
    """
    Main function to demonstrate Shihan MCP as an SSE server.
    """
    print("🥋 Shihan MCP SSE Server Example")
    
    # Start the server
    server_process = await start_sse_server()
    
    try:
        # Call the tools
        await call_shihan_tools()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        # Stop the server
        print("\n🛑 Stopping Shihan MCP SSE server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")

if __name__ == "__main__":
    asyncio.run(main())