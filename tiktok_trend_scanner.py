"""
TikTok Trend Scanner
---------------------
Scans TikTok for trending content based on keywords every day from 7–8 PM.
Uses the unofficial TikTokApi library (Playwright-based).

Setup:
    pip install TikTokApi schedule
    python -m playwright install chromium

Optional email summary:
    Fill in the EMAIL CONFIG section below.
"""

import csv
import json
import logging
import os
import smtplib
import time
import asyncio
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import schedule
from TikTokApi import TikTokApi

# ---------------------------------------------------------------------------
# CONFIG — edit these before running
# ---------------------------------------------------------------------------

KEYWORDS = [
    "AI",
    "crypto",
    "fashion",
    "fitness",
    "viral dance",
]

# How many videos to pull per keyword per scan
VIDEOS_PER_KEYWORD = 20

# How many hashtag videos to pull per keyword
HASHTAG_VIDEOS = 10

# Scan window: start and end time (24-hour format)
SCAN_START = "19:00"   # 7:00 PM
SCAN_END   = "20:00"   # 8:00 PM

# How often (minutes) to scan within the window
SCAN_INTERVAL_MINUTES = 15

# Where results are saved
OUTPUT_DIR = "tiktok_results"

# ms_token cookie value from your browser (improves results, optional)
# Steps: Open TikTok in Chrome → F12 → Application → Cookies → copy ms_token value
MS_TOKEN = os.environ.get("TIKTOK_MS_TOKEN", None)

# --- Email alerts (optional) ------------------------------------------------
EMAIL_ENABLED   = False
EMAIL_SENDER    = "you@gmail.com"
EMAIL_PASSWORD  = ""              # Gmail App Password
EMAIL_RECIPIENT = "you@gmail.com"
SMTP_HOST       = "smtp.gmail.com"
SMTP_PORT       = 587
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def current_time_str() -> str:
    return datetime.now().strftime("%H:%M")


def in_scan_window() -> bool:
    """Return True if the current time is inside the 7–8 PM scan window."""
    now = current_time_str()
    return SCAN_START <= now < SCAN_END


def load_seen_ids(filepath: str) -> set[str]:
    if os.path.exists(filepath):
        with open(filepath) as f:
            return set(json.load(f))
    return set()


def save_seen_ids(filepath: str, ids: set[str]) -> None:
    with open(filepath, "w") as f:
        json.dump(sorted(ids), f, indent=2)


