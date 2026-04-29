import requests
import logging
from data.locations import get_location
from data.bias import get_bias
from data.confidence import calculate_confidence

log = logging.getLogger(__name__)

NEWSAPI_KEY = "1521046e36d042e8b0214173566e2b35"
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"

QUERIES = [
    {"category": "general", "country": None, "q": "war OR military OR conflict OR attack"},
    {"category": "general", "country": None, "q": "iran OR israel OR ukraine OR russia"},
    {"category": "general", "country": None, "q": "missile OR airstrike OR sanctions OR nuclear"},
]

def fetch_newsapi():
    if NEWSAPI_KEY == "1521046e36d042e8b0214173566e2b35":
        return []
    items = []
    seen = set()
    try:
        for query in QUERIES:
            params = {
                "apiKey": NEWSAPI_KEY,
                "q": query["q"],
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
            }
            r = requests.get(NEWSAPI_URL, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            for article in data.get("articles", []):
                title = (article.get("title") or "").strip()
                if not title or title in seen:
                    continue
                seen.add(title)
                source = article.get("source", {}).get("name", "NewsAPI")
                summary = (article.get("description") or "")[:200]
                url = article.get("url", "")
                image = article.get("urlToImage")
                pub = article.get("publishedAt", "")
                coords = get_location(title, summary)
                items.append({
                    "source":    source,
                    "title":     title,
                    "summary":   summary,
                    "url":       url,
                    "published": pub,
                    "category":  "news",
                    "severity":  "elevated",
                    "tags":      ["NEWS"],
                    "lat":       coords[0] if coords else None,
                    "lon":       coords[1] if coords else None,
                    "image":     image,
                    "bias":      get_bias(source),
                    "confidence": calculate_confidence(source, title, summary),
                    "coverage_count": 1,
                    "coverage_sources": [source],
                })
        log.info(f"NewsAPI: fetched {len(items)} articles")
    except Exception as e:
        log.error(f"NewsAPI failed: {e}")
    return items
