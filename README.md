# Shihan MCP

Shihan (師範) is the head instructor who inspects Hayato's strikes, enforces creed conformance, blocks sloppy commits, and supplies richer context to IDE agents.

## Overview

Shihan MCP is a supervisor agent for Hayato the Code Ninja. It provides tools for:

- **Log Sentinel** - Tail, parse, and summarize training.log and crash traces
- **Creed Auditor** - Static-analyze changed files looking for forbidden patterns
- **Fix Plan Critic** - Score ninja plans on precision, minimalism, and test coverage
- **Pager** - Send alerts via Pushover or create a ninja scroll with --page flag

## Installation

```bash
# Install the package in development mode
pip install -e .
```

## Usage

### Command Line

```bash
# Run as stdio server (default)
shihan-mcp

# Run as SSE server
shihan-mcp --serve --host localhost --port 8000
```

### Environment Variables

- `OPENAI_API_KEY` - OpenAI API key for LLM-powered tools
- `OPENAI_MODEL` - OpenAI model to use (default: gpt-4o-mini)
- `PUSHOVER_USER_KEY` - Pushover user key for alerts
- `PUSHOVER_API_TOKEN` - Pushover API token for alerts

### Integration with IDEs

#### Cursor

1. Settings → Experimental → MCP Servers → Add
2. Command: shihan-mcp
3. Args: (blank)
4. Transport: stdio

#### WindSurf Cascade

Add to the agents.json:

```json
{
  "name": "Shihan",
  "cmd": "shihan-mcp",
  "transport": "stdio",
  "tools": ["supervise_cycle", "audit_creed", "critique_plan", "tail_log"]
}
```

## Tools

### tail_log

Tails, parses, and summarizes training.log and crash traces.

```json
{
  "tail_lines": 500
}
```

### audit_creed

Static-analyzes changed files looking for forbidden patterns.

```json
{
  "files": ["path/to/file1.py", "path/to/file2.py"]
}
```

### critique_plan

Scores ninja plans on precision, minimalism, and test coverage.

```json
{
  "scroll_path": "path/to/scroll.md"
}
```

### page_ninja

Sends alerts via Pushover or creates a ninja scroll with --page flag.

```json
{
  "title": "Alert Title",
  "body": "Alert Body",
  "priority": 1
}
```

### supervise_cycle

Orchestrates the above tools based on the event type.

```json
{
  "event": "cycle_end"
}
```

## Testing

```bash
# Run the smoke test
python -m tests.test_shihan
```

## The Creed of the Code Ninja

- A ninja's strike should be precise, minimal, and surgical
- A ninja's path is clear, with no conditional checks for phantom attributes
- A ninja addresses problems directly, not by maneuvering around them