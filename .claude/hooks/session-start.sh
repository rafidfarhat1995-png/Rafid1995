#!/bin/bash
set -euo pipefail

# Only run in remote Claude Code on the web environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "Session start hook running..."

# No dependency manifests found in this repo.
# Add installation commands here as the project grows, for example:
#   npm install          # for Node.js projects
#   pip install -e .     # for Python projects
#   bundle install       # for Ruby projects

echo "Session start hook complete."
