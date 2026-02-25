"""
Trend Scanner - Reddit & TikTok
Rafid's Mac Mini Market Research Tool

What this does:
- Scans Reddit for trending Mac Mini posts (upvotes, comments, sentiment)
- Scans TikTok via Google to find what content is blowing up
- Saves everything to Excel with timestamps
- Gives you a clean daily report of what's trending RIGHT NOW
"""

import praw
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os
import time

# ============================================
# CUSTOMIZE THIS SECTION
# ============================================

# --- REDDIT SETUP ---
# Step 1: Go to https://www.reddit.com/prefs/apps
# Step 2: Click "Create App" at the bottom
# Step 3: Name it anything, pick "script", skip redirect URI
# Step 4: Copy your client_id and client_secret here
REDDIT_CLIENT_ID     = "your-reddit-client-id"
REDDIT_CLIENT_SECRET = "your-reddit-client-secret"
REDDIT_USER_AGENT    = "MacMiniTrendScanner/1.0 by Rafid"

# --- WHAT TO SEARCH ---
KEYWORDS = [
    "mac mini",
    "mac mini m4",
    "mac mini 2024",
    "mac mini m4 pro",
    "apple mac mini",
]

# --- WHERE TO LOOK ON REDDIT ---
SUBREDDITS = [
    "macmini",      # The main Mac Mini community
    "apple",        # General Apple subreddit
    "mac",          # General Mac subreddit
    "applehelp",    # People asking questions
    "hardware",     # Tech hardware discussion
]

# --- OUTPUT ---
OUTPUT_FILE = "mac_mini_trends.xlsx"
SEEN_FILE   = "seen_trend_posts.json"

# ============================================
# THE ENGINE - REDDIT SCANNER
# ============================================

def load_seen_posts():
    """
    Load the list of posts we've already seen.

    WHY: Without this, every time you run the script
    you'd see the same posts over and over.
    We save IDs to a JSON file and check against it.
    """
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))     # set() = faster lookups than a list
    return set()


def save_seen_posts(seen):
    """
    Save post IDs so we remember what we've already seen.

    WHY we use list(seen):
    JSON can't save Python sets directly.
    We convert to list to save, then convert back to set when loading.
    """
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def scan_reddit(seen_posts):
    """
    Search Reddit for Mac Mini trending posts.

    HOW PRAW WORKS:
    PRAW = Python Reddit API Wrapper
    It's a library that talks to Reddit's servers FOR us.
    We give it credentials, it gives us data.

    reddit.subreddit("macmini")  →  Opens that subreddit
    .search("mac mini")          →  Searches inside it
    limit=20                     →  Get the top 20 results
    sort="hot"                   →  Sort by what's trending NOW
    """
    print("\n  Connecting to Reddit...")

    # Create the Reddit connection
    # This is like logging into Reddit but for a script
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    results = []

    for subreddit_name in SUBREDDITS:
        print(f"  Scanning r/{subreddit_name}...")

        subreddit = reddit.subreddit(subreddit_name)

        for keyword in KEYWORDS:
            try:
                # Search this subreddit for the keyword
                # time_filter="week" = only posts from the last 7 days
                posts = subreddit.search(
                    keyword,
                    sort="hot",
                    time_filter="week",
                    limit=15,
                )

                for post in posts:
                    # post.id = unique ID Reddit gives every post
                    # We use it to track what we've already seen
                    if post.id in seen_posts:
                        continue    # Skip if we've seen this before

                    seen_posts.add(post.id)

                    results.append({
                        "platform":    "Reddit",
                        "subreddit":   f"r/{subreddit_name}",
                        "title":       post.title,
                        "upvotes":     post.score,
                        "comments":    post.num_comments,
                        "upvote_ratio": round(post.upvote_ratio * 100, 1),  # e.g. 94.5%
                        "keyword":     keyword,
                        "url":         f"https://reddit.com{post.permalink}",
                        "author":      str(post.author),
                        "date_found":  datetime.now().strftime("%Y-%m-%d"),
                        "type":        classify_post(post.title),
                    })

            except Exception as e:
                print(f"    Could not search {subreddit_name}: {e}")
                continue

            # Small pause between requests
            # WHY: Reddit has rate limits. If you hit their API too fast
            # they will block you. 0.5 seconds is safe.
            time.sleep(0.5)

    return results, seen_posts


