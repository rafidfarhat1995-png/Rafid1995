"""
Stats Canada Daily Summary
Fetches today's Statistics Canada releases and uses Claude to summarize them.
"""

import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timezone
import anthropic

RSS_URL = "https://www150.statcan.gc.ca/rss/daily-quotidien/rss-eng.xml"


def fetch_feed(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.read()


def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%a, %d %b %Y %H:%M:%S %z")
    except ValueError:
        return None


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()


def get_todays_releases():
    today = datetime.now(timezone.utc).date()
    raw = fetch_feed(RSS_URL)
    root = ET.fromstring(raw)
    items = root.findall(".//item")
    releases = []

    for item in items:
        pub_date_el = item.find("pubDate")
        if pub_date_el is None:
            continue
        pub_date = parse_date(pub_date_el.text)
        if pub_date and pub_date.date() == today:
            releases.append({
                "title": item.findtext("title", "").strip(),
                "description": strip_html(item.findtext("description", "")),
                "link": item.findtext("link", "").strip(),
            })

    return releases, today


def summarize_with_claude(releases, today):
    client = anthropic.Anthropic()

    # Build the content to summarize
    releases_text = "\n\n".join(
        f"Release {i+1}: {r['title']}\n{r['description']}"
        for i, r in enumerate(releases)
    )

    prompt = f"""Today is {today.strftime('%A, %B %d, %Y')}.

Statistics Canada published the following {len(releases)} release(s) today:

{releases_text}

Please provide a clear, plain-English summary of what Statistics Canada released today.
For each release, briefly explain:
- What data it covers
- The key finding or headline number (if available)
- Why it matters to Canadians

Keep it conversational and accessible — as if explaining to someone who doesn't follow economic data."""

    print(f"\n{'='*60}")
    print(f"  Statistics Canada Summary — {today.strftime('%B %d, %Y')}")
    print(f"{'='*60}\n")
    print(f"Found {len(releases)} release(s). Generating summary...\n")
    print("-" * 60)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print(f"\n{'-'*60}")
    print("\nSources:")
    for i, r in enumerate(releases, 1):
        print(f"  [{i}] {r['title']}")
        print(f"      {r['link']}")
    print(f"\n{'='*60}\n")


def main():
    try:
        releases, today = get_todays_releases()
    except Exception as e:
        print(f"Error fetching Stats Canada feed: {e}")
        return

    if not releases:
        print(f"\nNo Stats Canada releases found for today ({today}).")
        print("Releases are typically published at 8:30 AM Eastern time.")
        return

    summarize_with_claude(releases, today)


if __name__ == "__main__":
    main()
