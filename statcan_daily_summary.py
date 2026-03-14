#!/usr/bin/env python3
"""
Statistics Canada - Daily Release Summary
Fetches and summarizes data releases published in The Daily using the
Statistics Canada Web Data Service (WDS) API and RSS feed.

API docs: https://www.statcan.gc.ca/en/developers/wds/user-guide
The Daily: https://www150.statcan.gc.ca/n1/dai-quo/index-eng.htm

Usage:
    python statcan_daily_summary.py              # today's releases
    python statcan_daily_summary.py --date 2025-03-10  # specific date
    python statcan_daily_summary.py --limit 10   # cap number of tables shown
"""

import argparse
import sys
import textwrap
import xml.etree.ElementTree as ET
from datetime import date, datetime

try:
    import requests
except ImportError:
    print("Missing dependency: install with  pip install requests")
    sys.exit(1)

WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"
DAILY_RSS = "https://www150.statcan.gc.ca/n1/pub/71-607-x/71-607-x2018009-eng.xml"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "StatCanDailySummary/1.0 (python)"})


# ── Helpers ──────────────────────────────────────────────────────────────────

def wds_get(path: str) -> dict | list | None:
    """Call a WDS endpoint and return the parsed JSON, or None on error."""
    url = f"{WDS_BASE}/{path}"
    try:
        resp = SESSION.get(url, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        print(f"  [warn] WDS request failed ({url}): {exc}")
        return None


def get_changed_cubes(release_date: str) -> list[dict]:
    """Return the list of tables released on release_date (YYYY-MM-DD)."""
    data = wds_get(f"getChangedCubeList/{release_date}")
    if not data:
        return []
    # API returns either a list directly or {"status": ..., "object": [...]}
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and data.get("status") == "SUCCESS":
        return data.get("object") or []
    return []


def get_cube_metadata(pid: int) -> dict | None:
    """Fetch metadata for a single table (Product ID)."""
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


def fetch_rss_items() -> list[dict]:
    """
    Fetch The Daily RSS feed and return a list of
    {title, link, pubDate, description} dicts.
    """
    try:
        resp = SESSION.get(DAILY_RSS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [warn] RSS fetch failed: {exc}")
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        print(f"  [warn] RSS parse failed: {exc}")
        return []

    items = []
    ns = {"atom": "http://www.w3.org/2005/Atom"}  # in case of Atom feed
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        desc = (item.findtext("description") or "").strip()
        # Strip basic HTML tags from description
        import re
        desc = re.sub(r"<[^>]+>", " ", desc)
        desc = re.sub(r"\s+", " ", desc).strip()
        items.append({"title": title, "link": link, "pubDate": pub_date, "description": desc})
    return items


def filter_rss_by_date(items: list[dict], target_date: date) -> list[dict]:
    """Keep only RSS items whose pubDate matches target_date."""
    matching = []
    for item in items:
        raw = item.get("pubDate", "")
        for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
            try:
                dt = datetime.strptime(raw, fmt)
                if dt.date() == target_date:
                    matching.append(item)
                break
            except ValueError:
                continue
    return matching


# ── Formatting ────────────────────────────────────────────────────────────────

def wrap(text: str, indent: int = 4, width: int = 88) -> str:
    prefix = " " * indent
    return textwrap.fill(text, width=width, initial_indent=prefix, subsequent_indent=prefix)


def print_section(title: str) -> None:
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}")


def print_rss_summary(items: list[dict]) -> None:
    print_section(f"The Daily — News Releases ({len(items)} item(s))")
    if not items:
        print("  No RSS items found for this date.")
        return
    for i, item in enumerate(items, 1):
        print(f"\n  [{i}] {item['title']}")
        if item["pubDate"]:
            print(f"      Published : {item['pubDate']}")
        if item["link"]:
            print(f"      URL       : {item['link']}")
        if item["description"]:
            print(wrap(item["description"][:400] + ("…" if len(item["description"]) > 400 else "")))


def print_table_summary(cubes: list[dict], metadata_map: dict) -> None:
    print_section(f"Data Table Releases ({len(cubes)} table(s))")
    if not cubes:
        print("  No table releases found for this date.")
        return

    for cube in cubes:
        pid = cube.get("productId") or cube.get("pid")
        freq = cube.get("frequencyCode") or ""
        release_time = cube.get("releaseTime") or cube.get("releaseDate") or ""

        meta = metadata_map.get(pid)
        if meta:
            title_en = meta.get("cubeTitleEn") or meta.get("cubeTitleFr") or f"Table {pid}"
            note = meta.get("cubeNotes") or ""
        else:
            title_en = f"Table {pid}"
            note = ""

        print(f"\n  • {title_en}")
        print(f"    PID       : {pid}")
        if release_time:
            print(f"    Released  : {release_time}")
        if freq:
            freq_labels = {"1": "daily", "2": "weekly", "6": "monthly",
                           "7": "bimonthly", "9": "quarterly", "10": "semi-annual",
                           "12": "annual", "13": "occasional"}
            print(f"    Frequency : {freq_labels.get(str(freq), freq)}")
        if note:
            print(wrap(note[:300] + ("…" if len(note) > 300 else "")))
        print(f"    Link      : https://www150.statcan.gc.ca/t1/tbl1/en/dtbl/{pid:08d}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Statistics Canada daily release summary")
    parser.add_argument("--date", default=str(date.today()),
                        help="Release date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--limit", type=int, default=25,
                        help="Max number of data tables to display (default: 25)")
    parser.add_argument("--no-rss", action="store_true",
                        help="Skip The Daily RSS feed section")
    parser.add_argument("--no-tables", action="store_true",
                        help="Skip the data tables section")
    args = parser.parse_args()

    try:
        target_date = date.fromisoformat(args.date)
    except ValueError:
        print(f"Invalid date format: {args.date}  (expected YYYY-MM-DD)")
        sys.exit(1)

    print(f"\n{'─' * 70}")
    print(f"  Statistics Canada — Daily Release Summary")
    print(f"  Date: {target_date.strftime('%A, %B %d, %Y')}")
    print(f"{'─' * 70}")

    # ── RSS / news releases ────────────────────────────────────────────────
    if not args.no_rss:
        print("\nFetching The Daily RSS feed…")
        rss_items = fetch_rss_items()
        rss_today = filter_rss_by_date(rss_items, target_date)
        # If no items match the exact date, show the most recent ones instead
        if not rss_today and rss_items:
            rss_today = rss_items[:5]
            print(f"  (No RSS items for {target_date}; showing {len(rss_today)} most recent)")
        print_rss_summary(rss_today)

    # ── WDS data table releases ────────────────────────────────────────────
    if not args.no_tables:
        print("\nFetching changed table list from WDS API…")
        cubes = get_changed_cubes(args.date)

        if cubes:
            limited = cubes[: args.limit]
            print(f"  Found {len(cubes)} table(s) released; showing first {len(limited)}.")

            print("\nFetching table metadata…")
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
    print("  Source : Statistics Canada Web Data Service")
    print("  URL    : https://www.statcan.gc.ca/en/developers/wds")
    print(f"{'─' * 70}\n")


if __name__ == "__main__":
    main()
