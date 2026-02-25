"""
Investment Signals Engine — Chris Camillo Social Arbitrage Lens

Takes raw TikTok, Reddit, and X scan data and extracts actionable
investment signals: products, brands, and behaviors gaining organic
traction before mainstream coverage.

The core idea: if people are genuinely excited about something on social
media, it often shows up in revenue 1-3 quarters later. The gap between
the social signal and the financial recognition is the alpha.
"""

import json
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from config import REPORTS_DIR

logger = logging.getLogger(__name__)

# --- Known brands/tickers to watch for organic mentions ---
# Add more as you discover them. Ticker is None if private/not yet public.
BRAND_TICKER_MAP = {
    # Consumer / Retail
    "stanley": "SWK", "stanley cup": "SWK",
    "lululemon": "LULU", "lulu": "LULU",
    "crocs": "CROX",
    "birkenstock": "BIRK",
    "hoka": "DECK",
    "ugg": "DECK",
    "on running": "ONON", "on cloud": "ONON",
    "new balance": None,  # private
    "skims": None,        # private
    "alo yoga": None,     # private
    "gymshark": None,     # private
    "athletic greens": None, "ag1": None,
    "liquid death": None,
    "olipop": None,
    "poppi": None,
    "prime": "DKNG",      # Logan Paul / KSI
    "celsius": "CELH",
    "ghost energy": None,
    "reign": "MNST",
    "monster": "MNST",
    "red bull": None,     # private
    "yeti": "YETI",
    "hydroflask": "HBB",
    "owala": None,

    # Tech / Apps
    "duolingo": "DUOL",
    "roblox": "RBLX",
    "notion": None,
    "arc browser": None,
    "perplexity": None,
    "cursor": None,
    "bereal": None,
    "substack": None,
    "temu": "PDD",
    "shein": None,        # private
    "whatnot": None,
    "depop": "ETSY",
    "poshmark": "POSH",
    "vinted": None,
    "airbuds": None,

    # Food / Beverage
    "dutch bros": "BROS",
    "cava": "CAVA",
    "sweetgreen": "SG",
    "chipotle": "CMG",
    "wingstop": "WING",
    "shake shack": "SHAK",
    "toast": "TOST",
    "instacart": "CART",
    "gopuff": None,
    "boba": None,

    # Beauty / Health
    "e.l.f": "ELF", "elf cosmetics": "ELF",
    "rare beauty": None,   # private (Selena Gomez)
    "fenty": None,
    "drunk elephant": "BEIG",
    "tatcha": None,
    "glow recipe": None,
    "hims": "HIMS", "hers": "HIMS",
    "ro": None,
    "weight watchers": "WW",
    "noom": None,
    "ozempic": "NVO", "wegovy": "NVO",
    "mounjaro": "LLY",
    "zepbound": "LLY",
    "nutrafol": None,
    "viviscal": None,

    # Entertainment / Media
    "substack": None,
    "patreon": None,
    "spotify": "SPOT",
    "discord": None,
    "twitch": "AMZN",
    "kick": None,

    # Finance / Crypto
    "robinhood": "HOOD",
    "coinbase": "COIN",
    "sofi": "SOFI",
    "chime": None,
    "affirm": "AFRM",
    "klarna": None,
    "bitcoin": "BTC-USD", "btc": "BTC-USD",
    "ethereum": "ETH-USD", "eth": "ETH-USD",
    "solana": "SOL-USD",
}

# Words that indicate genuine enthusiasm (not just awareness)
EXCITEMENT_SIGNALS = [
    "obsessed", "love", "amazing", "incredible", "game changer", "game-changer",
    "can't stop", "addicted", "bought", "ordered", "just got", "just tried",
    "worth it", "10/10", "must have", "must-have", "finally tried",
    "everyone needs", "changed my life", "you need this", "where have you been",
    "how did i live without", "best purchase", "best thing", "underrated",
    "slept on", "hidden gem", "actually works", "actually good",
]

# Words that indicate concern or negative trend
CONCERN_SIGNALS = [
    "overrated", "scam", "disappointed", "returned", "not worth",
    "hate", "terrible", "worst", "boycott", "cancelled", "avoid",
    "never again", "waste of money", "fell off", "peaked",
]

# Velocity keywords — suggest something is accelerating fast
VELOCITY_SIGNALS = [
    "everywhere", "blowing up", "going viral", "can't escape", "all over",
    "suddenly", "overnight", "exploding", "trending", "taking over",
    "sold out", "waitlist", "out of stock", "can't find", "impossible to get",
    "everyone is", "everyone's", "nobody's talking about", "not enough people",
]


