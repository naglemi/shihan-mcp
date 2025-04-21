"""
FastMCP server for Shihan - the supervisor of Hayato the Code Ninja.
"""

import logging
import argparse
from mcp.server.fastmcp import FastMCP

from .tools.log_tail import LogSentinelTool
from .tools.creed_audit import CreedAuditTool
from .tools.plan_critic import PlanCriticTool
from .tools.pager import PagerTool
from .agents.watchdog_agent import WatchdogAgent, WatchInput

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the Shihan MCP server.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Shihan MCP Server")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Run as an SSE server instead of stdio"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE server (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE server (default: 8000)"
    )
    args = parser.parse_args()
    
    # Create the MCP server
    logger.info("Starting Shihan MCP server")
    mcp = FastMCP("shihan")
    
    # Register each tool
    logger.info("Registering tools")
    mcp.register_tool("tail_log", LogSentinelTool())
    mcp.register_tool("audit_creed", CreedAuditTool())
    mcp.register_tool("critique_plan", PlanCriticTool())
    mcp.register_tool("page_ninja", PagerTool())
    
    # Register the watchdog agent as a composite tool
    @mcp.tool(name="supervise_cycle", description="Shihan supervision entry")
    async def supervise_cycle(args: dict) -> str:
        """
        Supervise a ninja cycle.
        
        Args:
            args: A dictionary of arguments for the watchdog agent.
            
        Returns:
            A JSON string with the results of the supervision.
        """
        logger.info(f"Supervising cycle with event: {args.get('event', 'unknown')}")
        
        try:
            # Create a WatchInput object from the arguments
            watch_input = WatchInput(**args)
            
            # Run the watchdog agent
            result = WatchdogAgent().run(watch_input)
            
            # Return the result as a JSON string
            return result.model_dump_json()
            
        except Exception as e:
            logger.error(f"Error supervising cycle: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Return an error message
            return {
                "status": "error",
                "error": str(e),
                "actions_taken": [],
                "issues_found": [f"Internal error: {str(e)}"],
                "paged": False
            }
    
    # Run the server
    if args.serve:
        logger.info(f"Running as SSE server on {args.host}:{args.port}")
        mcp.run_sse(host=args.host, port=args.port)
    else:
        logger.info("Running as stdio server")
        mcp.run()

if __name__ == "__main__":
    main()