def append_to_csv(rows: list[dict], filepath: str) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    write_header = not os.path.exists(filepath)
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def send_email(subject: str, body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECIPIENT
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        log.info("Email sent to %s", EMAIL_RECIPIENT)
    except Exception as exc:
        log.error("Email failed: %s", exc)


def format_email_body(results: list[dict]) -> str:
    lines = [f"TikTok Trend Scan — {today_str()}\n"]
    for r in results:
        lines += [
            f"  Keyword : {r['keyword']}",
            f"  Author  : @{r['author']}",
            f"  Desc    : {r['description'][:80]}",
            f"  Likes   : {r['likes']:,}",
            f"  Views   : {r['views']:,}",
            f"  URL     : {r['url']}",
            "",
        ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# TikTok async scan
# ---------------------------------------------------------------------------

def extract_video_data(video, keyword: str) -> dict:
    """Pull the fields we care about from a TikTokApi video object."""
    try:
        desc  = getattr(video, "desc", "") or ""
        stats = getattr(video, "stats", {}) or {}

        if hasattr(stats, "__dict__"):          # object-style
            likes  = getattr(stats, "digg_count",   0) or 0
            views  = getattr(stats, "play_count",    0) or 0
            shares = getattr(stats, "share_count",   0) or 0
            comments = getattr(stats, "comment_count", 0) or 0
        else:                                   # dict-style
            likes  = stats.get("diggCount",    0)
            views  = stats.get("playCount",    0)
            shares = stats.get("shareCount",   0)
            comments = stats.get("commentCount", 0)

        author = getattr(video, "author", None)
        author_name = (
            getattr(author, "unique_id", "unknown")
            if author else "unknown"
        )

        hashtags = [
            f"#{getattr(h, 'name', h)}"
            for h in (getattr(video, "hashtags", []) or [])
        ]

        video_id = getattr(video, "id", "")
        url = f"https://www.tiktok.com/@{author_name}/video/{video_id}"

        return {
            "scanned_at":  now_str(),
            "keyword":     keyword,
            "video_id":    str(video_id),
            "author":      author_name,
            "description": desc[:200],
            "hashtags":    " ".join(hashtags[:10]),
            "likes":       likes,
            "views":       views,
            "shares":      shares,
            "comments":    comments,
            "url":         url,
        }
    except Exception as exc:
        log.debug("Could not extract video fields: %s", exc)
        return {}


async def scan_keyword(api: TikTokApi, keyword: str, seen_ids: set[str]) -> list[dict]:
    """Search TikTok for a keyword and return new video records."""
    new_rows = []

    # --- Search results ---
    try:
        async for video in api.search.videos(keyword, count=VIDEOS_PER_KEYWORD):
            row = extract_video_data(video, keyword)
            if not row or row["video_id"] in seen_ids:
                continue
            seen_ids.add(row["video_id"])
            new_rows.append(row)
    except Exception as exc:
        log.warning("[%s] Search failed: %s", keyword, exc)

    # --- Hashtag feed ---
    clean_kw = keyword.lstrip("#").replace(" ", "")
    try:
        tag = api.hashtag(name=clean_kw)
        async for video in tag.videos(count=HASHTAG_VIDEOS):
            row = extract_video_data(video, f"#{clean_kw}")
            if not row or row["video_id"] in seen_ids:
                continue
            seen_ids.add(row["video_id"])
            new_rows.append(row)
    except Exception as exc:
        log.debug("[#%s] Hashtag feed failed (may not exist): %s", clean_kw, exc)

    return new_rows


async def run_async_scan() -> list[dict]:
    """Run one full scan across all keywords."""
    all_new: list[dict] = []
    ms_tokens = [MS_TOKEN] if MS_TOKEN else None

    async with TikTokApi() as api:
        if ms_tokens:
            await api.create_sessions(ms_tokens=ms_tokens, num_sessions=1,
                                      sleep_after=3, headless=True)
        else:
            await api.create_sessions(num_sessions=1, sleep_after=3,
                                      headless=True)

        seen_path = os.path.join(OUTPUT_DIR, "seen_ids.json")
        seen_ids  = load_seen_ids(seen_path)

        for keyword in KEYWORDS:
            log.info("  Scanning keyword: %s", keyword)
            rows = await scan_keyword(api, keyword, seen_ids)
            log.info("    → %d new video(s)", len(rows))
            all_new.extend(rows)
            await asyncio.sleep(2)          # polite delay between keywords

        save_seen_ids(seen_path, seen_ids)

    return all_new


# ---------------------------------------------------------------------------
# Trend summary
# ---------------------------------------------------------------------------

def print_trend_summary(rows: list[dict]) -> None:
    if not rows:
        log.info("No new results to summarise.")
        return

    # Top videos by views
    top = sorted(rows, key=lambda r: r.get("views", 0), reverse=True)[:5]
    log.info("\n--- Top 5 videos by views ---")
    for i, r in enumerate(top, 1):
        log.info(
            "%d. [%s] @%s | views: %s | likes: %s\n   %s",
            i, r["keyword"], r["author"],
            f"{r['views']:,}", f"{r['likes']:,}",
            r["url"],
        )

    # Trending hashtags
    all_tags: dict[str, int] = {}
    for r in rows:
        for tag in r.get("hashtags", "").split():
            all_tags[tag] = all_tags.get(tag, 0) + 1

    if all_tags:
        top_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]
        log.info("\n--- Top hashtags in results ---")
        for tag, count in top_tags:
            log.info("  %s  (%d videos)", tag, count)


# ---------------------------------------------------------------------------
# Scheduled scan
# ---------------------------------------------------------------------------

def run_scan() -> None:
    if not in_scan_window():
        log.debug("Outside scan window (%s–%s), skipping.", SCAN_START, SCAN_END)
        return

    log.info("=== TikTok scan started (%s) ===", now_str())
    ensure_output_dir()

    csv_path = os.path.join(OUTPUT_DIR, f"trends_{today_str()}.csv")

    try:
        rows = asyncio.run(run_async_scan())
    except Exception as exc:
        log.error("Scan failed: %s", exc)
        return

    if rows:
        append_to_csv(rows, csv_path)
        log.info("Saved %d new record(s) → %s", len(rows), csv_path)
        print_trend_summary(rows)

        if EMAIL_ENABLED:
            send_email(
                subject=f"TikTok Trends: {len(rows)} new videos — {today_str()}",
                body=format_email_body(rows),
            )
    else:
        log.info("No new content found this scan.")

    log.info("=== Scan complete ===\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("TikTok Trend Scanner starting.")
    log.info("Keywords : %s", ", ".join(KEYWORDS))
    log.info("Window   : %s – %s  (every %d min)", SCAN_START, SCAN_END, SCAN_INTERVAL_MINUTES)
    log.info("Press Ctrl+C to stop.\n")

    # Run once immediately (useful for testing outside the window too)
    run_scan()

    # Schedule repeated scans inside the 7–8 PM window
    schedule.every(SCAN_INTERVAL_MINUTES).minutes.do(run_scan)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
