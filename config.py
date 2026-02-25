import os
from dotenv import load_dotenv

load_dotenv()

# Reddit API credentials (get free at https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "TrendScanner/1.0")

# TikTok session token (copy ms_token cookie from browser after logging in)
TIKTOK_MS_TOKEN = os.getenv("TIKTOK_MS_TOKEN", "")

# X (Twitter) API — free tier at https://developer.x.com
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "")

# AI keywords to search on X
X_AI_KEYWORDS = [
    "new AI model", "model release", "OpenAI", "Anthropic", "Google DeepMind",
    "LLM", "GPT", "Claude", "Gemini", "Llama", "Mistral",
    "AI breakthrough", "AI safety", "AGI", "open source AI",
    "AI agent", "multimodal", "reasoning model",
]

# Key AI accounts to monitor directly (no @ symbol)
X_AI_ACCOUNTS = [
    "OpenAI", "AnthropicAI", "GoogleDeepMind", "huggingface",
    "MistralAI", "sama", "karpathy", "ylecun",
]

# Max tweets to pull per search query (max 100 on free tier)
X_MAX_RESULTS_PER_QUERY = 100

# Subreddits to monitor for economic sentiment
ECONOMY_SUBREDDITS = [
    "economics",
    "personalfinance",
    "wallstreetbets",
    "economy",
    "inflation",
    "stocks",
    "investing",
    "povertyfinance",
    "jobs",
    "labor",
    "REBubble",
    "Frugal",
]

# Keywords that signal real economic conditions (not spin)
ECONOMY_KEYWORDS = [
    "laid off", "layoffs", "fired", "can't afford", "rent too high",
    "groceries expensive", "paycheck to paycheck", "debt", "recession",
    "unemployed", "inflation", "price increase", "cost of living",
    "mortgage", "eviction", "medical bills", "job market", "salary",
    "raise", "housing", "food costs", "interest rates", "credit card",
]

# How many posts to pull per subreddit per run
REDDIT_POST_LIMIT = 50

# TikTok categories to scan for trends
TIKTOK_TREND_CATEGORIES = [
    "trending", "foryou", "news", "lifestyle", "money", "food"
]

# Scheduler: run every night at this hour (24h format)
SCAN_HOUR = 23  # 11 PM

# Where to save reports
REPORTS_DIR = "reports"
