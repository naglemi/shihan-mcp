"""
Configuration settings for the Shihan MCP server.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class ChatCfg:
    """Configuration for chat models used by Shihan."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # tiny, cheap, good enough
    max_tokens = 4096

class Paths:
    """Path constants used throughout the application."""
    LOG = "training.log"
    SCROLLS = "./.scrolls"