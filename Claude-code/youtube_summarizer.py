"""
YouTube Summarizer - Built with Claude Code
Rafid's Personal Learning Assistant

What this does:
- Paste any YouTube link
- Pulls the full transcript automatically
- Claude AI summarizes it in seconds
- Tells you if it's worth watching
- Saves all summaries to your personal library
"""

import anthropic
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json
import os
import sys

# ============================================
# SETUP - ADD YOUR CLAUDE API KEY HERE
# Get it free at: console.anthropic.com
# ============================================

ANTHROPIC_API_KEY = "your-api-key-here"
LIBRARY_FILE = "youtube_library.json"

# ============================================
# THE ENGINE
# ============================================

def get_video_id(url):
    """Extract video ID from any YouTube URL format"""
    parsed = urlparse(url)

    if parsed.hostname in ["youtu.be"]:
        return parsed.path[1:]

    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/")[1]

    return None

def get_transcript(video_id):
    """Pull the full transcript from YouTube"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry["text"] for entry in transcript_list])
        return full_text
    except Exception as e:
        return None

def summarize_with_claude(transcript, url):
    """Send transcript to Claude and get intelligent summary"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""
    You are Rafid's personal learning assistant. He is a 30 year old learning
    Python automation and AI tools to rebuild his career and life. He has 90 days
    to master Claude and Python.

    Analyze this YouTube video transcript and give him exactly what he needs:

    TRANSCRIPT:
    {transcript[:8000]}

    Give him this exact format:

    ⚡ ONE LINE SUMMARY
    What this video is about in one punchy sentence.

    🎯 IS IT WORTH WATCHING?
    Yes / No / Maybe — and exactly why in one sentence.

    🧠 THE 3 KEY THINGS TO KNOW
    The 3 most important concepts from this video.
    No fluff. Just what matters.

    🛠️ ACTION STEPS FOR RAFID
    Specific things he can actually do today based on this video.
    Connect it to his goal of learning Python and Claude automation.

    ⏱️ TIME RATING
    If the video is 20 minutes, how many minutes are actually worth watching?
    Tell him which parts to skip.

    🔥 BOTTOM LINE
    One paragraph. Straight talk. Is this relevant to his 90 day plan or not?
    """

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

def save_to_library(url, summary):
    """Save every summary to your personal library"""
    library = []

    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "r") as f:
            library = json.load(f)

    library.append({
        "url": url,
        "summary": summary,
        "date": datetime.now().strftime("%Y-%m-%d %I:%M %p")
    })

    with open(LIBRARY_FILE, "w") as f:
        json.dump(library, f, indent=2)

def show_library():
    """Show all your saved summaries"""
    if not os.path.exists(LIBRARY_FILE):
        print("\n  No summaries saved yet.\n")
        return

    with open(LIBRARY_FILE, "r") as f:
        library = json.load(f)

    print(f"\n  YOUR YOUTUBE LIBRARY — {len(library)} videos summarized\n")
    print("-" * 50)

    for i, item in enumerate(library, 1):
        print(f"\n  [{i}] {item['date']}")
        print(f"  URL: {item['url']}")
        print(f"  {item['summary'][:200]}...")
        print()

def run():
    """Main function"""

    print("=" * 50)
    print("   RAFID'S YOUTUBE SUMMARIZER")
    print("   Powered by Claude AI")
    print("=" * 50)

    # Check for library command
    if len(sys.argv) > 1 and sys.argv[1] == "--library":
        show_library()
        return

    # Get URL from user
    print("\n  Paste a YouTube URL (or type 'library' to see saved summaries):")
    print()
    url = input("  > ").strip()

    if url.lower() == "library":
        show_library()
        return

    if not url:
        print("\n  No URL provided. Exiting.\n")
        return

    # Extract video ID
    print("\n  Getting video ID...")
    video_id = get_video_id(url)

    if not video_id:
        print("\n  Could not read that URL. Make sure it's a valid YouTube link.\n")
        return

    # Get transcript
    print("  Pulling transcript from YouTube...")
    transcript = get_transcript(video_id)

    if not transcript:
        print("\n  No transcript available for this video.")
        print("  This happens with music videos or videos without captions.\n")
        return

    word_count = len(transcript.split())
    print(f"  Transcript pulled. {word_count} words found.")

    # Send to Claude
    print("  Sending to Claude for analysis...")
    print("  (This takes about 10 seconds...)\n")

    summary = summarize_with_claude(transcript, url)

    # Display results
    print("=" * 50)
    print("   CLAUDE'S ANALYSIS")
    print("=" * 50)
    print()
    print(summary)
    print()
    print("=" * 50)

    # Save to library
    save_to_library(url, summary)
    print(f"\n  Saved to your library. ({LIBRARY_FILE})")
    print("  Run 'python youtube_summarizer.py --library' to see all saved videos.")
    print("\n  Time you just saved: watching the whole video.\n")

# ============================================
# RUN IT
# ============================================

if __name__ == "__main__":
    run()
