"""
X (Twitter) AI Updates Scanner
Monitors X for the latest AI news, model releases, and research breakthroughs.
Tracks key accounts, hashtags, and keywords in the AI space.
Requires a free X Developer account at https://developer.x.com
"""

import logging
from datetime import datetime, timezone, timedelta
from collections import Counter

import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import (
    X_BEARER_TOKEN,
    X_AI_KEYWORDS,
    X_AI_ACCOUNTS,
    X_MAX_RESULTS_PER_QUERY,
)

logger = logging.getLogger(__name__)
sentiment_analyzer = SentimentIntensityAnalyzer()


# --- AI Labs & Key Researchers to monitor ---
# These are the accounts that break news first
WATCHLIST = [
    "OpenAI",
    "AnthropicAI",
    "GoogleDeepMind",
    "Meta",
    "Microsoft",
    "sama",          # Sam Altman
    "ylecun",        # Yann LeCun
    "karpathy",      # Andrej Karpathy
    "demishassabis", # Demis Hassabis
    "gdb",           # Greg Brockman
    "ilyasut",       # Ilya Sutskever
    "DrJimFan",      # Jim Fan (NVIDIA)
    "hardmaru",      # David Ha
    "fchollet",      # François Chollet
    "EMostaque",     # Emad Mostaque
    "huggingface",
    "MistralAI",
    "xai",           # Elon's AI co
    "NvidiaAI",
]


def _classify_ai_topic(text: str) -> list[str]:
    """Tag a post with relevant AI sub-topics."""
    text_lower = text.lower()
    topics = []

    topic_map = {
        "model release": ["new model", "release", "launched", "introducing", "announcing"],
        "research paper": ["paper", "arxiv", "research", "study", "benchmark"],
        "safety": ["ai safety", "alignment", "risk", "dangerous", "regulate"],
        "agents": ["agent", "autonomous", "agentic", "tool use"],
        "image/video": ["image generation", "video generation", "sora", "dall-e", "midjourney", "flux"],
        "coding": ["copilot", "code generation", "devin", "cursor", "coding ai"],
        "open source": ["open source", "open-source", "weights", "hugging face", "ollama"],
        "funding": ["funding", "raised", "billion", "valuation", "investment"],
        "regulation": ["regulation", "ban", "law", "congress", "eu ai act", "policy"],
        "hardware": ["gpu", "chip", "nvidia", "tpu", "hardware", "inference"],
    }

    for topic, keywords in topic_map.items():
        if any(kw in text_lower for kw in keywords):
            topics.append(topic)

    return topics if topics else ["general ai"]


