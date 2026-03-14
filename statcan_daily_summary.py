#!/usr/bin/env python3
"""
Statistics Canada - Daily Release Summary
Fetches and summarizes data releases published in The Daily using the
Statistics Canada Web Data Service (WDS) API and The Daily web page.

API docs: https://www.statcan.gc.ca/en/developers/wds/user-guide
The Daily: https://www150.statcan.gc.ca/n1/dai-quo/index-eng.htm

Usage:
    python3 statcan_daily_summary.py              # most recent business day
    python3 statcan_daily_summary.py --date 2025-03-10  # specific date
    python3 statcan_daily_summary.py --limit 10   # cap number of tables shown
"""

import argparse
import html as html_module
import re
import sys
import textwrap
from datetime import date, timedelta
from html.parser import HTMLParser

try:
    import requests
except ImportError:
    print("Missing dependency: install with  pip3 install requests")
    sys.exit(1)

WDS_BASE  = "https://www150.statcan.gc.ca/t1/wds/rest"
DAILY_URL = "https://www150.statcan.gc.ca/n1/dai-quo/index-eng.htm"
SESSION   = requests.Session()
SESSION.headers.update({"User-Agent": "StatCanDailySummary/1.0 (python)"})


# ── Date helpers ──────────────────────────────────────────────────────────────

def last_business_day(d: date) -> date:
    """Return d if it is a weekday, otherwise step back to Friday."""
    while d.weekday() >= 5:   # 5 = Saturday, 6 = Sunday
        d -= timedelta(days=1)
    return d


# ── WDS API ───────────────────────────────────────────────────────────────────

def wds_get(path: str) -> dict | list | None:
    url = f"{WDS_BASE}/{path}"
    try:
        resp = SESSION.get(url, timeout=20)
        if resp.status_code == 409:
            return None   # no data for this date (weekend / holiday / too early)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        print(f"  [warn] WDS request failed: {exc}")
        return None


def get_changed_cubes(release_date: str) -> list[dict]:
    data = wds_get(f"getChangedCubeList/{release_date}")
    if not data:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and data.get("status") == "SUCCESS":
        return data.get("object") or []
    return []


def get_cube_metadata(pid: int) -> dict | None:
    data = wds_get(f"getCubeMetadata/{pid}")
    if not data:
        return None
    if isinstance(data, list) and data:
        obj = data[0]
        if obj.get("status") == "SUCCESS":
            return obj.get("object")
    if isinstance(data, dict) and data.get("status") == "SUCCESS":
        return data.get("object")
    return None


# ── The Daily page scraper ────────────────────────────────────────────────────

class _DailyParser(HTMLParser):
    """Minimal parser that extracts article links from The Daily index page."""

    def __init__(self):
        super().__init__()
        self._in_main  = False
        self._in_link  = False
        self._cur_href = ""
        self._cur_text = []
        self.articles  = []   # list of {title, url}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "main" or attrs.get("id") in ("wb-cont", "main-content"):
            self._in_main = True
        if self._in_main and tag == "a" and "href" in attrs:
            href = attrs["href"]
            # Keep only links that look like Daily article pages
            if re.search(r"dq\d{6}", href) or "daily-quotidien" in href:
                self._in_link  = True
                self._cur_href = href
                self._cur_text = []

    def handle_endtag(self, tag):
        if self._in_link and tag == "a":
            title = html_module.unescape(" ".join(self._cur_text).strip())
            if title:
                url = self._cur_href
                if not url.startswith("http"):
                    url = "https://www150.statcan.gc.ca" + url
                self.articles.append({"title": title, "url": url})
            self._in_link  = False
            self._cur_href = ""
            self._cur_text = []

    def handle_data(self, data):
        if self._in_link:
            self._cur_text.append(data.strip())


def fetch_daily_articles() -> list[dict]:
    """Scrape today's article list from The Daily index page."""
    try:
        resp = SESSION.get(DAILY_URL, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [warn] Could not fetch The Daily page: {exc}")
        return []

    parser = _DailyParser()
    parser.feed(resp.text)
    # De-duplicate by URL
    seen, unique = set(), []
    for a in parser.articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)
    return unique


# ── Formatting ────────────────────────────────────────────────────────────────

def wrap(text: str, indent: int = 4, width: int = 88) -> str:
    prefix = " " * indent
    return textwrap.fill(text, width=width, initial_indent=prefix,
                         subsequent_indent=prefix)


