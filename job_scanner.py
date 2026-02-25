"""
Job Scan Automation Script
--------------------------
Searches for jobs via RSS feeds (Indeed) and saves new results daily.
Runs automatically every morning at 7 AM.

Setup:
    pip install schedule requests beautifulsoup4 lxml

Optional email alerts:
    Fill in the EMAIL CONFIG section below.
"""

import csv
import json
import logging
import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import schedule
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# CONFIG — edit these values before running
# ---------------------------------------------------------------------------

JOB_SEARCHES = [
    {"keywords": "Python Developer", "location": "Remote"},
    {"keywords": "Data Engineer",    "location": "New York"},
]

# Results are saved here (CSV + JSON)
OUTPUT_DIR = "job_results"

# How many days back to consider a job "new" (avoids re-alerting old posts)
MAX_AGE_DAYS = 1

# --- Email alerts (optional) -----------------------------------------------
EMAIL_ENABLED = False          # Set True to receive email summaries
EMAIL_SENDER  = "you@gmail.com"
EMAIL_PASSWORD = ""            # Use an App Password, NOT your real password
EMAIL_RECIPIENT = "you@gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
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


def build_indeed_rss_url(keywords: str, location: str) -> str:
    """Return an Indeed RSS feed URL for the given query."""
    base = "https://www.indeed.com/rss"
    params = (
        f"?q={requests.utils.quote(keywords)}"
        f"&l={requests.utils.quote(location)}"
        f"&sort=date"
    )
    return base + params


def fetch_rss(url: str, timeout: int = 15) -> BeautifulSoup | None:
    """Fetch and parse an RSS feed. Returns None on failure."""
    headers = {"User-Agent": "Mozilla/5.0 (job-scanner-bot/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml-xml")
    except requests.RequestException as exc:
        log.warning("Failed to fetch %s — %s", url, exc)
        return None


def parse_jobs(soup: BeautifulSoup, source: str) -> list[dict]:
    """Extract job listings from a parsed RSS feed."""
    jobs = []
    for item in soup.find_all("item"):
        title   = (item.find("title")   or {}).get_text(strip=True)
        link    = (item.find("link")    or {}).get_text(strip=True)
        company = (item.find("source")  or {}).get_text(strip=True)
        pub_date = (item.find("pubDate") or {}).get_text(strip=True)
        snippet  = BeautifulSoup(
            (item.find("description") or {}).get_text(), "html.parser"
        ).get_text(strip=True)[:300]

        jobs.append({
            "title":    title,
            "company":  company,
            "link":     link,
            "pub_date": pub_date,
            "snippet":  snippet,
            "source":   source,
            "fetched":  datetime.now().isoformat(timespec="seconds"),
        })
    return jobs


def load_seen_links(filepath: str) -> set[str]:
    """Load previously seen job links from a JSON file."""
    if os.path.exists(filepath):
        with open(filepath) as f:
            return set(json.load(f))
    return set()


def save_seen_links(filepath: str, links: set[str]) -> None:
    with open(filepath, "w") as f:
        json.dump(sorted(links), f, indent=2)


def save_to_csv(jobs: list[dict], filepath: str) -> None:
    """Append jobs to a CSV, writing the header only once."""
    fieldnames = ["title", "company", "link", "pub_date", "snippet", "source", "fetched"]
    write_header = not os.path.exists(filepath)
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(jobs)


def send_email(subject: str, body: str) -> None:
    """Send a plain-text email summary."""
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


def format_email_body(new_jobs: list[dict]) -> str:
    lines = [f"Job Scan — {datetime.now().strftime('%Y-%m-%d')}\n"]
    for job in new_jobs:
        lines += [
            f"  {job['title']}",
            f"  {job['company']}",
            f"  {job['link']}",
            f"  Posted: {job['pub_date']}",
            "",
        ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core scan logic
# ---------------------------------------------------------------------------

def run_scan() -> None:
    log.info("=== Job scan started ===")
    ensure_output_dir()

    today        = datetime.now().strftime("%Y-%m-%d")
    csv_path     = os.path.join(OUTPUT_DIR, f"jobs_{today}.csv")
    seen_path    = os.path.join(OUTPUT_DIR, "seen_links.json")

    seen_links   = load_seen_links(seen_path)
    all_new_jobs: list[dict] = []

    for search in JOB_SEARCHES:
        keywords = search["keywords"]
        location = search["location"]
        label    = f"{keywords} / {location}"

        log.info("Searching: %s", label)
        url  = build_indeed_rss_url(keywords, location)
        soup = fetch_rss(url)

        if soup is None:
            log.warning("Skipping %s — could not fetch feed.", label)
            continue

        jobs     = parse_jobs(soup, source=label)
        new_jobs = [j for j in jobs if j["link"] not in seen_links]

        if new_jobs:
            log.info("  Found %d new listing(s)", len(new_jobs))
            save_to_csv(new_jobs, csv_path)
            seen_links.update(j["link"] for j in new_jobs)
            all_new_jobs.extend(new_jobs)
        else:
            log.info("  No new listings.")

    save_seen_links(seen_path, seen_links)

    total = len(all_new_jobs)
    log.info("=== Scan complete — %d new job(s) saved to %s ===", total, csv_path)

    if EMAIL_ENABLED and total > 0:
        subject = f"Job Scan: {total} new listing(s) — {today}"
        send_email(subject, format_email_body(all_new_jobs))


# ---------------------------------------------------------------------------
# Scheduler entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("Job scanner starting. Will run every day at 07:00.")
    log.info("Press Ctrl+C to stop.\n")

    # Run immediately on startup so you can verify it works
    run_scan()

    # Schedule the daily 7 AM run
    schedule.every().day.at("07:00").do(run_scan)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
