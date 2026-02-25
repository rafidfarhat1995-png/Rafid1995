"""
TikTok Trend Scanner
Pulls trending hashtags, sounds, video themes, and product/brand signals from TikTok.
Requires ms_token from a logged-in TikTok browser session.

Investment lens: captures early organic excitement around products/brands
before mainstream financial coverage — the Chris Camillo social arbitrage approach.
"""

import asyncio
import logging
from datetime import datetime
from collections import Counter
import re

from config import TIKTOK_MS_TOKEN, TIKTOK_TREND_CATEGORIES

logger = logging.getLogger(__name__)


def extract_themes_from_description(description: str) -> list[str]:
    """Pull meaningful words from a video description, strip fluff."""
    stop_words = {
        "the", "a", "an", "is", "it", "in", "on", "at", "to", "for",
        "of", "and", "or", "but", "with", "this", "that", "was", "are",
        "be", "been", "have", "has", "do", "did", "will", "would", "i",
        "you", "he", "she", "they", "we", "my", "your", "his", "her",
        "its", "our", "their", "what", "how", "why", "when", "where",
    }
    words = re.findall(r'\b[a-zA-Z]{4,}\b', description.lower())
    return [w for w in words if w not in stop_words]


async def scan_tiktok_trends() -> dict:
    """
    Scan TikTok for trending content.
    Returns structured data: hashtags, sounds, themes, top videos.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "trending_hashtags": [],
        "trending_sounds": [],
        "top_themes": [],
        "top_videos": [],
        "under_the_radar": [],   # high engagement but niche — early signal
        "acceleration_signals": [],  # suddenly appearing across many videos
        "error": None,
    }

    if not TIKTOK_MS_TOKEN:
        results["error"] = (
            "TIKTOK_MS_TOKEN not set. See .env.example for setup instructions."
        )
        logger.warning(results["error"])
        return results

    try:
        from TikTokApi import TikTokApi

        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[TIKTOK_MS_TOKEN],
                num_sessions=1,
                sleep_after=3,
                headless=True,
            )

            # --- Fetch trending videos ---
            logger.info("Fetching trending videos...")
            hashtag_counts = Counter()
            sound_counts = Counter()
            theme_words = []
            top_videos = []
            # Track hashtags that appear together with excitement language
            excitement_tags = Counter()

            async for video in api.trending.videos(count=150):
                video_data = video.as_dict

                # Collect hashtags
                challenges = video_data.get("challenges", [])
                for tag in challenges:
                    title = tag.get("title", "").lower()
                    if title:
                        hashtag_counts[f"#{title}"] += 1

                # Collect sounds
                music = video_data.get("music", {})
                if music:
                    sound_name = music.get("title", "")
                    author = music.get("authorName", "")
                    if sound_name:
                        sound_counts[f"{sound_name} — {author}"] += 1

                # Collect themes from descriptions
                desc = video_data.get("desc", "")
                theme_words.extend(extract_themes_from_description(desc))

                # Check for excitement language in descriptions
                desc_lower = desc.lower()
                excitement_words = [
                    "obsessed", "love", "amazing", "game changer", "bought",
                    "ordered", "must have", "changed my life", "you need",
                    "everyone needs", "worth it", "underrated", "slept on",
                    "hidden gem", "actually works", "blowing up", "sold out",
                ]
                has_excitement = any(w in desc_lower for w in excitement_words)

                # Top videos by play count
                stats = video_data.get("stats", {})
                play_count = stats.get("playCount", 0)
                like_count = stats.get("diggCount", 0)
                share_count = stats.get("shareCount", 0)

                # Engagement ratio: likes/plays — high ratio = genuine enthusiasm
                engagement_ratio = (like_count / play_count) if play_count > 0 else 0

                video_entry = {
                    "description": desc[:150],
                    "plays": play_count,
                    "likes": like_count,
                    "shares": share_count,
                    "engagement_ratio": round(engagement_ratio, 4),
                    "author": video_data.get("author", {}).get("uniqueId", ""),
                    "has_excitement_language": has_excitement,
                }

                if play_count > 100_000:
                    top_videos.append(video_entry)

                # Under-the-radar: high engagement ratio but lower total plays
                # These are early signals before they explode
                if 10_000 < play_count < 500_000 and engagement_ratio > 0.15:
                    results["under_the_radar"].append(video_entry)

                # Tag excitement hashtags
                if has_excitement:
                    for tag in challenges:
                        title = tag.get("title", "").lower()
                        if title:
                            excitement_tags[f"#{title}"] += 1

            # Sort and format results
            results["trending_hashtags"] = [
                {"tag": tag, "appearances": count}
                for tag, count in hashtag_counts.most_common(20)
            ]

            results["trending_sounds"] = [
                {"sound": sound, "uses": count}
                for sound, count in sound_counts.most_common(10)
            ]

            theme_counter = Counter(theme_words)
            results["top_themes"] = [
                {"theme": word, "frequency": count}
                for word, count in theme_counter.most_common(25)
            ]

            results["top_videos"] = sorted(
                top_videos, key=lambda x: x["plays"], reverse=True
            )[:10]

            # Acceleration signals: hashtags that appear frequently with excitement language
            results["acceleration_signals"] = [
                {"tag": tag, "excited_videos": count}
                for tag, count in excitement_tags.most_common(10)
                if count >= 2  # appeared with excitement in multiple videos
            ]

            results["under_the_radar"] = sorted(
                results["under_the_radar"],
                key=lambda x: x["engagement_ratio"],
                reverse=True,
            )[:8]

            logger.info(
                f"TikTok scan complete: "
                f"{len(results['trending_hashtags'])} hashtags, "
                f"{len(results['top_videos'])} top videos, "
                f"{len(results['under_the_radar'])} under-the-radar signals"
            )

    except ImportError:
        results["error"] = (
            "TikTokApi not installed. Run: pip install TikTokApi"
        )
        logger.error(results["error"])

    except Exception as e:
        results["error"] = f"TikTok scan failed: {str(e)}"
        logger.error(results["error"])

    return results


def run_tiktok_scan() -> dict:
    """Synchronous wrapper for use outside async contexts."""
    return asyncio.run(scan_tiktok_trends())