def print_section(title: str) -> None:
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}")


def print_articles(articles: list[dict]) -> None:
    print_section(f"The Daily — News Releases ({len(articles)} item(s))")
    if not articles:
        print("  Nothing found on The Daily page.")
        return
    for i, a in enumerate(articles, 1):
        print(f"\n  [{i}] {a['title']}")
        print(f"      {a['url']}")


def print_table_summary(cubes: list[dict], metadata_map: dict) -> None:
    print_section(f"Data Table Releases ({len(cubes)} table(s))")
    if not cubes:
        print("  No table releases found for this date.")
        return

    freq_labels = {"1": "daily", "2": "weekly", "6": "monthly",
                   "7": "bimonthly", "9": "quarterly", "10": "semi-annual",
                   "12": "annual", "13": "occasional"}

    for cube in cubes:
        pid          = cube.get("productId") or cube.get("pid")
        freq         = str(cube.get("frequencyCode") or "")
        release_time = cube.get("releaseTime") or cube.get("releaseDate") or ""
        meta         = metadata_map.get(pid)

        if meta:
            title_en = meta.get("cubeTitleEn") or meta.get("cubeTitleFr") or f"Table {pid}"
            note     = meta.get("cubeNotes") or ""
        else:
            title_en = f"Table {pid}"
            note     = ""

        print(f"\n  • {title_en}")
        print(f"    PID       : {pid}")
        if release_time:
            print(f"    Released  : {release_time}")
        if freq:
            print(f"    Frequency : {freq_labels.get(freq, freq)}")
        if note:
            print(wrap(note[:300] + ("…" if len(note) > 300 else "")))
        print(f"    Link      : https://www150.statcan.gc.ca/t1/tbl1/en/dtbl/{pid:08d}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Statistics Canada daily release summary")
    parser.add_argument(
        "--date", default=None,
        help="Release date YYYY-MM-DD (default: most recent business day)")
    parser.add_argument(
        "--limit", type=int, default=25,
        help="Max data tables to show (default: 25)")
    parser.add_argument("--no-news",   action="store_true",
                        help="Skip The Daily news articles section")
    parser.add_argument("--no-tables", action="store_true",
                        help="Skip the data tables section")
    args = parser.parse_args()

    # Resolve date — default to most recent business day
    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            print(f"Invalid date: {args.date}  (expected YYYY-MM-DD)")
            sys.exit(1)
    else:
        target_date = last_business_day(date.today())

    print(f"\n{'─' * 70}")
    print(f"  Statistics Canada — Daily Release Summary")
    print(f"  Date : {target_date.strftime('%A, %B %d, %Y')}")
    if target_date != date.today():
        print(f"  Note : Showing most recent business day (Stats Canada is")
        print(f"         closed on weekends and holidays).")
    print(f"{'─' * 70}")

    # ── The Daily news articles ────────────────────────────────────────────
    if not args.no_news:
        print("\nFetching The Daily news articles…")
        articles = fetch_daily_articles()
        print_articles(articles)

    # ── WDS data table releases ────────────────────────────────────────────
    if not args.no_tables:
        date_str = str(target_date)
        print(f"\nFetching data table releases for {date_str}…")
        cubes = get_changed_cubes(date_str)

        # If still nothing (e.g. holiday), walk back up to 7 days
        walked = 0
        check  = target_date
        while not cubes and walked < 7:
            check  -= timedelta(days=1)
            check   = last_business_day(check)
            walked += 1
            print(f"  No releases found — trying {check}…")
            cubes = get_changed_cubes(str(check))
        if cubes and walked:
            print(f"  Using releases from {check}.")
            target_date = check

        if cubes:
            limited = cubes[: args.limit]
            print(f"  Found {len(cubes)} table(s); showing first {len(limited)}.")
            print("  Fetching metadata…")
            metadata_map: dict[int, dict] = {}
            for cube in limited:
                pid = cube.get("productId") or cube.get("pid")
                if pid:
                    meta = get_cube_metadata(int(pid))
                    if meta:
                        metadata_map[int(pid)] = meta
            print_table_summary(limited, metadata_map)
        else:
            print_table_summary([], {})

    print(f"\n{'─' * 70}")
    print("  Source : Statistics Canada — The Daily &  WDS API")
    print("  URL    : https://www150.statcan.gc.ca/n1/dai-quo/index-eng.htm")
    print(f"{'─' * 70}\n")


if __name__ == "__main__":
    main()
