"""
Simple web scraper for quotes.toscrape.com
Scrapes quotes, authors, and tags across multiple pages.
"""

import requests
from bs4 import BeautifulSoup


BASE_URL = "http://quotes.toscrape.com"


def fetch_page(url):
    """Fetch HTML content from a URL. Returns BeautifulSoup object or None on failure."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_quotes(soup):
    """Extract quotes from a parsed page. Returns a list of dicts."""
    quotes = []
    for item in soup.select("div.quote"):
        text = item.select_one("span.text").get_text(strip=True)
        author = item.select_one("small.author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in item.select("a.tag")]
        quotes.append({"text": text, "author": author, "tags": tags})
    return quotes


def get_next_page(soup):
    """Return the URL for the next page, or None if there is none."""
    next_btn = soup.select_one("li.next a")
    if next_btn:
        return BASE_URL + next_btn["href"]
    return None


def scrape(max_pages=3):
    """
    Scrape quotes from the site, up to max_pages pages.
    Returns a list of quote dicts.
    """
    all_quotes = []
    url = BASE_URL
    page = 1

    while url and page <= max_pages:
        print(f"Scraping page {page}: {url}")
        soup = fetch_page(url)
        if not soup:
            break
        quotes = parse_quotes(soup)
        all_quotes.extend(quotes)
        url = get_next_page(soup)
        page += 1

    return all_quotes


def display(quotes):
    """Print scraped quotes to the console."""
    for i, q in enumerate(quotes, 1):
        print(f"\n[{i}] {q['text']}")
        print(f"    — {q['author']}")
        print(f"    Tags: {', '.join(q['tags']) if q['tags'] else 'none'}")


if __name__ == "__main__":
    print("Starting scraper...\n")
    results = scrape(max_pages=3)
    print(f"\n{'='*50}")
    print(f"Scraped {len(results)} quotes total")
    print(f"{'='*50}")
    display(results)
