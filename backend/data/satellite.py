import requests
import logging
import time

log = logging.getLogger(__name__)

CDSE_CLIENT_ID = "sh-346fb58c-1377-4036-9925-e8d4af312a4a"
CDSE_CLIENT_SECRET = "VNE1f1GZfBNf7Wr3xgoIcJ4mdsHNiMEW"
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

_token_cache = {"token": None, "expires": 0}

def get_token():
    if _token_cache["token"] and time.time() < _token_cache["expires"] - 60:
        return _token_cache["token"]
    r = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": CDSE_CLIENT_ID,
        "client_secret": CDSE_CLIENT_SECRET,
    }, timeout=10)
    r.raise_for_status()
    data = r.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires"] = time.time() + data.get("expires_in", 3600)
    return _token_cache["token"]

def get_satellite_image(lat, lon):
    try:
        token = get_token()
        size = 0.15
        bbox = [lon - size, lat - size, lon + size, lat + size]

        payload = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
                },
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": "2026-01-01T00:00:00Z",
                            "to": "2026-04-29T23:59:59Z"
                        },
                        "maxCloudCoverage": 30
                    }
                }]
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [{"identifier": "default", "format": {"type": "image/jpeg"}}]
            },
            "evalscript": "//VERSION=3\nfunction setup(){return{input:[{bands:[\"B04\",\"B03\",\"B02\"]}],output:{bands:3}}}\nfunction evaluatePixel(s){return[3.5*s.B04,3.5*s.B03,3.5*s.B02]}"
        }

        r = requests.post(
            PROCESS_URL,
            headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        r.raise_for_status()
        return r.content, "image/jpeg"
    except Exception as e:
        log.error("Satellite image fetch failed: %s" % e)
        return None, None

def get_satellite_image_url(lat, lon):
    return {"lat": lat, "lon": lon}
