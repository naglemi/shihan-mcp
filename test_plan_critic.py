#!/usr/bin/env python3
"""
Direct test of the PlanCriticTool.
"""

import sys
import os

# Add the current directory to the path so we can import the shihan_mcp package
sys.path.append('.')

# Import the tool
from shihan_mcp.tools.plan_critic import PlanCriticTool

def main():
    """Test the PlanCriticTool."""
    print("🥋 Testing PlanCriticTool")
    
    # Find the most recent scroll
    scrolls_dir = ".scrolls"
    if not os.path.exists(scrolls_dir):
        print(f"Error: {scrolls_dir} directory not found")
        return
    
    scrolls = [os.path.join(scrolls_dir, f) for f in os.listdir(scrolls_dir) if f.endswith('.md')]
    if not scrolls:
        print(f"Error: No scrolls found in {scrolls_dir}")
        return
    
    # Sort by modification time (newest first)
    scrolls.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    scroll_path = scrolls[0]
    
    print(f"Using scroll: {scroll_path}")
    
    # Create the tool
    tool = PlanCriticTool()
    
    # Run the tool
    print("\nAnalyzing scroll...")
    result = tool.run({"scroll_path": scroll_path})
    
    # Print the result
    print(f"\nScore: {result.get('score')}/100")
    
    issues = result.get('issues', [])
    if issues:
        print(f"\nIssues ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("\nNo issues found")

if __name__ == "__main__":
    main()