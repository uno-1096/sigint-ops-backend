import requests
import logging

log = logging.getLogger(__name__)

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"

def fetch_earthquakes() -> list:
    try:
        r = requests.get(USGS_URL, timeout=10)
        r.raise_for_status()
        data = r.json()

        quakes = []
        for f in data.get('features', []):
            props = f.get('properties', {})
            coords = f.get('geometry', {}).get('coordinates', [])
            if len(coords) < 2:
                continue

            mag   = props.get('mag', 0) or 0
            place = props.get('place', 'Unknown location')
            time_ms = props.get('time', 0)
            url   = props.get('url', '')

            if mag < 2.5:
                continue

            severity = 'critical' if mag >= 6.0 else 'elevated' if mag >= 4.5 else 'monitor'

            quakes.append({
                'id':       f.get('id', ''),
                'lat':      coords[1],
                'lon':      coords[0],
                'title':    f"M{mag:.1f} — {place}",
                'mag':      mag,
                'url':      url,
                'severity': severity,
                'type':     'earthquake',
            })

        log.info(f"USGS: fetched {len(quakes)} earthquakes")
        return quakes

    except Exception as e:
        log.error(f"USGS fetch failed: {e}")
        return []
