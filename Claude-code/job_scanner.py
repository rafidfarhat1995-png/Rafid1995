"""
Job Scanner Automation - Built with Claude Code
Rafid's Daily Job Hunting Assistant

What this does:
- Searches for jobs automatically every morning
- Tracks what you've already seen (no duplicates)
- Saves everything to Excel
- Prints a clean daily report in your terminal
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os

# ============================================
# CUSTOMIZE THIS SECTION - YOUR PREFERENCES
# ============================================

JOB_KEYWORDS = [
    "banking",
    "finance",
    "financial analyst",
    "compliance officer",
    "risk analyst",
    "data analyst finance",
]

LOCATION = "Canada"  # Change to your city

SEEN_JOBS_FILE = "seen_jobs.json"
OUTPUT_FILE = "jobs_found.xlsx"

# ============================================
# THE ENGINE - DON'T NEED TO TOUCH THIS
# ============================================

def load_seen_jobs():
    """Load jobs we've already seen so no duplicates"""
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen_jobs(seen):
    """Remember what we've already shown you"""
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(seen, f)

def search_jobs(keyword, location):
    """Search for jobs and return results"""
    jobs = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    # Format search URL
    query = keyword.replace(" ", "+")
    loc = location.replace(" ", "+")
    url = f"https://www.indeed.com/jobs?q={query}&l={loc}&sort=date&fromage=1"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find job cards
        job_cards = soup.find_all("div", class_="job_seen_beacon")

        for card in job_cards:
            try:
                title = card.find("h2", class_="jobTitle").get_text(strip=True)
                company = card.find("span", {"data-testid": "company-name"}).get_text(strip=True)
                location_tag = card.find("div", {"data-testid": "text-location"})
                job_location = location_tag.get_text(strip=True) if location_tag else location

                link_tag = card.find("a", class_="jcs-JobTitle")
                job_id = link_tag["id"] if link_tag and "id" in link_tag.attrs else title
                job_link = f"https://indeed.com{link_tag['href']}" if link_tag else "N/A"

                jobs.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "keyword": keyword,
                    "link": job_link,
                    "date_found": datetime.now().strftime("%Y-%m-%d"),
                    "applied": "No",
                    "follow_up": "No"
                })
            except Exception:
                continue

    except Exception as e:
        print(f"  Could not fetch results for '{keyword}': {e}")

    return jobs

def run_daily_scan():
    """Main function - runs the full scan"""

    print("=" * 50)
    print("   RAFID'S DAILY JOB SCANNER")
    print(f"   {datetime.now().strftime('%B %d, %Y - %I:%M %p')}")
    print("=" * 50)

    seen_jobs = load_seen_jobs()
    all_new_jobs = []

    print(f"\nScanning {len(JOB_KEYWORDS)} job categories in {LOCATION}...\n")

    for keyword in JOB_KEYWORDS:
        print(f"  Searching: {keyword}...")
        jobs = search_jobs(keyword, LOCATION)

        # Filter out duplicates
        new_jobs = [j for j in jobs if j["id"] not in seen_jobs]
        all_new_jobs.extend(new_jobs)

        # Mark as seen
        seen_jobs.extend([j["id"] for j in new_jobs])

        print(f"  Found {len(new_jobs)} new jobs")

    # Save updated seen list
    save_seen_jobs(seen_jobs)

    # Save to Excel
    if all_new_jobs:
        df = pd.DataFrame(all_new_jobs)

        # If file exists, append. Otherwise create new.
        if os.path.exists(OUTPUT_FILE):
            existing = pd.read_excel(OUTPUT_FILE)
            df = pd.concat([existing, df], ignore_index=True)

        df.to_excel(OUTPUT_FILE, index=False)

        print("\n" + "=" * 50)
        print(f"  SCAN COMPLETE")
        print(f"  New jobs found today: {len(all_new_jobs)}")
        print(f"  Saved to: {OUTPUT_FILE}")
        print("=" * 50)

        print("\n TOP NEW JOBS TODAY:")
        print("-" * 50)
        for job in all_new_jobs[:10]:
            print(f"\n  Role:    {job['title']}")
            print(f"  Company: {job['company']}")
            print(f"  Where:   {job['location']}")
            print(f"  Link:    {job['link']}")

        if len(all_new_jobs) > 10:
            print(f"\n  ... and {len(all_new_jobs) - 10} more in your Excel file")
    else:
        print("\n  No new jobs found today. Check back tomorrow.")

    print("\n Good luck Rafid. You got this.\n")

# ============================================
# RUN IT
# ============================================

if __name__ == "__main__":
    run_daily_scan()
