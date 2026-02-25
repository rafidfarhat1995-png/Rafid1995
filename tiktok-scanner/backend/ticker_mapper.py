"""
Product/brand keyword → public company ticker mapper.
This is the "Chris Camillo core" - connecting viral TikTok trends to tradeable stocks.

Add more mappings as you discover new trends. The broader your mapping database,
the more signals you can act on.
"""
from models import TickerMapping

# Curated database of product/brand → ticker mappings
TICKER_DATABASE: list[TickerMapping] = [
    # Beverages
    TickerMapping("CELH", "Celsius Holdings", ["celsius", "celsius drink", "celsius energy"], "Consumer Staples", "NASDAQ"),
    TickerMapping("KO", "Coca-Cola", ["coca cola", "coke", "sprite", "fanta", "powerade"], "Consumer Staples", "NYSE"),
    TickerMapping("PEP", "PepsiCo", ["pepsi", "mountain dew", "gatorade", "lipton", "tropicana"], "Consumer Staples", "NASDAQ"),
    TickerMapping("MNST", "Monster Beverage", ["monster energy", "monster drink", "monster zero"], "Consumer Staples", "NASDAQ"),
    TickerMapping("BROS", "Dutch Bros", ["dutch bros", "dutch brothers coffee"], "Consumer Discretionary", "NYSE"),

    # Apparel / Footwear
    TickerMapping("CROX", "Crocs Inc", ["crocs", "jibbitz", "croc", "croc shoes", "hey dude"], "Consumer Discretionary", "NASDAQ"),
    TickerMapping("LULU", "Lululemon Athletica", ["lululemon", "lulu align", "lululemon leggings", "lululemon haul"], "Consumer Discretionary", "NASDAQ"),
    TickerMapping("NKE", "Nike", ["nike", "air force", "air jordan", "nike dunk", "swoosh"], "Consumer Discretionary", "NYSE"),
    TickerMapping("DECK", "Deckers Outdoor", ["ugg", "hoka", "hoka shoes", "ugg boots"], "Consumer Discretionary", "NYSE"),
    TickerMapping("SKX", "Skechers", ["skechers", "skechers shoes"], "Consumer Discretionary", "NYSE"),
    TickerMapping("ONON", "On Holding", ["on running", "on cloud shoes", "on shoes"], "Consumer Discretionary", "NYSE"),

    # Personal Care / Beauty / Health
    TickerMapping("ELF", "e.l.f. Beauty", ["elf cosmetics", "elf beauty", "elf lip", "elf concealer", "elf primer"], "Consumer Staples", "NYSE"),
    TickerMapping("HIMS", "Hims & Hers Health", ["hims", "hers", "hims ed", "hims hair loss", "hims skincare"], "Healthcare", "NYSE"),
    TickerMapping("ULTA", "Ulta Beauty", ["ulta", "ulta beauty", "ulta haul"], "Consumer Discretionary", "NASDAQ"),
    TickerMapping("SBH", "Sally Beauty", ["sally beauty", "sally hansen"], "Consumer Discretionary", "NYSE"),

    # Tech / Consumer Electronics
    TickerMapping("AAPL", "Apple", ["apple", "iphone", "airpods", "macbook", "apple watch", "vision pro", "apple vision pro"], "Technology", "NASDAQ"),
    TickerMapping("NVDA", "NVIDIA", ["nvidia", "rtx", "geforce", "gpu", "ai chip", "nvidia stock"], "Technology", "NASDAQ"),
    TickerMapping("META", "Meta Platforms", ["meta", "instagram", "facebook", "whatsapp", "oculus", "quest"], "Technology", "NASDAQ"),
    TickerMapping("GOOGL", "Alphabet", ["google", "youtube", "pixel phone", "google pixel"], "Technology", "NASDAQ"),
    TickerMapping("AMZN", "Amazon", ["amazon", "amazon haul", "amazon finds", "prime", "amazon prime", "alexa"], "Technology", "NASDAQ"),
    TickerMapping("SPOT", "Spotify", ["spotify", "spotify playlist", "spotify wrapped"], "Technology", "NYSE"),

    # Food & Restaurant
    TickerMapping("CAVA", "CAVA Group", ["cava", "cava bowl", "cava restaurant"], "Consumer Discretionary", "NYSE"),
    TickerMapping("CMG", "Chipotle", ["chipotle", "chipotle burrito", "chipotle bowl"], "Consumer Discretionary", "NYSE"),
    TickerMapping("MCD", "McDonald's", ["mcdonalds", "mcdonald's", "big mac", "mcnugget", "happy meal"], "Consumer Discretionary", "NYSE"),
    TickerMapping("SBUX", "Starbucks", ["starbucks", "starbucks drink", "starbucks order", "starbucks secret menu"], "Consumer Discretionary", "NASDAQ"),
    TickerMapping("WEN", "Wendy's", ["wendys", "wendy's frosty", "wendys baconator"], "Consumer Discretionary", "NASDAQ"),

    # Home / Kitchenware
    TickerMapping("SWK", "Stanley Black & Decker", ["stanley cup", "stanley tumbler", "stanley quencher", "stanley bottle"], "Industrials", "NYSE"),
    TickerMapping("POOL", "Pool Corporation", ["pool", "swimming pool", "pool setup"], "Consumer Discretionary", "NASDAQ"),

    # Travel / Leisure
    TickerMapping("ABNB", "Airbnb", ["airbnb", "airbnb stay", "airbnb host"], "Consumer Discretionary", "NASDAQ"),
    TickerMapping("BKNG", "Booking Holdings", ["booking.com", "priceline"], "Consumer Discretionary", "NASDAQ"),

    # Education / Apps
    TickerMapping("DUOL", "Duolingo", ["duolingo", "duolingo streak", "duolingo owl", "duo the owl"], "Technology", "NASDAQ"),

    # Fitness / Health
    TickerMapping("NVO", "Novo Nordisk", ["ozempic", "wegovy", "semaglutide", "weight loss injection"], "Healthcare", "NYSE"),
    TickerMapping("LLY", "Eli Lilly", ["mounjaro", "zepbound", "tirzepatide"], "Healthcare", "NYSE"),
    TickerMapping("PTON", "Peloton", ["peloton", "peloton bike", "peloton tread"], "Consumer Discretionary", "NASDAQ"),

    # Finance / Crypto Adjacent
    TickerMapping("COIN", "Coinbase", ["coinbase", "crypto", "bitcoin", "ethereum", "solana exchange"], "Financial Services", "NASDAQ"),
    TickerMapping("PYPL", "PayPal", ["paypal", "venmo", "paypal pay"], "Financial Services", "NASDAQ"),
    TickerMapping("AFRM", "Affirm", ["affirm", "buy now pay later", "bnpl"], "Financial Services", "NASDAQ"),
]

# Build fast lookup index: keyword → TickerMapping
_keyword_index: dict[str, list[TickerMapping]] = {}
for mapping in TICKER_DATABASE:
    for kw in mapping.keywords:
        kw_lower = kw.lower()
        if kw_lower not in _keyword_index:
            _keyword_index[kw_lower] = []
        _keyword_index[kw_lower].append(mapping)


def find_tickers_for_text(text: str) -> list[TickerMapping]:
    """
    Given any text (video description, hashtag, product mention),
    return all matching ticker mappings.
    """
    text_lower = text.lower()
    matched: dict[str, TickerMapping] = {}  # dedupe by ticker

    for keyword, mappings in _keyword_index.items():
        if keyword in text_lower:
            for m in mappings:
                matched[m.ticker] = m

    return list(matched.values())


def find_tickers_for_keywords(keywords: list[str]) -> list[TickerMapping]:
    """Match a list of keywords to tickers."""
    matched: dict[str, TickerMapping] = {}
    for kw in keywords:
        for m in find_tickers_for_text(kw):
            matched[m.ticker] = m
    return list(matched.values())


def get_all_mappings() -> list[TickerMapping]:
    return TICKER_DATABASE
