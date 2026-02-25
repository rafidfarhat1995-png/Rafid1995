"""
Quick test for the investment signals engine.
Uses synthetic mock data — no API keys required.

Run:
    python test_signals.py
"""

import json
from investment_signals import extract_investment_signals, render_signals_markdown

# --- Mock TikTok data (mimics what tiktok_scanner.py returns) ---
MOCK_TIKTOK = {
    "trending_hashtags": [
        {"tag": "#celsiusenergy", "appearances": 12},
        {"tag": "#stanley", "appearances": 8},
        {"tag": "#olipop", "appearances": 7},
        {"tag": "#onrunning", "appearances": 5},
        {"tag": "#dutchbros", "appearances": 4},
    ],
    "top_themes": [
        {"theme": "celsius", "frequency": 9},
        {"theme": "stanley", "frequency": 6},
        {"theme": "hoka", "frequency": 5},
        {"theme": "cava", "frequency": 3},
    ],
    "top_videos": [
        {
            "description": "obsessed with my new Stanley cup honestly everyone needs this "
                           "in their life changed my life #stanley #waterbottle",
            "plays": 4_200_000,
            "likes": 380_000,
            "engagement_ratio": 0.090,
            "author": "hydrationqueen",
            "has_excitement_language": True,
        },
        {
            "description": "trying celsius for the first time omg it actually works "
                           "10/10 would recommend #celsiusenergy #gym",
            "plays": 2_100_000,
            "likes": 250_000,
            "engagement_ratio": 0.119,
            "author": "fitcheck2024",
            "has_excitement_language": True,
        },
        {
            "description": "dutch bros blowing up in my city sold out of the new drink "
                           "everywhere i go #dutchbros #coffee",
            "plays": 950_000,
            "likes": 91_000,
            "engagement_ratio": 0.096,
            "author": "coffeediary",
            "has_excitement_language": True,
        },
        {
            "description": "hoka clifton review after 3 months of running worth every penny",
            "plays": 700_000,
            "likes": 55_000,
            "engagement_ratio": 0.079,
            "author": "runningreviews",
            "has_excitement_language": True,
        },
        {
            "description": "trying cava for the first time hidden gem honestly slept on this",
            "plays": 1_500_000,
            "likes": 130_000,
            "engagement_ratio": 0.087,
            "author": "foodtok",
            "has_excitement_language": True,
        },
    ],
    "under_the_radar": [
        {
            "description": "nobody's talking about on running shoes but they changed my training",
            "plays": 180_000,
            "likes": 32_000,
            "engagement_ratio": 0.178,
            "author": "trainwithme",
            "has_excitement_language": True,
        },
    ],
    "acceleration_signals": [
        {"tag": "#celsiusenergy", "excited_videos": 6},
        {"tag": "#stanley", "excited_videos": 5},
    ],
    "error": None,
}

# --- Mock Reddit data (mimics what reddit_scanner.py returns) ---
MOCK_REDDIT = {
    "notable_posts": [
        {
            "title": "Celsius is genuinely the best pre-workout replacement I've found",
            "subreddit": "Fitness",
            "score": 4200,
            "sentiment": {"label": "positive", "compound": 0.88},
        },
        {
            "title": "Dutch Bros is expanding fast — anyone else noticing the lines?",
            "subreddit": "Coffee",
            "score": 1800,
            "sentiment": {"label": "positive", "compound": 0.62},
        },
        {
            "title": "ELF cosmetics is just as good as brands 3x the price",
            "subreddit": "femalefashionadvice",
            "score": 3100,
            "sentiment": {"label": "positive", "compound": 0.79},
        },
    ],
    "top_keywords": [
        {"keyword": "celsius", "mentions": 22},
        {"keyword": "stanley cup", "mentions": 14},
        {"keyword": "cava", "mentions": 11},
        {"keyword": "hoka", "mentions": 8},
        {"keyword": "elf cosmetics", "mentions": 7},
    ],
    "consumer_buzz": [
        {
            "title": "Switched to Olipop and haven't looked back — actually tastes good",
            "subreddit": "EatCheapAndHealthy",
            "score": 2900,
            "comments": 187,
            "sentiment": {"label": "positive", "compound": 0.80},
            "url": "https://reddit.com/r/EatCheapAndHealthy/example",
        },
        {
            "title": "HOKA vs On Running — which do you prefer for long runs?",
            "subreddit": "running",
            "score": 1400,
            "comments": 312,
            "sentiment": {"label": "positive", "compound": 0.55},
            "url": "https://reddit.com/r/running/example",
        },
    ],
    "error": None,
}

# --- Mock X data ---
MOCK_X = {
    "top_posts": [
        {
            "text": "Celsius Holdings ($CELH) is everywhere on TikTok right now — "
                    "every gym video features it. This is what early looks like.",
            "likes": 890,
            "retweets": 210,
        },
        {
            "text": "Stanley cup obsession is absolutely real — sold out at Target again. $SWK",
            "likes": 440,
            "retweets": 95,
        },
    ],
    "account_highlights": [],
    "error": None,
}


def run_test():
    print("=" * 60)
    print("INVESTMENT SIGNALS ENGINE — TEST RUN")
    print("=" * 60)

    signals = extract_investment_signals(MOCK_TIKTOK, MOCK_REDDIT, MOCK_X)

    print(f"\nTotal brands detected: {signals['total_brands_detected']}")
    print(f"Public tickers found:  {len(signals['public_tickers'])}")
    print(f"Private brands:        {len(signals['private_to_watch'])}")
    print(f"Fade signals:          {len(signals['fade_signals'])}")

    print("\n--- TOP PUBLIC TICKER SIGNALS ---")
    for s in signals["public_tickers"]:
        print(
            f"  {s['brand'].upper():20s} | {s['ticker']:8s} | "
            f"{s['direction']:8s} | confidence: {s['confidence']:6s} | "
            f"score: {s['signal_score']}"
        )
        for e in s["evidence"][:1]:
            print(f"    via {e['source']}: \"{e['text'][:80]}\"")

    print("\n--- PRIVATE BRANDS TO WATCH ---")
    for s in signals["private_to_watch"]:
        print(f"  {s['brand'].upper():20s} | sources: {', '.join(s['sources'])}")

    print("\n--- MARKDOWN REPORT PREVIEW ---")
    print(render_signals_markdown(signals))

    # Verify data shape
    assert isinstance(signals["top_signals"], list)
    assert all("signal_score" in s for s in signals["top_signals"])
    assert all("ticker" in s for s in signals["public_tickers"])
    assert all(s["direction"] in ("BULLISH", "BEARISH", "NEUTRAL") for s in signals["top_signals"])
    assert all(s["confidence"] in ("HIGH", "MEDIUM", "LOW") for s in signals["top_signals"])

    print("\n[PASS] All assertions passed.")


if __name__ == "__main__":
    run_test()
