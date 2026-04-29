import requests
import logging

log = logging.getLogger(__name__)

# Cloudflare Radar - free internet disruption data
RADAR_URL = "https://api.cloudflare.com/client/v4/radar/annotations/outages"

# Fallback: static known disruption indicators from news
def fetch_internet_outages():
    try:
        r = requests.get(
            "https://api.cloudflare.com/client/v4/radar/annotations/outages",
            headers={"Accept": "application/json"},
            params={"limit": 20, "format": "json"},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        outages = []
        for item in data.get("result", {}).get("annotations", []):
            outages.append({
                "country": item.get("locationName", "Unknown"),
                "country_code": item.get("locationAlpha2", ""),
                "level": "disruption",
                "type": "internet",
                "start": item.get("startDate", ""),
                "end": item.get("endDate", ""),
                "description": item.get("description", ""),
                "score": 1,
            })
        log.info(f"Cloudflare Radar: {len(outages)} outages")
        return outages
    except Exception as e:
        log.error(f"Outage fetch failed: {e}")
        return []
