import requests
import logging
from data.locations import get_location
from data.bias import get_bias
from data.confidence import calculate_confidence

log = logging.getLogger(__name__)

GUARDIAN_KEY = "d3d5cb08-f2dc-4572-9a90-79a9c5d57e0b"
GUARDIAN_URL = "https://content.guardianapis.com/search"

QUERIES = [
    "war OR conflict OR military OR airstrike",
    "iran OR israel OR ukraine OR russia OR nato",
    "sanctions OR nuclear OR missile OR attack",
    "protest OR coup OR crisis OR emergency",
]

def fetch_guardian():
    if not GUARDIAN_KEY:
        return []
    items = []
    seen = set()
    try:
        for q in QUERIES:
            r = requests.get(GUARDIAN_URL, params={
                "api-key": GUARDIAN_KEY,
                "q": q,
                "lang": "en",
                "order-by": "newest",
                "page-size": 10,
                "show-fields": "thumbnail,trailText,headline",
            }, timeout=10)
            r.raise_for_status()
            for article in r.json().get("response", {}).get("results", []):
                title = article.get("webTitle", "").strip()
                if not title or title in seen:
                    continue
                seen.add(title)
                fields = article.get("fields", {})
                summary = fields.get("trailText", "")[:200]
                image = fields.get("thumbnail")
                url = article.get("webUrl", "")
                pub = article.get("webPublicationDate", "")
                coords = get_location(title, summary)
                items.append({
                    "source": "The Guardian",
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
                    "bias": get_bias("The Guardian"),
                    "confidence": calculate_confidence("The Guardian", title, summary),
                    "coverage_count": 1,
                    "coverage_sources": ["The Guardian"],
                })
        log.info(f"Guardian: fetched {len(items)} articles")
    except Exception as e:
        log.error(f"Guardian fetch failed: {e}")
    return items