def _extract_brand_mentions(text: str) -> list[tuple[str, str | None]]:
    """Find brand names in text. Returns list of (brand, ticker) tuples."""
    text_lower = text.lower()
    found = []
    for brand, ticker in BRAND_TICKER_MAP.items():
        if brand in text_lower:
            found.append((brand, ticker))
    return found


def _score_excitement(text: str) -> dict:
    """Return excitement, concern, and velocity scores for a piece of text."""
    text_lower = text.lower()
    excitement = sum(1 for s in EXCITEMENT_SIGNALS if s in text_lower)
    concern = sum(1 for s in CONCERN_SIGNALS if s in text_lower)
    velocity = sum(1 for s in VELOCITY_SIGNALS if s in text_lower)
    return {"excitement": excitement, "concern": concern, "velocity": velocity}


def extract_investment_signals(
    tiktok_data: dict,
    reddit_data: dict,
    x_data: dict,
) -> dict:
    """
    Main function. Runs all scan data through the investment lens.
    Returns ranked signals with ticker, evidence, and confidence level.
    """
    signals = {}  # brand -> accumulated signal data

    def _add_signal(brand: str, ticker, source: str, text: str, engagement: int = 0):
        if brand not in signals:
            signals[brand] = {
                "brand": brand,
                "ticker": ticker,
                "sources": [],
                "total_mentions": 0,
                "total_engagement": 0,
                "excitement_score": 0,
                "concern_score": 0,
                "velocity_score": 0,
                "evidence": [],
                "is_publicly_traded": ticker is not None,
            }
        s = signals[brand]
        s["total_mentions"] += 1
        s["total_engagement"] += engagement
        if source not in s["sources"]:
            s["sources"].append(source)

        scores = _score_excitement(text)
        s["excitement_score"] += scores["excitement"]
        s["concern_score"] += scores["concern"]
        s["velocity_score"] += scores["velocity"]

        # Keep up to 3 pieces of evidence
        if len(s["evidence"]) < 3:
            s["evidence"].append({
                "source": source,
                "text": text[:200],
                "engagement": engagement,
            })

    # --- Mine TikTok ---
    for vid in tiktok_data.get("top_videos", []):
        text = vid.get("description", "")
        engagement = vid.get("plays", 0) // 1000  # normalize
        for brand, ticker in _extract_brand_mentions(text):
            _add_signal(brand, ticker, "tiktok", text, engagement)

    for tag_item in tiktok_data.get("trending_hashtags", []):
        tag = tag_item.get("tag", "")
        for brand, ticker in _extract_brand_mentions(tag):
            _add_signal(brand, ticker, "tiktok", tag, tag_item.get("appearances", 0))

    for theme_item in tiktok_data.get("top_themes", []):
        theme = theme_item.get("theme", "")
        for brand, ticker in _extract_brand_mentions(theme):
            _add_signal(brand, ticker, "tiktok", theme, theme_item.get("frequency", 0))

    # --- Mine Reddit ---
    for post in reddit_data.get("notable_posts", []):
        text = post.get("title", "")
        engagement = post.get("score", 0)
        for brand, ticker in _extract_brand_mentions(text):
            _add_signal(brand, ticker, f"reddit/r/{post.get('subreddit','')}", text, engagement)

    for keyword_item in reddit_data.get("top_keywords", []):
        kw = keyword_item.get("keyword", "")
        for brand, ticker in _extract_brand_mentions(kw):
            _add_signal(brand, ticker, "reddit", kw, keyword_item.get("mentions", 0))

    # --- Mine X ---
    for post in x_data.get("top_posts", []):
        text = post.get("text", "")
        engagement = post.get("likes", 0) + post.get("retweets", 0) * 2
        for brand, ticker in _extract_brand_mentions(text):
            _add_signal(brand, ticker, "x", text, engagement)

    for post in x_data.get("account_highlights", []):
        text = post.get("text", "")
        engagement = post.get("likes", 0) + post.get("retweets", 0) * 2
        for brand, ticker in _extract_brand_mentions(text):
            _add_signal(brand, ticker, "x", text, engagement)

    # --- Score and rank ---
    for brand, s in signals.items():
        # Net excitement: excitement minus concern, weighted by velocity
        net_excitement = s["excitement_score"] - (s["concern_score"] * 2)
        velocity_boost = s["velocity_score"] * 0.5
        source_diversity = len(s["sources"])  # appearing on multiple platforms = stronger

        s["signal_score"] = round(
            (s["total_mentions"] * 1.0)
            + (s["total_engagement"] * 0.01)
            + (net_excitement * 2.0)
            + (velocity_boost * 1.5)
            + (source_diversity * 3.0),  # cross-platform = high weight
            2,
        )

        # Confidence level
        if s["signal_score"] >= 15 and source_diversity >= 2:
            s["confidence"] = "HIGH"
        elif s["signal_score"] >= 7:
            s["confidence"] = "MEDIUM"
        else:
            s["confidence"] = "LOW"

        # Classify the signal direction
        if s["concern_score"] > s["excitement_score"]:
            s["direction"] = "BEARISH"
        elif s["excitement_score"] > 0 or s["velocity_score"] > 0:
            s["direction"] = "BULLISH"
        else:
            s["direction"] = "NEUTRAL"

    # Sort by signal score
    ranked = sorted(signals.values(), key=lambda x: x["signal_score"], reverse=True)

    # Split into categories
    top_signals = [s for s in ranked if s["direction"] == "BULLISH"][:10]
    watch_list = [s for s in ranked if s["direction"] == "NEUTRAL"][:5]
    fade_signals = [s for s in ranked if s["direction"] == "BEARISH"][:5]
    public_only = [s for s in top_signals if s["is_publicly_traded"]]

    return {
        "generated_at": datetime.now().isoformat(),
        "top_signals": top_signals,
        "public_tickers": public_only,        # tradeable now
        "private_to_watch": [                  # IPO pipeline / acquisition targets
            s for s in top_signals if not s["is_publicly_traded"]
        ][:5],
        "watch_list": watch_list,
        "fade_signals": fade_signals,
        "total_brands_detected": len(signals),
        "methodology": (
            "Social arbitrage: brands gaining organic excitement on TikTok, Reddit, "
            "and X before mainstream financial coverage. High cross-platform presence "
            "= stronger signal. Velocity signals (sold out, everywhere, blowing up) "
            "weighted extra. Concern signals reduce score."
        ),
    }


