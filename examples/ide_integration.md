# Shihan MCP IDE Integration

This guide demonstrates how to integrate Shihan MCP with your IDE (Cursor, WindSurf, Copilot, etc.).

## Cursor Integration

### Step 1: Install Shihan MCP

```bash
# Clone the repository
git clone https://github.com/yourusername/shihan-mcp.git
cd shihan-mcp

# Install the package
./install_shihan.sh
```

### Step 2: Configure Cursor

1. Open Cursor
2. Go to Settings → Experimental → MCP Servers → Add
3. Fill in the following details:
   - Command: `shihan-mcp`
   - Args: (leave blank)
   - Transport: `stdio`
4. Click "Add"

### Step 3: Create Command Palette Commands

1. Open Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
2. Type "Configure User Commands"
3. Add the following commands:

```json
{
  "commands": [
    {
      "name": "Tail training.log via Shihan",
      "command": "mcp call tail_log '{\"tail_lines\": 500}'",
      "when": "editorTextFocus"
    },
    {
      "name": "Shihan: Supervise Cycle",
      "command": "mcp call supervise_cycle '{\"event\":\"cycle_end\"}'",
      "when": "editorTextFocus"
    },
    {
      "name": "Shihan: Audit Current File",
      "command": "mcp call audit_creed '{\"files\": [\"${file}\"]}'",
      "when": "editorTextFocus"
    },
    {
      "name": "Shihan: Critique Ninja Plan",
      "command": "mcp call critique_plan '{\"scroll_path\": \"${file}\"}'",
      "when": "editorTextFocus && resourceExtname == .md"
    }
  ]
}
```

## WindSurf Integration

### Step 1: Install Shihan MCP

Follow the same installation steps as for Cursor.

### Step 2: Configure WindSurf

Add to the `agents.json` file:

```json
{
  "name": "Shihan",
  "cmd": "shihan-mcp",
  "transport": "stdio",
  "tools": ["supervise_cycle", "audit_creed", "critique_plan", "tail_log"]
}
```

### Step 3: Chain After Hayato

Modify your Hayato configuration to chain Shihan after it completes a cycle:

```json
{
  "name": "Hayato",
  "cmd": "hayato-agent",
  "transport": "stdio",
  "tools": ["..."],
  "post_commands": [
    "mcp call supervise_cycle '{\"event\":\"cycle_end\"}'"
  ]
}
```

## Testing the Integration

1. Open the Command Palette
2. Type "Shihan" to see available commands
3. Select "Shihan: Supervise Cycle"
4. You should see the results of the supervision in a new editor tab

## Troubleshooting

If you encounter issues:

1. Check that Shihan MCP is installed correctly:
   ```bash
   which shihan-mcp
   ```

2. Verify your environment variables:
   ```bash
   cat .env
   ```

3. Run the test script:
   ```bash
   python -m tests.test_shihan
   ```

4. Check the logs:
   ```bash
   tail -n 100 ~/.cursor/logs/mcp.log  # For Cursor