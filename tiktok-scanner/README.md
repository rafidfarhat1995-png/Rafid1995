# TikTok Social Arbitrage Scanner

A social arbitrage tool inspired by **Chris Camillo's** approach: scan TikTok for viral product/brand trends *before* they hit mainstream media, then map them to public company tickers.

## How It Works

```
TikTok Videos → Trend Clustering → Signal Scoring → Ticker Mapping → Dashboard
```

1. **Ingest** – Pull trending TikTok videos (mock data now, real API ready)
2. **Cluster** – Group videos by product/brand mentions
3. **Score** – Calculate view velocity, sentiment, and signal strength
4. **Map** – Match products to public company tickers (e.g. "Stanley cup" → `SWK`)
5. **Display** – Dashboard shows ranked signals with scores and ticker chips

## Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open: http://localhost:8000

Click **Run Scan** to generate signals.

## Project Structure

```
tiktok-scanner/
├── backend/
│   ├── main.py           # FastAPI server + API routes
│   ├── models.py         # Data models (TikTokVideo, TrendSignal, etc.)
│   ├── scanner.py        # Core trend analysis engine
│   ├── ticker_mapper.py  # Product → ticker mapping database
│   ├── mock_data.py      # Mock TikTok data (replace with real API)
│   └── requirements.txt
├── frontend/
│   └── index.html        # Dashboard UI (vanilla JS, no build step)
└── README.md
```

## Connecting Real TikTok Data

Replace the `get_trending_videos()` function in `mock_data.py`:

1. Apply for [TikTok Research API](https://developers.tiktok.com/products/research-api/) access
2. Use the `POST /v2/research/video/query/` endpoint
3. Map the response fields to the `TikTokVideo` model in `models.py`

```python
# mock_data.py - replace this function
def get_trending_videos(limit: int = 100) -> list[TikTokVideo]:
    # Real API call:
    headers = {"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"}
    body = {
        "query": {"and": [{"operation": "IN", "field_name": "hashtag_name",
                           "field_values": ["TikTokMadeMeBuyIt", "viral", "trending"]}]},
        "start_date": "20240101",
        "end_date": "20240131",
        "max_count": limit,
        "fields": "id,username,video_description,hashtag_names,view_count,like_count,share_count,create_time"
    }
    response = httpx.post("https://open.tiktokapis.com/v2/research/video/query/",
                          headers=headers, json=body)
    # ... map to TikTokVideo objects
```

## Signal Score Breakdown

| Component | Max Points | Description |
|-----------|-----------|-------------|
| View velocity | 40 | Views/hour — accelerating trends score higher |
| Video volume | 30 | More videos = broader organic reach |
| Sentiment | 20 | Positive sentiment = consumer intent |
| Ticker mapped | 10 | Actionable = linked to tradeable stock |

**Signal strength levels:**
- `viral` ≥ 75 — Act now, trend is exploding
- `strong` ≥ 55 — Worth watching closely
- `moderate` ≥ 35 — Early signal, monitor
- `weak` < 35 — Noise, low confidence

## Current Ticker Database

35+ mappings across: Beverages, Apparel/Footwear, Beauty, Tech, Food/Restaurant, Health/Pharma, Finance

Add new mappings in `ticker_mapper.py` → `TICKER_DATABASE`.

## Roadmap

- [ ] Real TikTok Research API integration
- [ ] Persistent database (SQLite → PostgreSQL)
- [ ] Email/Slack alerts when signal crosses threshold
- [ ] Price correlation: does TikTok virality predict stock movement?
- [ ] Creator tracking (monitor specific influencers)
- [ ] Multi-platform: Reddit, Instagram, YouTube Shorts
