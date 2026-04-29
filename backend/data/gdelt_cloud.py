import requests
import logging

log = logging.getLogger(__name__)

GDELT_CLOUD_KEY = "gdelt_sk_10d5fd179209f970b8c64b657d6cc72783f0e7d6d06beff26d4e837731acc96a"
GDELT_CLOUD_URL = "https://gdeltcloud.com/api/v2/events"

def fetch_gdelt_cloud():
    if not GDELT_CLOUD_KEY:
        return []
    items = []
    try:
        r = requests.get(GDELT_CLOUD_URL,
            params={"event_family": "conflict", "sort": "significance", "limit": 20},
            headers={"Authorization": f"Bearer {GDELT_CLOUD_KEY}"},
            timeout=10
        )
        r.raise_for_status()
        for event in r.json().get("data", []):
            title = event.get("title", "")
            if not title:
                continue
            geo = event.get("geography") or {}
            items.append({
                "source": "GDELT Cloud",
                "title": title,
                "summary": event.get("summary", "")[:200],
                "url": event.get("primary_story_url", event.get("url", "")),
                "published": event.get("date", ""),
                "category": "conflict",
                "severity": "critical" if event.get("has_fatalities") else "elevated",
                "tags": ["CONFLICT"],
                "lat": geo.get("lat"),
                "lon": geo.get("lon"),
                "image": None,
                "bias": {"bias": "center", "label": "C", "color": "#888780"},
                "confidence": {"score": 88, "label": "High", "color": "#97c459"},
                "coverage_count": event.get("article_count", 1),
                "coverage_sources": ["GDELT Cloud"],
            })
        log.info(f"GDELT Cloud: fetched {len(items)} conflict events")
    except Exception as e:
        log.error(f"GDELT Cloud fetch failed: {e}")
    return items
