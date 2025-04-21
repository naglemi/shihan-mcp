#!/usr/bin/env python3
"""
Direct test of the PagerTool.
"""

import sys
import os

# Add the current directory to the path so we can import the shihan_mcp package
sys.path.append('.')

# Import the tool
from shihan_mcp.tools.pager import PagerTool

def main():
    """Test the PagerTool."""
    print("🥋 Testing PagerTool")
    
    # Create the tool
    tool = PagerTool()
    
    # Test with different priorities
    priorities = [0, 1, 2]
    
    for priority in priorities:
        print(f"\n===== Testing with priority {priority} =====")
        
        # Run the tool
        result = tool.run({
            "title": f"Test Alert (Priority {priority})",
            "body": f"This is a test alert with priority {priority}.\n\nIt's sent from the PagerTool test script.",
            "priority": priority
        })
        
        # Print the result
        print(f"Status: {result.get('status')}")
        print(f"Method: {result.get('method')}")

if __name__ == "__main__":
    main()