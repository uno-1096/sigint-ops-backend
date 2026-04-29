import requests
import logging

log = logging.getLogger(__name__)

ADSBX_URL = "https://api.adsb.lol/v2/ladd"

MILITARY_PREFIXES = [
    "RCH","REACH","JAKE","ROCKY","KING","PEARL","TOPAZ","FORTE",
    "LAGR","EVIL","GHOST","VIPER","EAGLE","HAWK","FALCON","RAPTOR",
    "USAF","NAVY","DUKE","BARON","ACE","EVAC","SWIFT","IRON",
    "ARCAT","MVJ","TOG","VET","PWA","OAE","FFL","SWB","TRITN"
]

def is_military(callsign):
    if not callsign:
        return False
    cs = callsign.strip().upper()
    return any(cs.startswith(p) for p in MILITARY_PREFIXES)

def fetch_aircraft(max_aircraft=100):
    try:
        r = requests.get(ADSBX_URL, timeout=15, headers={"User-Agent": "sigint-ops/1.0"})
        r.raise_for_status()
        data = r.json()
        aircraft = []

        for ac in data.get("ac", []):
            lat = ac.get("lat")
            lon = ac.get("lon")
            if lat is None or lon is None:
                continue

            alt = ac.get("alt_baro") or ac.get("alt_geom") or 0
            if alt == "ground":
                continue
            try:
                alt = int(float(str(alt)))
            except:
                continue

            callsign = (ac.get("flight") or ac.get("r") or "").strip()
            vel = ac.get("gs") or 0
            hdg = ac.get("track") or 0

            aircraft.append({
                "icao":     ac.get("hex", ""),
                "callsign": callsign or ac.get("hex", ""),
                "lat":      round(float(lat), 4),
                "lon":      round(float(lon), 4),
                "altitude": alt,
                "velocity": round(float(vel)),
                "heading":  round(float(hdg)),
                "type":     "military" if is_military(callsign) else "civilian",
            })

            if len(aircraft) >= max_aircraft:
                break

        log.info(f"ADSB: fetched {len(aircraft)} aircraft")
        return aircraft

    except Exception as e:
        log.error(f"ADSB fetch failed: {e}")
        return []
