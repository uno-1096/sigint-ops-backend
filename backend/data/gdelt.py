import requests
import csv
import io
import logging

log = logging.getLogger(__name__)

# GDELT 2.0 CSV direct endpoint - last 15 min events
GDELT_CSV = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

CRITICAL_KEYWORDS = ["attack","strike","missile","bomb","explosion","killed","airstrike","war","conflict","hostage"]
ELEVATED_KEYWORDS = ["protest","clash","arrest","sanctions","military","troops","naval","warship","escalat"]

def classify_severity(title):
    t = title.lower()
    if any(k in t for k in CRITICAL_KEYWORDS):
        return "critical"
    if any(k in t for k in ELEVATED_KEYWORDS):
        return "elevated"
    return "monitor"

def fetch_gdelt_events(max_events=50):
    try:
        # Get the index to find latest file URLs
        r = requests.get(GDELT_CSV, timeout=10)
        r.raise_for_status()
        lines = r.text.strip().splitlines()

        # Line format: "size hash url" - grab all 3 lines, find the export CSV
        csv_url = None
        for line in lines:
            parts = line.strip().split(" ")
            if len(parts) >= 3 and "export" in parts[2]:
                csv_url = parts[2]
                break

        if not csv_url:
            log.error("GDELT: could not find export URL")
            return []

        import zipfile, io as _io
        r2 = requests.get(csv_url, timeout=30)
        r2.raise_for_status()

        raw = _io.BytesIO(r2.content)
        with zipfile.ZipFile(raw) as z:
            name = z.namelist()[0]
            with z.open(name) as f:
                text = f.read().decode("latin-1", errors="replace")

        events = []
        reader = csv.reader(io.StringIO(text), delimiter="\t")
        for row in reader:
            if len(row) < 60:
                continue
            try:
                lat = float(row[56]) if row[56].strip() else None
                lon = float(row[57]) if row[57].strip() else None
                if lat is None or lon is None:
                    continue
                if abs(lat) < 0.1 and abs(lon) < 0.1:
                    continue
                url       = row[60] if len(row) > 60 else ""
                actor1    = row[7].strip()  or "Unknown"
                country   = row[51].strip() or ""
                evtcode   = row[26].strip() or ""
                title     = f"{actor1} — {country} ({evtcode})" if country else actor1
                severity  = classify_severity(title + " " + url)
                events.append({
                    "id":       row[0],
                    "lat":      round(lat, 4),
                    "lon":      round(lon, 4),
                    "title":    title,
                    "url":      url,
                    "severity": severity,
                    "type":     "incident",
                })
            except (ValueError, IndexError):
                continue
            if len(events) >= max_events:
                break

        log.info(f"GDELT: fetched {len(events)} events")
        return events

    except Exception as e:
        log.error(f"GDELT fetch failed: {e}")
        return []
