# TikTok, Reddit & X Scanner

Scans TikTok for social trends, Reddit for real economic sentiment, and X for AI updates — every night while you sleep.

## What It Does

**TikTok Scanner**
- Pulls trending hashtags, sounds, and video themes
- Identifies what topics/themes are going viral
- Captures top videos by play count

**Reddit Economy Scanner**
- Monitors 12 economic subreddits (r/economics, r/personalfinance, r/wallstreetbets, etc.)
- Sentiment analysis on every post — not headlines, actual people talking
- Surfaces "pain points" (high-engagement negative posts) and "green shoots" (positive)
- Tracks keywords like "laid off", "can't afford", "rent too high", "grocery prices"

**X AI Scanner**
- Monitors 19 key AI accounts: OpenAI, Anthropic, Google DeepMind, Sam Altman, Karpathy, Yann LeCun, etc.
- Searches for model releases, research papers, safety news, funding rounds, and more
- Flags breaking news from the last 6 hours separately
- Classifies posts by AI sub-topic: model release, research, agents, open source, regulation, hardware, etc.
- Sentiment analysis on the AI community's mood

**Daily Report**
- Saves a `.md` file you can read and a `.json` file for data use
- Console summary after every scan

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure credentials
```bash
cp .env.example .env
```
Then edit `.env` with your credentials:

**Reddit** (free, 2 minutes):
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app" → choose "script"
3. Copy the `client_id` (under the app name) and `client_secret`
4. Paste into `.env`

**TikTok** (requires a TikTok account):
1. Log into TikTok in Chrome
2. Open DevTools → Application → Cookies → `https://www.tiktok.com`
3. Find the `msToken` cookie, copy its value
4. Paste into `.env` as `TIKTOK_MS_TOKEN`

**X (Twitter)** (free tier, 5 minutes):
1. Go to https://developer.x.com and sign up
2. Create a new Project and App
3. Copy the **Bearer Token** from your app's Keys & Tokens page
4. Paste into `.env` as `X_BEARER_TOKEN`

---

## Usage

**Run once right now (all three scanners):**
```bash
python main.py
```

**Run every night at 11 PM automatically:**
```bash
python main.py --schedule
```

**Quick X-only check (fastest, no TikTok/Reddit):**
```bash
python main.py --x-only
```

**Change the scan time:** Edit `SCAN_HOUR` in `config.py` (24h format, default = 23)

---

## Output

Reports are saved in the `reports/` folder:
- `reports/2024-01-15.md` — readable report
- `reports/2024-01-15.json` — raw data

---

## Customization

Edit `config.py` to:
- Add/remove subreddits (`ECONOMY_SUBREDDITS`)
- Add/remove economy keywords (`ECONOMY_KEYWORDS`)
- Change how many posts to pull (`REDDIT_POST_LIMIT`)
- Add/remove X AI keywords (`X_AI_KEYWORDS`)
- Add/remove X accounts to monitor (`X_AI_ACCOUNTS`)
- Change the nightly scan time (`SCAN_HOUR`)
