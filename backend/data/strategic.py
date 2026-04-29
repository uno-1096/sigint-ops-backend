# Static strategic locations overlay

STRATEGIC_LOCATIONS = [
    {"name": "Natanz Nuclear Facility", "lat": 33.7244, "lon": 51.7272, "type": "nuclear", "country": "Iran"},
    {"name": "Fordow Nuclear Facility", "lat": 34.8847, "lon": 50.9766, "type": "nuclear", "country": "Iran"},
    {"name": "Dimona Nuclear Reactor",  "lat": 30.9928, "lon": 35.1448, "type": "nuclear", "country": "Israel"},
    {"name": "Zaporizhzhia NPP",        "lat": 47.5076, "lon": 34.5858, "type": "nuclear", "country": "Ukraine"},
    {"name": "Bushehr Nuclear Plant",   "lat": 28.8347, "lon": 50.8881, "type": "nuclear", "country": "Iran"},
    {"name": "Yongbyon Nuclear",        "lat": 39.7939, "lon": 125.7553,"type": "nuclear", "country": "North Korea"},
    {"name": "Al Udeid Air Base",       "lat": 25.1173, "lon": 51.3149, "type": "military","country": "Qatar/USA"},
    {"name": "RAF Akrotiri",            "lat": 34.5974, "lon": 32.9879, "type": "military","country": "Cyprus/UK"},
    {"name": "Diego Garcia",            "lat": -7.3133, "lon": 72.4228, "type": "military","country": "UK/USA"},
    {"name": "Incirlik Air Base",       "lat": 37.0021, "lon": 35.4259, "type": "military","country": "Turkey/USA"},
    {"name": "Naval Base Bahrain",      "lat": 26.1947, "lon": 50.5917, "type": "military","country": "Bahrain/USA"},
    {"name": "Camp Lemonnier",          "lat": 11.5333, "lon": 43.1500, "type": "military","country": "Djibouti/USA"},
    {"name": "Strait of Hormuz",        "lat": 26.5667, "lon": 56.2500, "type": "chokepoint","country": ""},
    {"name": "Strait of Malacca",       "lat": 2.5000,  "lon": 101.000, "type": "chokepoint","country": ""},
    {"name": "Bab el-Mandeb",           "lat": 12.5833, "lon": 43.3333, "type": "chokepoint","country": ""},
    {"name": "Suez Canal",              "lat": 30.4547, "lon": 32.3491, "type": "chokepoint","country": "Egypt"},
]

def get_strategic_locations():
    return STRATEGIC_LOCATIONS