def scan_x_for_ai(hours_back: int = 24) -> dict:
    """
    Search X for AI updates from the past N hours.
    Returns top posts, trending topics, key account activity, and sentiment.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "hours_scanned": hours_back,
        "top_posts": [],
        "breaking_news": [],       # high-engagement posts from last 6 hours
        "account_highlights": [],  # notable posts from watchlist accounts
        "trending_topics": [],
        "topic_breakdown": {},
        "overall_sentiment": {},
        "total_posts_scanned": 0,
        "error": None,
    }

    if not X_BEARER_TOKEN:
        results["error"] = (
            "X_BEARER_TOKEN not set. See .env.example — get a free key at "
            "https://developer.x.com"
        )
        logger.warning(results["error"])
        return results

    try:
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN, wait_on_rate_limit=True)

        start_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        all_tweets = []
        topic_counter = Counter()
        sentiment_scores = []

        # Build search query covering all AI keywords + filter out noise
        keyword_query = " OR ".join(f'"{kw}"' for kw in X_AI_KEYWORDS[:10])
        search_query = (
            f"({keyword_query}) "
            f"lang:en -is:retweet -is:reply "
            f"has:mentions OR has:links"
        )

        logger.info("Searching X for AI updates...")
        response = client.search_recent_tweets(
            query=search_query,
            max_results=min(X_MAX_RESULTS_PER_QUERY, 100),
            start_time=start_time,
            tweet_fields=["created_at", "public_metrics", "author_id", "text"],
            expansions=["author_id"],
            user_fields=["username", "verified", "public_metrics"],
        )

        # Build author lookup
        author_map = {}
        if response.includes and "users" in response.includes:
            for user in response.includes["users"]:
                author_map[user.id] = {
                    "username": user.username,
                    "followers": user.public_metrics.get("followers_count", 0),
                }

        if response.data:
            for tweet in response.data:
                metrics = tweet.public_metrics or {}
                engagement = (
                    metrics.get("like_count", 0)
                    + metrics.get("retweet_count", 0) * 2
                    + metrics.get("reply_count", 0)
                )

                author_info = author_map.get(tweet.author_id, {})
                topics = _classify_ai_topic(tweet.text)
                topic_counter.update(topics)

                scores = sentiment_analyzer.polarity_scores(tweet.text)
                sentiment_scores.append(scores["compound"])

                tweet_data = {
                    "text": tweet.text,
                    "author": author_info.get("username", "unknown"),
                    "author_followers": author_info.get("followers", 0),
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "engagement_score": engagement,
                    "topics": topics,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
                    "is_from_watchlist": author_info.get("username", "").lower()
                        in [a.lower() for a in WATCHLIST],
                }
                all_tweets.append(tweet_data)
                results["total_posts_scanned"] += 1

        # Also pull recent posts from key watchlist accounts directly
        logger.info("Pulling posts from key AI accounts...")
        for username in X_AI_ACCOUNTS[:8]:  # limit to top 8 to respect rate limits
            try:
                user_resp = client.get_user(username=username)
                if not user_resp.data:
                    continue

                user_tweets = client.get_users_tweets(
                    id=user_resp.data.id,
                    max_results=10,
                    start_time=start_time,
                    tweet_fields=["created_at", "public_metrics", "text"],
                    exclude=["retweets", "replies"],
                )

                if user_tweets.data:
                    for tweet in user_tweets.data:
                        metrics = tweet.public_metrics or {}
                        engagement = (
                            metrics.get("like_count", 0)
                            + metrics.get("retweet_count", 0) * 2
                        )
                        if engagement > 100:  # only notable posts
                            results["account_highlights"].append({
                                "account": f"@{username}",
                                "text": tweet.text[:280],
                                "likes": metrics.get("like_count", 0),
                                "retweets": metrics.get("retweet_count", 0),
                                "topics": _classify_ai_topic(tweet.text),
                                "created_at": tweet.created_at.isoformat()
                                    if tweet.created_at else "",
                            })
            except Exception as acc_err:
                logger.warning(f"Could not fetch @{username}: {acc_err}")
                continue

        # Sort all posts by engagement
        all_tweets.sort(key=lambda x: x["engagement_score"], reverse=True)
        results["top_posts"] = all_tweets[:15]

        # Breaking news: high-engagement posts from last 6 hours
        six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=6)
        results["breaking_news"] = [
            t for t in all_tweets
            if t["engagement_score"] > 500
            and t.get("created_at", "")
            and datetime.fromisoformat(t["created_at"]) > six_hours_ago
        ][:5]

        # Account highlights sorted by engagement
        results["account_highlights"].sort(
            key=lambda x: x["likes"] + x["retweets"] * 2, reverse=True
        )
        results["account_highlights"] = results["account_highlights"][:10]

        # Topic breakdown
        results["topic_breakdown"] = dict(topic_counter.most_common())
        results["trending_topics"] = [
            {"topic": topic, "mentions": count}
            for topic, count in topic_counter.most_common(8)
        ]

        # Overall sentiment
        if sentiment_scores:
            avg = sum(sentiment_scores) / len(sentiment_scores)
            results["overall_sentiment"] = {
                "average_compound": round(avg, 3),
                "label": "positive" if avg >= 0.05 else ("negative" if avg <= -0.05 else "neutral"),
                "excited_posts": sum(1 for s in sentiment_scores if s >= 0.2),
                "concerned_posts": sum(1 for s in sentiment_scores if s <= -0.2),
            }

        logger.info(
            f"X scan complete: {results['total_posts_scanned']} posts, "
            f"{len(results['account_highlights'])} account highlights"
        )

    except tweepy.TweepyException as e:
        results["error"] = f"X API error: {str(e)}"
        logger.error(results["error"])
    except Exception as e:
        results["error"] = f"X scan failed: {str(e)}"
        logger.error(results["error"])

    return results
