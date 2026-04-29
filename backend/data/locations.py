
# Country/region keyword to lat/lon lookup
LOCATIONS = {
    "ukraine": (49.0, 31.0), "russia": (61.0, 105.0), "israel": (31.5, 34.8),
    "iran": (32.0, 53.0), "gaza": (31.4, 34.3), "lebanon": (33.9, 35.5),
    "syria": (35.0, 38.0), "iraq": (33.0, 44.0), "yemen": (15.5, 48.0),
    "saudi": (24.0, 45.0), "egypt": (26.0, 30.0), "turkey": (39.0, 35.0),
    "china": (35.0, 105.0), "taiwan": (23.5, 121.0), "japan": (36.0, 138.0),
    "korea": (36.0, 128.0), "india": (20.0, 77.0), "pakistan": (30.0, 69.0),
    "afghanistan": (33.0, 65.0), "sudan": (15.0, 30.0), "ethiopia": (9.0, 39.0),
    "somalia": (6.0, 46.0), "libya": (27.0, 17.0), "mali": (17.0, -4.0),
    "niger": (17.0, 8.0), "nigeria": (9.0, 8.0), "congo": (-4.0, 22.0),
    "myanmar": (17.0, 96.0), "venezuela": (8.0, -66.0), "haiti": (19.0, -72.0),
    "mexico": (23.0, -102.0), "colombia": (4.0, -74.0), "brazil": (-10.0, -55.0),
    "usa": (38.0, -97.0), "united states": (38.0, -97.0), "america": (38.0, -97.0),
    "uk": (54.0, -2.0), "britain": (54.0, -2.0), "france": (46.0, 2.0),
    "germany": (51.0, 10.0), "poland": (52.0, 20.0), "nato": (50.0, 10.0),
    "pentagon": (38.87, -77.05), "washington": (38.9, -77.0),
    "beijing": (39.9, 116.4), "moscow": (55.75, 37.6), "tehran": (35.7, 51.4),
    "tel aviv": (32.1, 34.8), "kyiv": (50.45, 30.52), "baghdad": (33.3, 44.4),
    "kabul": (34.5, 69.2), "islamabad": (33.7, 73.1),
}

def get_location(title, summary=""):
    text = (title + " " + summary).lower()
    for keyword, coords in LOCATIONS.items():
        if keyword in text:
            return coords
    return None
