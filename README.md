# Obsidian ↔ Claude / Claude Code Integration

Connect your Obsidian vault to Claude or Claude Code so the AI can read, write,
and manage your notes directly.

---

## Overview

There are two main ways to connect Obsidian to Claude:

| Method | Best For | Requires |
|--------|----------|----------|
| **Claude Code + MCP plugin** | Claude Code CLI users | Node.js, Obsidian |
| **Claude Desktop + MCP server** | Claude Desktop app users | Node.js, Obsidian |

---

## Option A — Claude Code (CLI) Integration

This is the tightest integration. Claude Code connects to your live Obsidian
instance over WebSocket and can read/write your notes as you work.

### Step 1 — Install the Obsidian plugin

1. Open Obsidian → **Settings** → **Community plugins** → **Browse**
2. Search for **"Claude Code"** and install it
3. Enable the plugin and note the port (default: `22360`)

### Step 2 — Connect Claude Code

In your terminal, run:

```bash
claude /ide
```

Select **Obsidian** from the list. Claude Code will auto-discover your running
Obsidian instance on the WebSocket port.

Alternatively, pass the port explicitly:

```bash
claude --ide-port 22360
```

### Step 3 — Verify the connection

In Claude Code, run:

```
/status
```

You should see your vault name listed as the active IDE.

---

## Option B — Claude Desktop + MCP Server

Use this if you prefer the Claude Desktop app over the CLI.

### Step 1 — Install the Obsidian Local REST API plugin

1. Open Obsidian → **Settings** → **Community plugins** → **Browse**
2. Search for **"Local REST API"** and install it
3. Enable it and copy the **API key** from its settings

### Step 2 — Configure Claude Desktop

Edit your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Paste the contents of [`claude_desktop_config.json`](./claude_desktop_config.json)
from this repo, replacing the placeholder values:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp-server"],
      "env": {
        "OBSIDIAN_API_KEY": "YOUR_API_KEY_HERE",
        "OBSIDIAN_BASE_URL": "http://127.0.0.1:27123",
        "OBSIDIAN_VERIFY_SSL": "false"
      }
    }
  }
}
```

### Step 3 — Restart Claude Desktop

Close and reopen the app. You should see an Obsidian icon in the tool strip.

---

## Quick Setup Script

Run the automated setup (installs MCP dependencies and writes config):

```bash
bash setup.sh
```

The script will:
1. Check that Node.js ≥ 18 is installed
2. Ask for your vault path and Local REST API key
3. Write the correct config to `~/.config/Claude/claude_desktop_config.json`
4. Print next steps

---

## What Claude Can Do With Your Vault

Once connected, Claude can:

- Read any note by title or content search
- Create and update notes
- Manage tags and front-matter metadata
- Move and rename files
- Search across the entire vault
- Generate summaries, outlines, and linked notes

---

## Security Notes

- MCP grants **full read/write access** to your vault. Back up your vault first.
- API keys are stored locally in the config file — never commit them to git.
- The Local REST API only accepts connections from `localhost` by default.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Claude Code can't find Obsidian | Make sure Obsidian is open and the Claude Code plugin is enabled |
| Wrong port | Check Settings → Community Plugins → Claude Code → Port |
| Claude Desktop shows no Obsidian tools | Restart Claude Desktop after editing the config |
| API key errors | Regenerate the key in the Local REST API plugin settings |

---

## Resources

- [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
- [Obsidian Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [obsidian-mcp-server on npm](https://www.npmjs.com/package/obsidian-mcp-server)
- [Model Context Protocol](https://modelcontextprotocol.io)
