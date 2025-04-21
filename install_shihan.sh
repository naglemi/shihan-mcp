#!/bin/bash
set -euo pipefail
# Shihan MCP Installation Script
#
# This script installs Shihan MCP and sets up the Git pre-commit hook.
#
# Usage:
#   ./install_shihan.sh

echo "🥋 Installing Shihan MCP - Supervisor for Hayato the Code Ninja"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is not installed. Please install pip and try again."
    exit 1
fi

# Install the package
echo "📦 Installing shihan-mcp package..."
pip install -e .

# Check if installation was successful
if ! command -v shihan-mcp &> /dev/null; then
    echo "❌ Error: Failed to install shihan-mcp. Please check the error messages above."
    exit 1
fi

echo "✅ shihan-mcp installed successfully"

# Set up Git pre-commit hook
if [ -d ".git" ]; then
    echo "🔄 Setting up Git pre-commit hook..."
    
    # Create hooks directory if it doesn't exist
    mkdir -p .git/hooks
    
    # Copy the pre-commit hook
    cp git-hooks/pre-commit .git/hooks/
    chmod +x .git/hooks/pre-commit
    
    echo "✅ Git pre-commit hook installed"
else
    echo "⚠️  Not a Git repository. Skipping pre-commit hook installation."
fi

# Check for environment variables
echo "🔑 Checking environment variables..."

if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "⚠️  OPENAI_API_KEY is not set. Please set it in your .env file or environment."
    echo "    export OPENAI_API_KEY=your_api_key"
fi

if [ -z "${PUSHOVER_USER_KEY:-}" ] || [ -z "${PUSHOVER_API_TOKEN:-}" ]; then
    echo "⚠️  Pushover credentials are not set. Paging will fall back to ninjascroll.sh."
    echo "    export PUSHOVER_USER_KEY=your_user_key"
    echo "    export PUSHOVER_API_TOKEN=your_api_token"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOF
# OpenAI API key for LLM-powered tools
OPENAI_API_KEY=

# OpenAI model to use (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# Pushover credentials for alerts
PUSHOVER_USER_KEY=
PUSHOVER_API_TOKEN=
EOF
    echo "✅ .env file template created. Please fill in your API keys."
fi

echo "
🎉 Shihan MCP installation complete!

To test the installation, run:
    python -m tests.test_shihan

To integrate with Hayato's ninja cycle, add this line to the end of ninjatest.sh:
    ./shihan_hook.sh

To use Shihan MCP in your IDE:
    - Cursor: Settings → Experimental → MCP Servers → Add
      Command: shihan-mcp
      Args: (blank)
      Transport: stdio
"