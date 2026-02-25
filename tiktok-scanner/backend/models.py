"""
Data models for the TikTok Social Arbitrage Scanner.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TikTokVideo:
    video_id: str
    author: str
    description: str
    hashtags: list[str]
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    created_at: datetime
    sound_name: Optional[str] = None
    product_mentions: list[str] = field(default_factory=list)


@dataclass
class TrendSignal:
    """A social arbitrage signal - something trending that maps to a public company."""
    signal_id: str
    keyword: str                  # e.g. "Stanley cup", "Celsius drink"
    category: str                 # e.g. "beverage", "tech", "apparel"
    video_count: int              # number of videos mentioning it in window
    total_views: int
    view_velocity: float          # views per hour - key Camillo metric
    sentiment: str                # "positive", "neutral", "negative"
    tickers: list[str]            # mapped public company tickers
    first_seen: datetime
    last_seen: datetime
    signal_strength: str          # "weak", "moderate", "strong", "viral"

    @property
    def signal_score(self) -> float:
        """Score from 0-100. Higher = stronger arbitrage opportunity."""
        velocity_score = min(self.view_velocity / 1000, 40)   # max 40pts
        volume_score = min(self.video_count / 50, 30)          # max 30pts
        sentiment_score = 20 if self.sentiment == "positive" else (
            10 if self.sentiment == "neutral" else 0
        )
        ticker_score = 10 if self.tickers else 0               # mapped = actionable
        return round(velocity_score + volume_score + sentiment_score + ticker_score, 1)


@dataclass
class TickerMapping:
    ticker: str
    company_name: str
    keywords: list[str]   # product/brand keywords that map to this ticker
    sector: str
    exchange: str


@dataclass
class ScanSnapshot:
    snapshot_id: str
    scanned_at: datetime
    videos_scanned: int
    signals_found: int
    top_signals: list[TrendSignal]
