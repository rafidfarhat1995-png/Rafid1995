"""
TikTok Trend Scanner
Pulls trending hashtags, sounds, and video themes from TikTok.
Requires ms_token from a logged-in TikTok browser session.
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

            # --- Trending Hashtags ---
            logger.info("Fetching trending hashtags...")
            hashtag_counts = Counter()
            sound_counts = Counter()
            theme_words = []
            top_videos = []

            async for video in api.trending.videos(count=100):
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

                # Top videos by play count
                stats = video_data.get("stats", {})
                play_count = stats.get("playCount", 0)
                if play_count > 100_000:
                    top_videos.append({
                        "description": desc[:120],
                        "plays": play_count,
                        "likes": stats.get("diggCount", 0),
                        "shares": stats.get("shareCount", 0),
                        "author": video_data.get("author", {}).get("uniqueId", ""),
                    })

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

            logger.info(
                f"TikTok scan complete: "
                f"{len(results['trending_hashtags'])} hashtags, "
                f"{len(results['top_videos'])} top videos"
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
