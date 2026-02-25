"""
Report Generator
Takes raw scan data and produces a clean, readable daily report.
Saves as both JSON (for data) and Markdown (for reading).
"""

import json
import os
from datetime import datetime
from pathlib import Path

from config import REPORTS_DIR


def _sentiment_emoji(label: str) -> str:
    return {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(label, "⚪")


def generate_report(tiktok_data: dict, reddit_data: dict) -> dict:
    """Combine TikTok and Reddit data into a single report object."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "tiktok": tiktok_data,
        "reddit": reddit_data,
        "summary": _build_summary(tiktok_data, reddit_data),
    }
    return report


def _build_summary(tiktok: dict, reddit: dict) -> dict:
    """Plain-English summary of what the scanners found."""
    summary = {}

    # TikTok summary
    top_tags = [t["tag"] for t in tiktok.get("trending_hashtags", [])[:5]]
    top_themes = [t["theme"] for t in tiktok.get("top_themes", [])[:5]]
    summary["tiktok"] = {
        "status": "ok" if not tiktok.get("error") else "error",
        "top_hashtags": top_tags,
        "top_themes": top_themes,
        "note": tiktok.get("error") or f"{len(top_tags)} trending hashtags captured",
    }

    # Reddit summary
    overall = reddit.get("overall_sentiment", {})
    top_keywords = [k["keyword"] for k in reddit.get("top_keywords", [])[:5]]
    summary["reddit"] = {
        "status": "ok" if not reddit.get("error") else "error",
        "economy_mood": overall.get("label", "unknown"),
        "average_sentiment_score": overall.get("average_compound", 0),
        "posts_scanned": reddit.get("total_posts_scanned", 0),
        "top_concerns": top_keywords,
        "note": reddit.get("error") or (
            f"Economy mood is {overall.get('label', 'unknown').upper()} "
            f"(score: {overall.get('average_compound', 0)})"
        ),
    }

    return summary


def save_report(report: dict) -> tuple[str, str]:
    """Save report as JSON and Markdown. Returns (json_path, md_path)."""
    Path(REPORTS_DIR).mkdir(exist_ok=True)
    date_str = report["date"]

    json_path = os.path.join(REPORTS_DIR, f"{date_str}.json")
    md_path = os.path.join(REPORTS_DIR, f"{date_str}.md")

    # Save raw JSON
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    # Save readable Markdown
    with open(md_path, "w") as f:
        f.write(_render_markdown(report))

    return json_path, md_path


def _render_markdown(report: dict) -> str:
    lines = []
    date = report["date"]
    generated = report["generated_at"]
    summary = report.get("summary", {})
    tiktok = report.get("tiktok", {})
    reddit = report.get("reddit", {})

    lines.append(f"# Daily Trend & Economy Report — {date}")
    lines.append(f"*Generated: {generated}*\n")

    # --- Executive Summary ---
    lines.append("## Executive Summary\n")

    tsum = summary.get("tiktok", {})
    rsum = summary.get("reddit", {})

    if tsum.get("top_hashtags"):
        lines.append(
            f"**TikTok:** Top trending tags today — "
            f"{', '.join(tsum['top_hashtags'])}"
        )
    else:
        lines.append(f"**TikTok:** {tsum.get('note', 'No data')}")

    mood = rsum.get("economy_mood", "unknown")
    score = rsum.get("average_sentiment_score", 0)
    emoji = _sentiment_emoji(mood)
    lines.append(
        f"**Reddit Economy Mood:** {emoji} {mood.upper()} (score: {score})"
    )
    if rsum.get("top_concerns"):
        lines.append(
            f"**Top concerns on Reddit:** {', '.join(rsum['top_concerns'])}"
        )
    lines.append("")

    # --- TikTok Section ---
    lines.append("---\n## TikTok Trends\n")

    if tiktok.get("error"):
        lines.append(f"> ⚠️ {tiktok['error']}\n")
    else:
        lines.append("### Trending Hashtags")
        for item in tiktok.get("trending_hashtags", [])[:10]:
            lines.append(f"- `{item['tag']}` — appeared in {item['appearances']} videos")

        lines.append("\n### Trending Sounds")
        for item in tiktok.get("trending_sounds", [])[:5]:
            lines.append(f"- *{item['sound']}* ({item['uses']} videos)")

        lines.append("\n### Top Themes (from video descriptions)")
        themes = [t["theme"] for t in tiktok.get("top_themes", [])[:15]]
        lines.append(", ".join(themes) if themes else "None captured")

        lines.append("\n### Top Videos by Play Count")
        for i, vid in enumerate(tiktok.get("top_videos", [])[:5], 1):
            lines.append(
                f"{i}. **@{vid['author']}** — {vid['description'][:80]}...  \n"
                f"   {vid['plays']:,} plays | {vid['likes']:,} likes | "
                f"{vid['shares']:,} shares"
            )

    lines.append("")

    # --- Reddit Section ---
    lines.append("---\n## Reddit: How the Economy is Really Doing\n")

    if reddit.get("error"):
        lines.append(f"> ⚠️ {reddit['error']}\n")
    else:
        overall = reddit.get("overall_sentiment", {})
        mood_label = overall.get("label", "unknown")
        lines.append(
            f"**Overall Mood:** {_sentiment_emoji(mood_label)} {mood_label.upper()}  \n"
            f"Posts scanned: {reddit.get('total_posts_scanned', 0)} across "
            f"{len(reddit.get('sentiment_by_subreddit', {}))} subreddits  \n"
            f"Positive: {overall.get('positive_posts', 0)} | "
            f"Negative: {overall.get('negative_posts', 0)} | "
            f"Neutral: {overall.get('neutral_posts', 0)}\n"
        )

        lines.append("### Mood by Subreddit")
        for sub, data in sorted(
            reddit.get("sentiment_by_subreddit", {}).items(),
            key=lambda x: x[1]["average_compound"],
        ):
            emoji = _sentiment_emoji(data["label"])
            lines.append(
                f"- **r/{sub}** {emoji} {data['label']} "
                f"(score: {data['average_compound']}, {data['posts_scanned']} posts)"
            )

        lines.append("\n### What People Are Talking About")
        for item in reddit.get("top_keywords", []):
            lines.append(
                f"- **{item['keyword']}** — mentioned in {item['mentions']} posts"
            )

        if reddit.get("pain_points"):
            lines.append("\n### Pain Points (High-Engagement Negative Posts)")
            for post in reddit["pain_points"]:
                lines.append(
                    f"- [{post['title']}]({post['url']})  \n"
                    f"  r/{post['subreddit']} | {post['score']:,} upvotes | "
                    f"{post['comments']} comments"
                )

        if reddit.get("green_shoots"):
            lines.append("\n### Green Shoots (High-Engagement Positive Posts)")
            for post in reddit["green_shoots"]:
                lines.append(
                    f"- [{post['title']}]({post['url']})  \n"
                    f"  r/{post['subreddit']} | {post['score']:,} upvotes | "
                    f"{post['comments']} comments"
                )

    lines.append("\n---\n*End of report*")
    return "\n".join(lines)


def print_summary(report: dict) -> None:
    """Print a quick console summary after a scan."""
    summary = report.get("summary", {})
    tsum = summary.get("tiktok", {})
    rsum = summary.get("reddit", {})

    print("\n" + "=" * 60)
    print(f"  SCAN COMPLETE — {report['date']}")
    print("=" * 60)
    print(f"\n[TIKTOK]  {tsum.get('note', 'No data')}")
    if tsum.get("top_hashtags"):
        print(f"  Tags: {', '.join(tsum['top_hashtags'])}")

    print(f"\n[REDDIT]  {rsum.get('note', 'No data')}")
    if rsum.get("top_concerns"):
        print(f"  Top concerns: {', '.join(rsum['top_concerns'])}")

    print("=" * 60 + "\n")
