#!/usr/bin/env python3
"""
Example of how to integrate Shihan MCP with Hayato's code.

This script demonstrates how to call Shihan's tools directly from Python code.
"""

import asyncio
import json
import sys
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def call_shihan_tool(tool_name, args):
    """
    Call a Shihan MCP tool.
    
    Args:
        tool_name: The name of the tool to call.
        args: The arguments to pass to the tool.
        
    Returns:
        The result of the tool call.
    """
    # Set up server parameters
    params = StdioServerParameters(
        command='shihan-mcp',
        args=[],
    )
    
    # Connect to the server
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            # Initialize the session
            await s.initialize()
            
            # Call the tool
            resp = await s.call_tool(
                name=tool_name,
                arguments={"args": args},
            )
            
            # Parse and return the result
            return json.loads(resp.content[0].text)

async def main():
    """
    Main function to demonstrate Shihan MCP integration.
    """
    print("🥋 Hayato's Shihan MCP Integration Example")
    
    # Example 1: Tail the log
    print("\n📋 Example 1: Tailing the log")
    try:
        log_result = await call_shihan_tool("tail_log", {"tail_lines": 100})
        print(f"Log Summary: {log_result.get('summary')}")
        if log_result.get('last_error'):
            print(f"Last Error: {log_result.get('last_error')}")
    except Exception as e:
        print(f"Error tailing log: {str(e)}")
    
    # Example 2: Audit a Python file
    print("\n🔍 Example 2: Auditing a Python file")
    try:
        # You can replace this with any Python file you want to audit
        audit_result = await call_shihan_tool("audit_creed", {"files": ["shihan_mcp/server.py"]})
        if audit_result.get('violations'):
            print("Violations found:")
            for violation in audit_result.get('violations'):
                print(f"  - {violation}")
        else:
            print("No violations found")
    except Exception as e:
        print(f"Error auditing file: {str(e)}")
    
    # Example 3: Supervise a cycle
    print("\n🔄 Example 3: Supervising a cycle")
    try:
        cycle_result = await call_shihan_tool("supervise_cycle", {"event": "manual_check"})
        print(f"Status: {cycle_result.get('status')}")
        print("Actions taken:")
        for action in cycle_result.get('actions_taken', []):
            print(f"  - {action}")
        if cycle_result.get('issues_found'):
            print("Issues found:")
            for issue in cycle_result.get('issues_found'):
                print(f"  - {issue}")
    except Exception as e:
        print(f"Error supervising cycle: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())