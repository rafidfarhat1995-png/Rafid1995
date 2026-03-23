import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import textwrap

RSS_URL = "https://www150.statcan.gc.ca/rss/daily-quotidien/rss-eng.xml"

def fetch_feed(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.read()

def parse_date(date_str):
    # RSS dates look like: "Mon, 23 Mar 2026 08:30:00 -0400"
    try:
        return datetime.strptime(date_str.strip(), "%a, %d %b %Y %H:%M:%S %z")
    except ValueError:
        return None

def main():
    today = datetime.now(timezone.utc).date()

    print(f"\n{'='*60}")
    print(f"  Statistics Canada Releases — {today.strftime('%B %d, %Y')}")
    print(f"{'='*60}\n")

    try:
        raw = fetch_feed(RSS_URL)
    except Exception as e:
        print(f"Error fetching feed: {e}")
        return

    root = ET.fromstring(raw)
    ns = {"media": "http://search.yahoo.com/mrss/"}

    items = root.findall(".//item")
    todays_items = []

    for item in items:
        pub_date_el = item.find("pubDate")
        if pub_date_el is None:
            continue
        pub_date = parse_date(pub_date_el.text)
        if pub_date and pub_date.date() == today:
            title = item.findtext("title", "No title").strip()
            description = item.findtext("description", "").strip()
            link = item.findtext("link", "").strip()
            todays_items.append((title, description, link))

    if not todays_items:
        print("No releases found for today yet.")
        print("Stats Canada typically publishes releases at 8:30 AM Eastern time.")
    else:
        print(f"Found {len(todays_items)} release(s):\n")
        for i, (title, description, link) in enumerate(todays_items, 1):
            print(f"[{i}] {title}")
            print(f"    URL: {link}")
            if description:
                # Clean up HTML tags simply
                import re
                clean = re.sub(r"<[^>]+>", "", description).strip()
                wrapped = textwrap.fill(clean, width=70, initial_indent="    ", subsequent_indent="    ")
                print(f"\n    Summary:\n{wrapped}")
            print()

    print(f"{'='*60}")
    print("Source: Statistics Canada — The Daily")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
