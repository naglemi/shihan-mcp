#!/bin/bash
set -euo pipefail
# Shihan Hook - Integrates Shihan MCP with Hayato's ninja cycle
#
# This script is meant to be appended to ninjatest.sh to automatically
# trigger Shihan supervision after training completes.
#
# Usage:
#   Add to the end of ninjatest.sh:
#   ./shihan_hook.sh

# Check if shihan-mcp is installed
if ! command -v shihan-mcp &> /dev/null; then
    echo "Error: shihan-mcp is not installed. Please install it with 'pip install -e .'."
    exit 1
fi

echo "🔍 Shihan is supervising the cycle..."

# Call the supervise_cycle tool via MCP
python -c "
import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import sys

async def call_shihan():
    params = StdioServerParameters(
        command='shihan-mcp',
        args=[],
    )
    
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            resp = await s.call_tool(
                name='supervise_cycle',
                arguments={'args': {'event': 'cycle_end'}},
            )
            result = json.loads(resp.content[0].text)
            
            # Print the results
            print('\\n📋 Shihan Supervision Report:\\n')
            
            if result.get('issues_found'):
                print('⚠️  Issues Found:')
                for issue in result.get('issues_found'):
                    print(f'  - {issue}')
            else:
                print('✅ No issues found')
                
            if result.get('paged'):
                print('\\n📱 Hayato has been paged')
            
            print('\\n🔄 Actions Taken:')
            for action in result.get('actions_taken', []):
                print(f'  - {action}')
            
            return result

asyncio.run(call_shihan())
"

echo "🏁 Shihan supervision complete"