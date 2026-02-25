"""
TikTok Social Arbitrage Scanner - FastAPI Server
"""
import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mock_data import get_trending_videos, get_historical_snapshot
from scanner import run_scan, analyze_videos
from ticker_mapper import get_all_mappings

app = FastAPI(
    title="TikTok Social Arbitrage Scanner",
    description="Scan TikTok for viral product trends and map them to public company tickers.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_dashboard():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────

@app.get("/api/scan")
def run_new_scan(limit: int = 100):
    """
    Run a fresh scan of TikTok trending videos.
    Returns the top social arbitrage signals with ticker mappings.
    """
    videos = get_trending_videos(limit=limit)
    snapshot = run_scan(videos)

    return {
        "snapshot_id": snapshot.snapshot_id,
        "scanned_at": snapshot.scanned_at.isoformat(),
        "videos_scanned": snapshot.videos_scanned,
        "signals_found": snapshot.signals_found,
        "signals": [
            {
                "signal_id": s.signal_id,
                "keyword": s.keyword,
                "category": s.category,
                "video_count": s.video_count,
                "total_views": s.total_views,
                "view_velocity": s.view_velocity,
                "sentiment": s.sentiment,
                "tickers": s.tickers,
                "signal_strength": s.signal_strength,
                "signal_score": s.signal_score,
                "first_seen": s.first_seen.isoformat(),
                "last_seen": s.last_seen.isoformat(),
            }
            for s in snapshot.top_signals
        ],
    }


@app.get("/api/history")
def get_trend_history(days: int = 7):
    """
    Get historical trend data for sparkline charts.
    Shows how keyword volume has changed over time.
    """
    return get_historical_snapshot(days_back=days)


@app.get("/api/tickers")
def get_ticker_database():
    """Return the full product→ticker mapping database."""
    mappings = get_all_mappings()
    return [
        {
            "ticker": m.ticker,
            "company_name": m.company_name,
            "keywords": m.keywords,
            "sector": m.sector,
            "exchange": m.exchange,
        }
        for m in mappings
    ]


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
