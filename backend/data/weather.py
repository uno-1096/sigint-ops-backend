import requests
import logging

log = logging.getLogger(__name__)

def fetch_weather_alerts():
    alerts = []

    # NOAA Active Alerts - extreme and severe only
    try:
        r = requests.get(
            "https://api.weather.gov/alerts/active",
            params={"status": "actual", "message_type": "alert", "severity": "Extreme,Severe"},
            headers={"User-Agent": "sigint-ops/1.0 (ops.unocloud.us)"},
            timeout=10
        )
        r.raise_for_status()
        for feature in r.json().get("features", [])[:15]:
            props = feature.get("properties", {})
            geo = feature.get("geometry") or {}
            coords = None
            if geo.get("type") == "Point":
                coords = geo["coordinates"]
            elif geo.get("type") == "Polygon":
                c = geo.get("coordinates", [[]])[0]
                if c:
                    coords = c[0]
            alerts.append({
                "title": props.get("headline", props.get("event", "Weather Alert")),
                "type": "weather",
                "severity": "critical" if props.get("severity") == "Extreme" else "elevated",
                "source": "NOAA",
                "lat": float(coords[1]) if coords else None,
                "lon": float(coords[0]) if coords else None,
                "description": props.get("description", "")[:200],
                "url": props.get("web", ""),
            })
        log.info(f"NOAA: {len(alerts)} severe weather alerts")
    except Exception as e:
        log.error(f"NOAA fetch failed: {e}")

    # GDACS Global Disaster Alert
    try:
        r = requests.get(
            "https://www.gdacs.org/gdacsapi/api/events/geteventlist/EVENTS",
            timeout=10,
            headers={"User-Agent": "sigint-ops/1.0"}
        )
        r.raise_for_status()
        for event in r.json().get("features", [])[:10]:
            props = event.get("properties", {})
            level = props.get("alertlevel", "")
            if level not in ["Orange", "Red"]:
                continue
            geo = event.get("geometry", {})
            coords = geo.get("coordinates", [None, None])
            alerts.append({
                "title": props.get("name", "Disaster Alert"),
                "type": "disaster",
                "severity": "critical" if level == "Red" else "elevated",
                "source": "GDACS",
                "lat": float(coords[1]) if len(coords) > 1 and coords[1] else None,
                "lon": float(coords[0]) if coords[0] else None,
                "description": props.get("description", "")[:200],
                "url": "",
            })
        log.info(f"GDACS: {len([a for a in alerts if a['source'] == 'GDACS'])} disaster alerts")
    except Exception as e:
        log.error(f"GDACS fetch failed: {e}")

    return alerts
