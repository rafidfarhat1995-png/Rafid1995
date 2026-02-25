"""
Mock TikTok data generator.
Simulates TikTok Research API responses for development and testing.
Replace get_trending_videos() with real API calls when you have access.

TikTok Research API: https://developers.tiktok.com/products/research-api/
"""
import random
import uuid
from datetime import datetime, timedelta
from models import TikTokVideo

# Realistic trending product/brand scenarios (Chris Camillo style targets)
TRENDING_SCENARIOS = [
    {
        "keywords": ["stanley cup", "stanley quencher", "stanley tumbler"],
        "hashtags": ["#StanleyCup", "#StanleyQuencher", "#WaterBottle", "#Hydration", "#TikTokMadeMeBuyIt"],
        "authors": ["lifestyle_hannah", "drinkware_queen", "hydration_nation", "cupobsessed"],
        "sentiment_weight": 0.9,  # mostly positive
    },
    {
        "keywords": ["celsius energy", "celsius drink", "celsius energy drink"],
        "hashtags": ["#Celsius", "#CelsiusDrink", "#EnergyDrink", "#GymTok", "#PreWorkout"],
        "authors": ["gymtok_official", "fitness_fever", "preworkout_pete", "energy_enthusiast"],
        "sentiment_weight": 0.85,
    },
    {
        "keywords": ["elf cosmetics", "elf lip", "elf concealer", "elf foundation"],
        "hashtags": ["#ElfCosmetics", "#ElfBeauty", "#DrugstoreMakeup", "#MakeupTok", "#CrueltyFree"],
        "authors": ["makeup_maven", "budget_beauty", "cosmetic_queen", "glow_up_girl"],
        "sentiment_weight": 0.88,
    },
    {
        "keywords": ["crocs", "crocs jibbitz", "crocs platform", "crocs trend"],
        "hashtags": ["#Crocs", "#CrocsStyle", "#Jibbitz", "#ComfortShoes", "#OOTD"],
        "authors": ["shoe_obsessed", "comfort_first_fashion", "croc_collector", "trendy_toes"],
        "sentiment_weight": 0.75,
    },
    {
        "keywords": ["hims ed", "hims hair loss", "hims skincare"],
        "hashtags": ["#Hims", "#MensHealth", "#HairLoss", "#HealthTok", "#Wellness"],
        "authors": ["mens_health_talk", "hair_loss_journey", "wellness_warrior_m", "health_hacks_guy"],
        "sentiment_weight": 0.7,
    },
    {
        "keywords": ["duolingo streak", "duolingo app", "duolingo owl"],
        "hashtags": ["#Duolingo", "#LearnOnTikTok", "#LanguageLearning", "#DuolingoStreak", "#LanguageTok"],
        "authors": ["language_lover_leo", "streak_keeper", "duolingo_addict", "polyglot_pod"],
        "sentiment_weight": 0.82,
    },
    {
        "keywords": ["apple vision pro", "vision pro review", "spatial computing"],
        "hashtags": ["#AppleVisionPro", "#VisionPro", "#Apple", "#SpatialComputing", "#TechTok"],
        "authors": ["tech_daily_dose", "apple_insider_fan", "future_tech_now", "gadget_guru_g"],
        "sentiment_weight": 0.78,
    },
    {
        "keywords": ["amazon prime", "amazon haul", "amazon finds"],
        "hashtags": ["#AmazonFinds", "#AmazonHaul", "#TikTokMadeMeBuyIt", "#AmazonMustHaves", "#Shopping"],
        "authors": ["amazon_addict_amy", "haul_queen_h", "finds_obsessed", "deal_hunter_daily"],
        "sentiment_weight": 0.87,
    },
    {
        "keywords": ["nvidia gpu", "rtx 5090", "nvidia stock", "ai chip"],
        "hashtags": ["#Nvidia", "#GPU", "#AITok", "#TechTok", "#GamingSetup"],
        "authors": ["gpu_nerd_g", "ai_investing", "tech_stocks_talk", "gaming_rig_review"],
        "sentiment_weight": 0.8,
    },
    {
        "keywords": ["lululemon align", "lululemon leggings", "lululemon haul"],
        "hashtags": ["#Lululemon", "#AthleticWear", "#LululemonLeggings", "#FitnessFashion", "#OOTD"],
        "authors": ["athleisure_queen", "lulu_lover_l", "pilates_princess", "workout_wardrobe"],
        "sentiment_weight": 0.9,
    },
]

