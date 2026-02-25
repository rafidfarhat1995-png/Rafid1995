"""
Reddit Economy Scanner
Reads top posts across economic subreddits and surfaces what people
are actually experiencing — not what the headlines say.

Also scans buy/sell/recommend subreddits for organic product enthusiasm —
early signals of consumer spending trends before they show up in earnings.
"""

import logging
from datetime import datetime
from collections import Counter, defaultdict

import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    ECONOMY_SUBREDDITS,
    ECONOMY_KEYWORDS,
    REDDIT_POST_LIMIT,
    REDDIT_CONSUMER_SUBREDDITS,
)

logger = logging.getLogger(__name__)

sentiment_analyzer = SentimentIntensityAnalyzer()


def get_sentiment_label(compound_score: float) -> str:
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    return "neutral"


def analyze_text(text: str) -> dict:
    scores = sentiment_analyzer.polarity_scores(text)
    return {
        "compound": round(scores["compound"], 3),
        "label": get_sentiment_label(scores["compound"]),
    }


def find_matching_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in ECONOMY_KEYWORDS if kw in text_lower]


def scan_reddit_economy() -> dict:
    """
    Pull top posts from economic subreddits.
    Returns sentiment breakdown, keyword hits, and notable posts.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "overall_sentiment": {},
        "sentiment_by_subreddit": {},
        "top_keywords": [],
        "notable_posts": [],
        "pain_points": [],          # high-engagement negative posts
        "green_shoots": [],         # high-engagement positive posts
        "consumer_buzz": [],        # organic product/brand enthusiasm
        "total_posts_scanned": 0,
        "error": None,
    }

    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        results["error"] = (
            "Reddit credentials not set. See .env.example for setup instructions."
        )
        logger.warning(results["error"])
        return results

    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )

        all_sentiments = []
        keyword_counter = Counter()
        notable_posts = []
        sub_sentiments = defaultdict(list)

        for sub_name in ECONOMY_SUBREDDITS:
            logger.info(f"Scanning r/{sub_name}...")
            try:
                subreddit = reddit.subreddit(sub_name)
                posts = list(subreddit.hot(limit=REDDIT_POST_LIMIT))

                for post in posts:
                    full_text = f"{post.title} {post.selftext}"
                    sentiment = analyze_text(full_text)
                    matched_keywords = find_matching_keywords(full_text)

                    all_sentiments.append(sentiment["compound"])
                    sub_sentiments[sub_name].append(sentiment["compound"])
                    keyword_counter.update(matched_keywords)

                    results["total_posts_scanned"] += 1

                    # Keep notable posts (high engagement)
                    if post.score > 500 or post.num_comments > 100:
                        notable_posts.append({
                            "subreddit": sub_name,
                            "title": post.title,
                            "score": post.score,
                            "comments": post.num_comments,
                            "sentiment": sentiment,
                            "keywords": matched_keywords,
                            "url": f"https://reddit.com{post.permalink}",
                        })

            except Exception as sub_error:
                logger.warning(f"Failed to scan r/{sub_name}: {sub_error}")
                continue

        # Overall sentiment
        if all_sentiments:
            avg = sum(all_sentiments) / len(all_sentiments)
            results["overall_sentiment"] = {
                "average_compound": round(avg, 3),
                "label": get_sentiment_label(avg),
                "positive_posts": sum(1 for s in all_sentiments if s >= 0.05),
                "negative_posts": sum(1 for s in all_sentiments if s <= -0.05),
                "neutral_posts": sum(
                    1 for s in all_sentiments if -0.05 < s < 0.05
                ),
            }

        # Per-subreddit sentiment
        for sub, scores in sub_sentiments.items():
            if scores:
                avg = sum(scores) / len(scores)
                results["sentiment_by_subreddit"][sub] = {
                    "average_compound": round(avg, 3),
                    "label": get_sentiment_label(avg),
                    "posts_scanned": len(scores),
                }

        # Top keywords driving the conversation
        results["top_keywords"] = [
            {"keyword": kw, "mentions": count}
            for kw, count in keyword_counter.most_common(15)
        ]

        # Sort notable posts
        notable_posts.sort(key=lambda x: x["score"], reverse=True)
        results["notable_posts"] = notable_posts[:20]

        # Pain points: top negative high-engagement posts
        results["pain_points"] = [
            p for p in notable_posts
            if p["sentiment"]["label"] == "negative"
        ][:5]

        # Green shoots: top positive high-engagement posts
        results["green_shoots"] = [
            p for p in notable_posts
            if p["sentiment"]["label"] == "positive"
        ][:5]

        # --- Consumer Buzz: scan buy/recommend subreddits for product enthusiasm ---
        logger.info("Scanning consumer subreddits for product buzz...")
        consumer_posts = []
        for sub_name in REDDIT_CONSUMER_SUBREDDITS:
            try:
                subreddit = reddit.subreddit(sub_name)
                for post in subreddit.hot(limit=30):
                    full_text = f"{post.title} {post.selftext}"
                    sentiment = analyze_text(full_text)
                    # Only keep positive, high-engagement posts — genuine enthusiasm
                    if post.score > 100 and sentiment["label"] == "positive":
                        consumer_posts.append({
                            "subreddit": sub_name,
                            "title": post.title,
                            "score": post.score,
                            "comments": post.num_comments,
                            "sentiment": sentiment,
                            "url": f"https://reddit.com{post.permalink}",
                        })
                        results["total_posts_scanned"] += 1
            except Exception as sub_error:
                logger.warning(f"Failed to scan r/{sub_name}: {sub_error}")
                continue

        consumer_posts.sort(key=lambda x: x["score"], reverse=True)
        results["consumer_buzz"] = consumer_posts[:15]

        logger.info(
            f"Reddit scan complete: {results['total_posts_scanned']} posts, "
            f"overall sentiment: {results['overall_sentiment'].get('label', 'unknown')}, "
            f"{len(results['consumer_buzz'])} consumer buzz posts"
        )

    except Exception as e:
        results["error"] = f"Reddit scan failed: {str(e)}"
        logger.error(results["error"])

    return results
