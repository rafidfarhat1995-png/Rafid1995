#!/bin/bash
# =============================================================================
# Mac Mini 24/7 Setup Script
# Run this once on your Mac mini and everything configures itself.
# Usage: chmod +x setup_macmini.sh && ./setup_macmini.sh
# =============================================================================

set -e  # Exit on any error

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PYTHON=$(which python3)
LOG_DIR="$REPO_DIR/logs"

echo "============================================"
echo "  Mac Mini 24/7 Automation Setup"
echo "  Repo: $REPO_DIR"
echo "============================================"
echo ""

# ---------------------------------------------------------------------------
# 1. Homebrew + Python
# ---------------------------------------------------------------------------
echo "[1/6] Checking Homebrew..."
if ! command -v brew &>/dev/null; then
    echo "  Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "  Homebrew already installed."
fi

echo "[1/6] Checking Python 3..."
if ! command -v python3 &>/dev/null; then
    brew install python3
else
    echo "  Python $(python3 --version) already installed."
fi

PYTHON=$(which python3)

# ---------------------------------------------------------------------------
# 2. Python dependencies
# ---------------------------------------------------------------------------
echo ""
echo "[2/6] Installing Python dependencies..."
$PYTHON -m pip install --upgrade pip --quiet
$PYTHON -m pip install -r "$REPO_DIR/requirements.txt" --quiet
echo "  Done."

# ---------------------------------------------------------------------------
# 3. Playwright browser
# ---------------------------------------------------------------------------
echo ""
echo "[3/6] Installing Playwright Chromium browser..."
$PYTHON -m playwright install chromium
echo "  Done."

# ---------------------------------------------------------------------------
# 4. Log directory
# ---------------------------------------------------------------------------
echo ""
echo "[4/6] Creating log directory..."
mkdir -p "$LOG_DIR"
echo "  Logs will be saved to: $LOG_DIR"

# ---------------------------------------------------------------------------
# 5. launchd plists — one per script
# ---------------------------------------------------------------------------
echo ""
echo "[5/6] Registering LaunchAgents (macOS scheduler)..."
mkdir -p "$LAUNCH_AGENTS_DIR"

# --- Job Scanner (runs daily at 07:00) -------------------------------------
JOB_PLIST="$LAUNCH_AGENTS_DIR/com.rafid.jobscanner.plist"
cat > "$JOB_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rafid.jobscanner</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$REPO_DIR/job_scanner.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$REPO_DIR</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$LOG_DIR/job_scanner.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/job_scanner_error.log</string>

    <key>RunAtLoad</key>
    <false/>

    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
PLIST

# --- TikTok Trend Scanner (runs daily at 19:00) ----------------------------
TIKTOK_PLIST="$LAUNCH_AGENTS_DIR/com.rafid.tiktokscanner.plist"
cat > "$TIKTOK_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rafid.tiktokscanner</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$REPO_DIR/tiktok_trend_scanner.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$REPO_DIR</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>19</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$LOG_DIR/tiktok_scanner.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/tiktok_scanner_error.log</string>

    <key>RunAtLoad</key>
    <false/>

    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
PLIST

# Load both agents into macOS scheduler
launchctl unload "$JOB_PLIST"    2>/dev/null || true
launchctl unload "$TIKTOK_PLIST" 2>/dev/null || true
launchctl load   "$JOB_PLIST"
launchctl load   "$TIKTOK_PLIST"

echo "  Job scanner     → daily at 07:00 AM"
echo "  TikTok scanner  → daily at 07:00 PM"

# ---------------------------------------------------------------------------
# 6. Prevent Mac mini from sleeping
# ---------------------------------------------------------------------------
echo ""
echo "[6/6] Disabling sleep so scripts always run..."
# Disable system sleep (keeps running even with lid closed on Mac mini)
sudo pmset -a sleep 0
sudo pmset -a disksleep 0
sudo pmset -a displaysleep 10   # Screen off after 10 min (saves power)
sudo pmset -a powernap 1        # Allow background tasks during power nap
echo "  System sleep disabled. Display sleeps after 10 minutes."

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "============================================"
echo "  Setup complete."
echo ""
echo "  Scripts registered:"
echo "  - Job scanner     : every day at 7:00 AM"
echo "  - TikTok scanner  : every day at 7:00 PM"
echo ""
echo "  Logs:"
echo "  - $LOG_DIR/job_scanner.log"
echo "  - $LOG_DIR/tiktok_scanner.log"
echo ""
echo "  Useful commands:"
echo "  - View live job log  : tail -f $LOG_DIR/job_scanner.log"
echo "  - View live TikTok   : tail -f $LOG_DIR/tiktok_scanner.log"
echo "  - Stop job scanner   : launchctl unload $JOB_PLIST"
echo "  - Stop TikTok scanner: launchctl unload $TIKTOK_PLIST"
echo "  - Re-enable sleep    : sudo pmset -a sleep 10"
echo "============================================"
