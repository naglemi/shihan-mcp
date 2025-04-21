#!/usr/bin/env python3
"""
Example of how to use the LintAgent to catch subtle tensor mishandling.

This script demonstrates how to use the LintAgent to analyze Python code
for potential tensor-related issues.
"""

import sys
import os
import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

# Sample code with tensor operations to lint
SAMPLE_CODE = """
import torch
import numpy as np

def process_batch(batch, model):
    # Convert batch to tensor
    x = torch.tensor(batch)
    
    # Reshape tensor without checking dimensions
    x = x.reshape(10, -1)
    
    # Run model
    output = model(x)
    
    # Compute loss with potential dimension mismatch
    target = torch.zeros(8, 10)
    loss = ((output - target) ** 2).mean()
    
    # Create tensor but never use it
    unused = torch.ones(5, 5)
    
    return loss

def main():
    # Create random model
    model = torch.nn.Linear(100, 10)
    
    # Create batch with wrong dimensions
    batch = np.random.rand(8, 120)
    
    # Process batch
    loss = process_batch(batch, model)
    
    print(f"Loss: {loss}")

if __name__ == "__main__":
    main()
"""

async def call_lint_agent():
    """
    Call the LintAgent to analyze the sample code.
    """
    # Create a temporary file with the sample code
    temp_file = "temp_tensor_code.py"
    with open(temp_file, "w") as f:
        f.write(SAMPLE_CODE)
    
    try:
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
                
                # Register the lint_code tool if it's not already registered
                # Note: This is a placeholder for when the LintAgent is fully implemented
                try:
                    await s.call_tool(
                        name="lint_code",
                        arguments={"args": {"file_path": temp_file}},
                    )
                except Exception:
                    print("The lint_code tool is not yet implemented in Shihan MCP.")
                    print("This is a placeholder for a future extension.")
                    print("\nHere's what the LintAgent would analyze:")
                    print("1. Dimension mismatches:")
                    print("   - Line 10: Reshaping to (10, -1) without checking input dimensions")
                    print("   - Line 14: Target tensor has shape (8, 10) but output might have different shape")
                    print("2. Unused tensors:")
                    print("   - Line 17: 'unused' tensor is created but never used")
                    print("3. Potential broadcasting issues:")
                    print("   - Line 14: Subtraction between tensors might rely on broadcasting")
                    print("\nWhen implemented, the LintAgent will use an LLM to catch these issues automatically.")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

async def main():
    """
    Main function to demonstrate the LintAgent.
    """
    print("🔍 LintAgent Example")
    print("\n📋 Sample code to lint:")
    print(SAMPLE_CODE)
    
    print("\n🧐 Analyzing code with LintAgent...")
    await call_lint_agent()

if __name__ == "__main__":
    asyncio.run(main())