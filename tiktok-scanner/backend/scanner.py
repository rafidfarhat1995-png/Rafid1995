"""
TikTok Social Arbitrage Scanner - Core Analysis Engine.

Inspired by Chris Camillo's social arbitrage approach:
- Find products/trends going viral on TikTok
- Measure velocity (how fast views are accumulating)
- Map trends to public company tickers
- Score the signal strength before it hits mainstream media
"""
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from models import TikTokVideo, TrendSignal, ScanSnapshot
from ticker_mapper import find_tickers_for_keywords, find_tickers_for_text


# Minimum thresholds for a signal to be worth reporting
MIN_VIDEO_COUNT = 3          # at least N videos about the topic
MIN_TOTAL_VIEWS = 50_000     # at least this many total views
SCAN_WINDOW_HOURS = 48       # look at videos from last N hours


def _detect_sentiment(video: TikTokVideo) -> str:
    """
    Simple keyword-based sentiment. Replace with ML model for production.
    """
    positive_words = {
        "love", "obsessed", "amazing", "best", "incredible", "need", "must",
        "game changer", "life changing", "cant stop", "addicted", "recommend",
        "finally", "honest review", "worth it", "🔥", "😍", "🙌", "✨",
    }
    negative_words = {
        "hate", "worst", "scam", "fake", "overrated", "disappointed", "terrible",
        "waste", "broken", "bad", "awful", "dont buy", "don't buy", "😤", "💀",
    }

    text = (video.description + " ".join(video.hashtags)).lower()

    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"


def _calculate_velocity(videos: list[TikTokVideo]) -> float:
    """
    Views per hour - Chris Camillo's key metric.
    High velocity = trend is accelerating NOW, before mainstream media picks it up.
    """
    if not videos:
        return 0.0

    now = datetime.utcnow()
    total_views = 0
    oldest = now

    for v in videos:
        total_views += v.view_count
        if v.created_at < oldest:
            oldest = v.created_at

    hours_elapsed = max(1.0, (now - oldest).total_seconds() / 3600)
    return round(total_views / hours_elapsed, 1)


def _strength_label(score: float) -> str:
    if score >= 75:
        return "viral"
    elif score >= 55:
        return "strong"
    elif score >= 35:
        return "moderate"
    return "weak"


def _extract_all_keywords(video: TikTokVideo) -> list[str]:
    """Pull all searchable text from a video for keyword matching."""
    parts = [video.description] + video.hashtags + video.product_mentions
    return [p.lower() for p in parts]


def analyze_videos(videos: list[TikTokVideo]) -> list[TrendSignal]:
    """
    Core analysis: cluster videos by topic, score each cluster,
    map to tickers, return ranked TrendSignals.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=SCAN_WINDOW_HOURS)

    # Filter to scan window
    recent_videos = [v for v in videos if v.created_at >= cutoff]

    # Group videos by product mentions
    topic_clusters: dict[str, list[TikTokVideo]] = defaultdict(list)

    for video in recent_videos:
        keywords = _extract_all_keywords(video)
        matched_mappings = find_tickers_for_keywords(keywords)

        if matched_mappings:
            # Assign video to each ticker cluster it mentions
            for mapping in matched_mappings:
                primary_keyword = mapping.keywords[0]
                topic_clusters[primary_keyword].append(video)
        else:
            # Try product_mentions directly
            for mention in video.product_mentions:
                topic_clusters[mention.lower()].append(video)

    signals: list[TrendSignal] = []

    for keyword, cluster_videos in topic_clusters.items():
        # Deduplicate videos within this cluster
        seen_ids = set()
        unique_videos = []
        for v in cluster_videos:
            if v.video_id not in seen_ids:
                seen_ids.add(v.video_id)
                unique_videos.append(v)

        if len(unique_videos) < MIN_VIDEO_COUNT:
            continue

        total_views = sum(v.view_count for v in unique_videos)
        if total_views < MIN_TOTAL_VIEWS:
            continue

        velocity = _calculate_velocity(unique_videos)

        # Aggregate sentiment
        sentiments = [_detect_sentiment(v) for v in unique_videos]
        pos = sentiments.count("positive")
        neg = sentiments.count("negative")
        dominant_sentiment = "positive" if pos > neg else ("negative" if neg > pos else "neutral")

        # Map to tickers
        all_text = " ".join(_extract_all_keywords(v) for v in unique_videos)
        ticker_mappings = find_tickers_for_text(all_text)
        tickers = [m.ticker for m in ticker_mappings]

        # Determine category from first matched ticker
        category = ticker_mappings[0].sector if ticker_mappings else "Uncategorized"

        created_ats = [v.created_at for v in unique_videos]
        signal = TrendSignal(
            signal_id=str(uuid.uuid4())[:8],
            keyword=keyword,
            category=category,
            video_count=len(unique_videos),
            total_views=total_views,
            view_velocity=velocity,
            sentiment=dominant_sentiment,
            tickers=tickers,
            first_seen=min(created_ats),
            last_seen=max(created_ats),
            signal_strength="weak",  # placeholder, set below
        )
        signal.signal_strength = _strength_label(signal.signal_score)
        signals.append(signal)

    # Sort by signal score descending (highest opportunity first)
    signals.sort(key=lambda s: s.signal_score, reverse=True)
    return signals


def run_scan(videos: list[TikTokVideo]) -> ScanSnapshot:
    """Run a full scan and return a snapshot."""
    signals = analyze_videos(videos)
    return ScanSnapshot(
        snapshot_id=str(uuid.uuid4())[:8],
        scanned_at=datetime.utcnow(),
        videos_scanned=len(videos),
        signals_found=len(signals),
        top_signals=signals[:10],
    )
