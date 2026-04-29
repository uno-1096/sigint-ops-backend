import requests
import logging
from data.locations import get_location
from data.bias import get_bias
from data.confidence import calculate_confidence

log = logging.getLogger(__name__)

NEWSDATA_KEY = "pub_780ee6fc966649f7b3d9208ad406c3a2"
NEWSDATA_URL = "https://newsdata.io/api/1/news"

def fetch_newsdata():
    if not NEWSDATA_KEY:
        return []
    items = []
    seen = set()
    try:
        r = requests.get(NEWSDATA_URL, params={
            "apikey": NEWSDATA_KEY,
            "q": "war OR conflict OR military OR attack OR crisis",
            "language": "en",
            "category": "politics,world",
            "size": 10,
        }, timeout=10)
        r.raise_for_status()
        for article in r.json().get("results", []):
            title = (article.get("title") or "").strip()
            if not title or title in seen:
                continue
            seen.add(title)
            summary = (article.get("description") or "")[:200]
            url = article.get("link", "")
            image = article.get("image_url")
            pub = article.get("pubDate", "")
            source = article.get("source_name", "NewsData")
            coords = get_location(title, summary)
            items.append({
                "source": source,
                "title": title,
                "summary": summary,
                "url": url,
                "published": pub,
                "category": "news",
                "severity": "monitor",
                "tags": ["NEWS"],
                "lat": coords[0] if coords else None,
                "lon": coords[1] if coords else None,
                "image": image,
                "bias": get_bias(source),
                "confidence": calculate_confidence(source, title, summary),
                "coverage_count": 1,
                "coverage_sources": [source],
            })
        log.info(f"NewsData: fetched {len(items)} articles")
    except Exception as e:
        log.error(f"NewsData fetch failed: {e}")
    return items