def save_signals(signals: dict, date_str: str) -> str:
    """Save investment signals to a dedicated file."""
    Path(REPORTS_DIR).mkdir(exist_ok=True)
    path = f"{REPORTS_DIR}/{date_str}_signals.json"
    with open(path, "w") as f:
        json.dump(signals, f, indent=2)
    return path


def render_signals_markdown(signals: dict) -> str:
    """Render investment signals as a standalone markdown section."""
    lines = []
    lines.append("---\n## Investment Signals — Social Arbitrage\n")
    lines.append(
        f"*{signals.get('total_brands_detected', 0)} brands detected across all platforms. "
        f"Ranked by organic excitement + cross-platform velocity.*\n"
    )

    # Publicly traded — actionable now
    public = signals.get("public_tickers", [])
    if public:
        lines.append("### Publicly Traded — Actionable Signals\n")
        lines.append("| Brand | Ticker | Signal | Confidence | Sources | Evidence |")
        lines.append("|-------|--------|--------|------------|---------|----------|")
        for s in public:
            sources = ", ".join(s["sources"])
            evidence = s["evidence"][0]["text"][:80] + "..." if s["evidence"] else ""
            direction_emoji = "🟢" if s["direction"] == "BULLISH" else "🔴"
            lines.append(
                f"| **{s['brand'].title()}** | `{s['ticker']}` | "
                f"{direction_emoji} {s['direction']} (score: {s['signal_score']}) | "
                f"{s['confidence']} | {sources} | *\"{evidence}\"* |"
            )

    # Private brands — watch for IPO/acquisition
    private = signals.get("private_to_watch", [])
    if private:
        lines.append("\n### Private Brands Gaining Traction — Watch for IPO/Acquisition\n")
        for s in private:
            lines.append(
                f"- **{s['brand'].title()}** — score: {s['signal_score']}, "
                f"mentions: {s['total_mentions']}, "
                f"sources: {', '.join(s['sources'])}"
            )
            if s["evidence"]:
                lines.append(f"  > \"{s['evidence'][0]['text'][:120]}\"")

    # Fade signals — bearish
    fade = signals.get("fade_signals", [])
    if fade:
        lines.append("\n### Fade Signals — Declining Organic Enthusiasm\n")
        for s in fade:
            ticker_str = f" (`{s['ticker']}`)" if s["ticker"] else ""
            lines.append(
                f"- **{s['brand'].title()}**{ticker_str} — "
                f"concern score: {s['concern_score']}, "
                f"sources: {', '.join(s['sources'])}"
            )

    lines.append(
        f"\n*Methodology: {signals.get('methodology', '')}*"
    )

    return "\n".join(lines)