def classify_post(title):
    """
    Look at the title and guess what type of post this is.

    WHY: This helps you understand the conversation.
    Is everyone complaining? Asking for help? Praising the product?
    """
    title_lower = title.lower()

    if any(word in title_lower for word in ["review", "worth", "thoughts", "opinion"]):
        return "Review / Opinion"
    elif any(word in title_lower for word in ["help", "issue", "problem", "fix", "error", "not working"]):
        return "Support / Problem"
    elif any(word in title_lower for word in ["buy", "purchase", "order", "shipping", "deal", "price"]):
        return "Buying Decision"
    elif any(word in title_lower for word in ["setup", "build", "configuration", "using it as"]):
        return "Setup / Build"
    elif any(word in title_lower for word in ["vs", "compare", "or", "better"]):
        return "Comparison"
    else:
        return "General Discussion"


# ============================================
# THE ENGINE - TIKTOK SCANNER
# ============================================

def scan_tiktok_via_google(seen_posts):
    """
    Find TikTok videos about Mac Mini by searching Google.

    WHY NOT TIKTOK DIRECTLY?
    TikTok's official API requires a business application
    that takes weeks to get approved. Their website also
    has strong bot detection.

    WHY GOOGLE WORKS:
    Google indexes TikTok videos publicly.
    We search Google for 'site:tiktok.com mac mini'
    which returns TikTok links directly.
    No API needed. No approval needed.

    HOW BeautifulSoup WORKS:
    When Google returns a page of results, it's HTML.
    HTML is a wall of messy tags like <div class="...">
    BeautifulSoup reads that mess and lets us pull out
    exactly what we want, like titles and links.
    """
    print("\n  Scanning TikTok via Google...")

    results = []

    headers = {
        # We tell Google we're a normal browser, not a bot
        # Without this header, Google returns a stripped page
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for keyword in KEYWORDS:
        try:
            # Build the Google search URL
            # site:tiktok.com = only return TikTok results
            # &tbs=qdr:w = results from the past week only
            query = keyword.replace(" ", "+")
            url = f"https://www.google.com/search?q=site:tiktok.com+{query}&tbs=qdr:w&num=10"

            response = requests.get(url, headers=headers, timeout=10)

            # Parse the HTML Google returned
            soup = BeautifulSoup(response.text, "html.parser")

            # Google puts each result in a <div class="g"> block
            search_results = soup.find_all("div", class_="g")

            for result in search_results:
                try:
                    # Find the link inside the result block
                    link_tag = result.find("a")
                    if not link_tag:
                        continue

                    link = link_tag.get("href", "")

                    # Only keep actual TikTok video links
                    if "tiktok.com/@" not in link:
                        continue

                    # Get the title of the result
                    title_tag = result.find("h3")
                    title = title_tag.get_text(strip=True) if title_tag else "No title"

                    # Get the description snippet
                    snippet_tag = result.find("div", {"data-sncf": "1"}) or result.find("span", class_="aCOpRe")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    # Use the link as our unique ID to prevent duplicates
                    if link in seen_posts:
                        continue
                    seen_posts.add(link)

                    results.append({
                        "platform":     "TikTok",
                        "subreddit":    "TikTok",
                        "title":        title,
                        "upvotes":      0,          # Google doesn't show likes
                        "comments":     0,
                        "upvote_ratio": 0,
                        "keyword":      keyword,
                        "url":          link,
                        "author":       extract_creator(link),
                        "date_found":   datetime.now().strftime("%Y-%m-%d"),
                        "type":         classify_post(title),
                    })

                except Exception:
                    continue

            print(f"    '{keyword}' → {len([r for r in results if r['keyword'] == keyword])} TikTok results")

            # Be polite to Google. Wait 2 seconds between searches.
            # WHY: If you hammer Google with requests it will block your IP.
            time.sleep(2)

        except Exception as e:
            print(f"    Could not search TikTok for '{keyword}': {e}")
            continue

    return results, seen_posts


def extract_creator(url):
    """
    Pull the creator username from a TikTok URL.

    TikTok URLs look like: https://www.tiktok.com/@username/video/12345
    We want: @username

    .split("@") splits on the @ symbol → ["https://tiktok.com/", "username/video/12345"]
    We take [1] (second part), then split on "/" to get just the username
    """
    try:
        return "@" + url.split("@")[1].split("/")[0]
    except Exception:
        return "Unknown"


# ============================================
# THE REPORT
# ============================================

def print_report(reddit_results, tiktok_results):
    """
    Print a clean summary of what's trending.
    """
    print("\n" + "=" * 55)
    print("   TREND REPORT — MAC MINI")
    print(f"   {datetime.now().strftime('%B %d, %Y — %I:%M %p')}")
    print("=" * 55)

    # --- REDDIT STATS ---
    print(f"\n  REDDIT: {len(reddit_results)} new posts found")

    if reddit_results:
        # Sort by upvotes, show the hottest post
        top_reddit = sorted(reddit_results, key=lambda x: x["upvotes"], reverse=True)

        print("\n  TOP REDDIT POSTS THIS WEEK:")
        print("  " + "-" * 50)
        for post in top_reddit[:5]:
            print(f"\n  [{post['upvotes']:,} upvotes] {post['title'][:60]}")
            print(f"   Subreddit: {post['subreddit']} | Comments: {post['comments']} | Type: {post['type']}")
            print(f"   {post['url']}")

        # Show what types of conversations are happening
        print("\n  CONVERSATION BREAKDOWN:")
        types = {}
        for post in reddit_results:
            types[post["type"]] = types.get(post["type"], 0) + 1
        for post_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * count
            print(f"   {post_type:<25} {bar} ({count})")

    # --- TIKTOK STATS ---
    print(f"\n  TIKTOK: {len(tiktok_results)} videos found")

    if tiktok_results:
        print("\n  TOP TIKTOK CONTENT:")
        print("  " + "-" * 50)
        for video in tiktok_results[:5]:
            print(f"\n  Creator: {video['author']}")
            print(f"  Title:   {video['title'][:65]}")
            print(f"  Link:    {video['url']}")

    print("\n" + "=" * 55)


def save_to_excel(all_results):
    """
    Save everything to Excel, appending to existing data.

    WHY pd.concat:
    If the file already exists, we read it.
    Then we stick the old data and new data together with concat.
    This means your file grows over time — you can track trends week to week.
    """
    if not all_results:
        return

    df_new = pd.DataFrame(all_results)

    if os.path.exists(OUTPUT_FILE):
        df_existing = pd.read_excel(OUTPUT_FILE)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n  Saved {len(all_results)} new entries to {OUTPUT_FILE}")


# ============================================
# RUN THE FULL SCAN
# ============================================

def run_trend_scan():
    """Main function — runs the full scan from start to finish"""

    print("=" * 55)
    print("   RAFID'S MAC MINI TREND SCANNER")
    print("   Reddit + TikTok | Powered by Python")
    print("=" * 55)

    # Load memory (posts we've already seen)
    seen_posts = load_seen_posts()

    # --- REDDIT ---
    reddit_results = []
    if REDDIT_CLIENT_ID != "your-reddit-client-id":
        reddit_results, seen_posts = scan_reddit(seen_posts)
        print(f"  Reddit scan complete: {len(reddit_results)} new posts")
    else:
        print("\n  [REDDIT SKIPPED] Add your Reddit API keys at the top of this file")
        print("  Get them free at: https://www.reddit.com/prefs/apps")

    # --- TIKTOK ---
    tiktok_results, seen_posts = scan_tiktok_via_google(seen_posts)
    print(f"  TikTok scan complete: {len(tiktok_results)} videos found")

    # Save memory
    save_seen_posts(seen_posts)

    # Combine both
    all_results = reddit_results + tiktok_results

    # Print the report
    print_report(reddit_results, tiktok_results)

    # Save to Excel
    save_to_excel(all_results)

    print("\n  Done. Your trends are ready.\n")


# ============================================
# RUN IT
# ============================================

if __name__ == "__main__":
    run_trend_scan()
