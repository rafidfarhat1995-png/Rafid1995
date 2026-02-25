#!/bin/bash
# Start the TikTok Social Arbitrage Scanner
set -e

echo "Starting TikTok Social Arbitrage Scanner..."
cd "$(dirname "$0")/backend"

if ! command -v pip &> /dev/null; then
  echo "Error: pip not found. Install Python 3.10+."
  exit 1
fi

echo "Installing dependencies..."
pip install -r requirements.txt -q

echo "Server starting at http://localhost:8000"
uvicorn main:app --reload --port 8000 --host 0.0.0.0
