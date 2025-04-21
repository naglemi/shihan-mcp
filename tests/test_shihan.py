"""
Test harness for the Shihan MCP server.
"""

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import asyncio
import sys
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def smoke():
    """
    Smoke test for the Shihan MCP server.
    
    This test connects to the server, initializes a session, and calls the tail_log tool.
    """
    logger.info("Starting smoke test for Shihan MCP server")
    
    # Set up server parameters
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "shihan_mcp.server"],
    )
    
    try:
        # Connect to the server
        logger.info("Connecting to server")
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                # Initialize the session
                logger.info("Initializing session")
                await s.initialize()
                
                # List available tools
                logger.info("Listing available tools")
                tools = await s.list_tools()
                logger.info(f"Available tools: {', '.join(tool.name for tool in tools.tools)}")
                
                # Call the tail_log tool
                logger.info("Calling tail_log tool")
                resp = await s.call_tool(name="tail_log", arguments={"args": {"tail_lines": 100}})
                
                # Print the response
                logger.info("Received response from tail_log tool")
                print(json.dumps(json.loads(resp.content[0].text), indent=2))
                
                # Call the supervise_cycle tool
                logger.info("Calling supervise_cycle tool")
                resp = await s.call_tool(
                    name="supervise_cycle",
                    arguments={"args": {"event": "manual_check"}}
                )
                
                # Print the response
                logger.info("Received response from supervise_cycle tool")
                print(json.dumps(json.loads(resp.content[0].text), indent=2))
                
    except Exception as e:
        logger.error(f"Error in smoke test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    logger.info("Smoke test completed successfully")
    return True

if __name__ == "__main__":
    success = asyncio.run(smoke())
    sys.exit(0 if success else 1)