COMMENT_TEMPLATES = [
    "I just bought this!!",
    "Obsessed with this 😍",
    "Where can I get this?",
    "This is all over my fyp",
    "Just ordered mine!",
    "Game changer fr fr",
    "My whole feed is this rn",
    "I need this in my life",
    "Already bought 3",
    "Can't believe I slept on this",
]


def _random_datetime_in_window(hours_back: int = 48) -> datetime:
    """Generate a random datetime within the last N hours."""
    now = datetime.utcnow()
    offset = random.uniform(0, hours_back * 3600)
    return now - timedelta(seconds=offset)


def _generate_video(scenario: dict, is_trending: bool = False) -> TikTokVideo:
    """Generate a single mock TikTok video for a given scenario."""
    keyword = random.choice(scenario["keywords"])
    author = random.choice(scenario["authors"])
    hashtags = random.sample(scenario["hashtags"], k=random.randint(2, len(scenario["hashtags"])))

    # Trending videos get much higher view counts (power law distribution)
    if is_trending:
        views = random.randint(500_000, 15_000_000)
        likes = int(views * random.uniform(0.05, 0.15))
    else:
        views = random.randint(10_000, 500_000)
        likes = int(views * random.uniform(0.03, 0.10))

    comments = int(likes * random.uniform(0.05, 0.2))
    shares = int(likes * random.uniform(0.02, 0.12))

    descriptions = [
        f"You NEED to try {keyword} - completely changed my life 🙌",
        f"POV: you discovered {keyword} on TikTok",
        f"I cannot stop talking about {keyword}",
        f"Honest review: {keyword} after 30 days",
        f"Why is everyone suddenly obsessed with {keyword}?",
        f"{keyword} haul! Everything I bought this week",
        f"Rating {keyword} so you don't have to",
    ]

    return TikTokVideo(
        video_id=str(uuid.uuid4())[:12],
        author=author,
        description=random.choice(descriptions),
        hashtags=hashtags,
        view_count=views,
        like_count=likes,
        comment_count=comments,
        share_count=shares,
        created_at=_random_datetime_in_window(48),
        sound_name=random.choice(["original sound", "trending audio", "viral sound 2024"]),
        product_mentions=[keyword],
    )


def get_trending_videos(limit: int = 100) -> list[TikTokVideo]:
    """
    Generate mock trending TikTok videos.

    REPLACE THIS FUNCTION with real TikTok Research API calls:
    POST https://open.tiktokapis.com/v2/research/video/query/
    Required scope: research.data.basic

    See: https://developers.tiktok.com/doc/research-api-specs-query-videos
    """
    videos = []

    # Pick 3-5 trending scenarios for this scan window
    active_scenarios = random.sample(TRENDING_SCENARIOS, k=random.randint(3, 5))

    for scenario in active_scenarios:
        # Each active trend generates a cluster of videos
        cluster_size = random.randint(8, 20)
        trending_count = random.randint(2, 5)  # a few breakout viral videos

        for i in range(cluster_size):
            is_trending = i < trending_count
            videos.append(_generate_video(scenario, is_trending=is_trending))

    # Add some noise (unrelated videos)
    noise_scenario = random.choice(TRENDING_SCENARIOS)
    for _ in range(random.randint(5, 15)):
        videos.append(_generate_video(noise_scenario, is_trending=False))

    random.shuffle(videos)
    return videos[:limit]


def get_historical_snapshot(days_back: int = 7) -> list[dict]:
    """
    Generate mock historical trend data for the dashboard sparklines.
    Returns daily signal counts per keyword over the past N days.
    """
    history = []
    now = datetime.utcnow()

    for scenario in TRENDING_SCENARIOS[:6]:  # top 6 for history
        keyword = scenario["keywords"][0]
        daily_counts = []

        base = random.randint(5, 20)
        for d in range(days_back, -1, -1):
            date = (now - timedelta(days=d)).strftime("%Y-%m-%d")
            # Simulate a rising trend for some, flat for others
            growth = random.uniform(0.9, 1.4) if random.random() > 0.3 else random.uniform(0.7, 1.1)
            base = max(1, int(base * growth))
            daily_counts.append({"date": date, "count": base + random.randint(-2, 5)})

        history.append({"keyword": keyword, "history": daily_counts})

    return history
