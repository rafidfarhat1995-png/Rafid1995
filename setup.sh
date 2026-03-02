#!/usr/bin/env bash
# setup.sh — Obsidian ↔ Claude Desktop MCP integration setup
set -euo pipefail

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

echo ""
echo "============================================"
echo "  Obsidian ↔ Claude Desktop MCP Setup"
echo "============================================"
echo ""

# ── 1. Check Node.js ─────────────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
  error "Node.js is not installed. Install it from https://nodejs.org (v18+) and re-run."
fi

NODE_VERSION=$(node -e "process.stdout.write(process.versions.node.split('.')[0])")
if [ "$NODE_VERSION" -lt 18 ]; then
  error "Node.js v18 or higher is required (found v${NODE_VERSION})."
fi
ok "Node.js v$(node --version | tr -d 'v') detected"

# ── 2. Check npx ──────────────────────────────────────────────────────────────
if ! command -v npx &>/dev/null; then
  error "npx is not available. It ships with Node.js — please reinstall Node.js."
fi
ok "npx detected"

# ── 3. Determine Claude Desktop config path ───────────────────────────────────
case "$(uname -s)" in
  Darwin) CONFIG_DIR="$HOME/Library/Application Support/Claude" ;;
  MINGW*|MSYS*|CYGWIN*) CONFIG_DIR="${APPDATA:-$HOME/AppData/Roaming}/Claude" ;;
  *) CONFIG_DIR="$HOME/.config/Claude" ;;
esac
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

info "Claude Desktop config will be written to:"
echo "  $CONFIG_FILE"
echo ""

# ── 4. Ask for Local REST API key ─────────────────────────────────────────────
echo "Before continuing, make sure you have:"
echo "  1. Installed the 'Local REST API' community plugin in Obsidian"
echo "  2. Enabled it and copied the API key from its settings"
echo ""
read -rp "Paste your Obsidian Local REST API key: " API_KEY
if [ -z "$API_KEY" ]; then
  error "API key cannot be empty."
fi

# ── 5. Ask for REST API port (default 27123) ──────────────────────────────────
read -rp "Local REST API port [27123]: " API_PORT
API_PORT="${API_PORT:-27123}"

# ── 6. Write config ───────────────────────────────────────────────────────────
mkdir -p "$CONFIG_DIR"

# Merge with existing config if present, otherwise start fresh
if [ -f "$CONFIG_FILE" ]; then
  info "Existing config found — backing up to ${CONFIG_FILE}.bak"
  cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"
fi

cat > "$CONFIG_FILE" <<EOF
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp-server"],
      "env": {
        "OBSIDIAN_API_KEY": "${API_KEY}",
        "OBSIDIAN_BASE_URL": "http://127.0.0.1:${API_PORT}",
        "OBSIDIAN_VERIFY_SSL": "false",
        "OBSIDIAN_ENABLE_CACHE": "true"
      }
    }
  }
}
EOF

ok "Config written to $CONFIG_FILE"

# ── 7. Next steps ─────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "  Setup complete! Next steps:"
echo "============================================"
echo ""
echo "  1. Open Obsidian and make sure the Local REST API plugin is running"
echo "  2. Restart Claude Desktop"
echo "  3. Start a new conversation — you should see Obsidian tools available"
echo ""
echo "  Tip: To use Claude Code CLI instead, run:"
echo "    claude /ide"
echo "  and select Obsidian from the list."
echo ""
