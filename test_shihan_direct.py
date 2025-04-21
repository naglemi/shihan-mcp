#!/usr/bin/env python3
"""
Direct test of Shihan MCP tools without using the MCP package.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to the path so we can import the shihan_mcp package
sys.path.append('.')

# Import the tools
from shihan_mcp.tools.log_tail import LogSentinelTool
from shihan_mcp.tools.creed_audit import CreedAuditTool
from shihan_mcp.agents.watchdog_agent import WatchdogAgent, WatchInput

def test_log_sentinel():
    """Test the LogSentinelTool."""
    print("\n===== Testing LogSentinelTool =====")
    
    # Create the tool
    tool = LogSentinelTool()
    
    # Run the tool
    result = tool.run({"tail_lines": 100})
    
    # Print the result
    print(f"Summary: {result.get('summary')}")
    if result.get('last_error'):
        print(f"Last Error: {result.get('last_error')}")
    print(f"Elapsed: {result.get('elapsed')}")
    
    return result

def create_test_python_file():
    """Create a test Python file with some creed violations."""
    print("\n===== Creating test Python file with creed violations =====")
    
    # Create a directory for test files
    os.makedirs("test_files", exist_ok=True)
    
    # Create a test file with creed violations
    with open("test_files/test_violations.py", "w") as f:
        f.write("""
# Test file with creed violations

def check_value(value):
    # Violation: is None check
    if value is None:
        return 0
    
    # Violation: **kwargs
    def inner_func(**kwargs):
        return kwargs.get('x', 0)
    
    # Violation: mock
    from unittest.mock import MagicMock
    mock_obj = MagicMock()
    
    # Violation: hasattr
    if hasattr(value, 'compute'):
        return value.compute()
    
    return value
""")
    
    print(f"Created test file: test_files/test_violations.py")
    return "test_files/test_violations.py"

def test_creed_audit(file_path):
    """Test the CreedAuditTool."""
    print("\n===== Testing CreedAuditTool =====")
    
    # Create the tool
    tool = CreedAuditTool()
    
    # Run the tool
    result = tool.run({"files": [file_path]})
    
    # Print the result
    violations = result.get('violations', [])
    if violations:
        print(f"Found {len(violations)} violations:")
        for violation in violations:
            print(f"  - {violation}")
    else:
        print("No violations found")
    
    return result

def create_test_scroll():
    """Create a test ninja scroll."""
    print("\n===== Creating test ninja scroll =====")
    
    # Create the scrolls directory if it doesn't exist
    os.makedirs(".scrolls", exist_ok=True)
    
    # Create a timestamp for the scroll name
    timestamp = datetime.now().strftime("%m-%d-%H%M")
    scroll_path = f".scrolls/{timestamp}-test-scroll.md"
    
    # Create a test scroll with some issues
    with open(scroll_path, "w") as f:
        f.write("""# Ninja Plan: Fix Multiple Issues at Once

## Problem Diagnosis

I've identified several issues in the codebase:

1. The model is not being properly initialized
2. There's a memory leak in the data loader
3. The optimizer is using the wrong learning rate

## Proposed Solution

I'll fix all these issues at once by:

1. Changing the model initialization
2. Fixing the memory leak
3. Adjusting the learning rate

## Implementation Plan

```python
# Fix model initialization
model = Model(in_features=10, out_features=5)  # Was Model(10)

# Fix memory leak
for batch in data_loader:
    # Process batch
    del batch  # Add this line to fix memory leak

# Fix learning rate
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)  # Was 0.1
```

## Testing Plan

I'll run the training script and check if the issues are resolved.
""")
    
    print(f"Created test scroll: {scroll_path}")
    return scroll_path

def test_watchdog_agent(scroll_path):
    """Test the WatchdogAgent."""
    print("\n===== Testing WatchdogAgent =====")
    
    # Create the agent
    agent = WatchdogAgent()
    
    # Test with scroll_committed event
    print("\nTesting with scroll_committed event:")
    input_obj = WatchInput(event="scroll_committed", scroll_path=scroll_path)
    result = agent.run(input_obj)
    
    # Print the result
    print(f"Status: {result.status}")
    print("Actions taken:")
    for action in result.actions_taken:
        print(f"  - {action}")
    if result.issues_found:
        print("Issues found:")
        for issue in result.issues_found:
            print(f"  - {issue}")
    
    # Test with cycle_end event
    print("\nTesting with cycle_end event:")
    input_obj = WatchInput(event="cycle_end")
    result = agent.run(input_obj)
    
    # Print the result
    print(f"Status: {result.status}")
    print("Actions taken:")
    for action in result.actions_taken:
        print(f"  - {action}")
    if result.issues_found:
        print("Issues found:")
        for issue in result.issues_found:
            print(f"  - {issue}")
    
    return result

def main():
    """Main function to test Shihan MCP tools."""
    print("🥋 Shihan MCP Direct Test")
    
    # Test LogSentinelTool
    log_result = test_log_sentinel()
    
    # Test CreedAuditTool
    file_path = create_test_python_file()
    audit_result = test_creed_audit(file_path)
    
    # Test WatchdogAgent
    scroll_path = create_test_scroll()
    watchdog_result = test_watchdog_agent(scroll_path)
    
    print("\n🏁 Test complete")

if __name__ == "__main__":
    main()