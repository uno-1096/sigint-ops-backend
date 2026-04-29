
# Confidence scoring based on source credibility + content signals

SOURCE_CREDIBILITY = {
    "Reuters": 95, "AP News": 95, "AP Top News": 95,
    "BBC World": 90, "France 24": 88, "DW News": 87,
    "Al Jazeera": 82, "The Guardian": 83, "UN News": 90,
    "Times of Israel": 78, "Jerusalem Post": 75, "Haaretz": 82,
    "Al Arabiya": 72, "TASS": 45, "Relief Web": 88,
    "Crisis Group": 85, "Reuters World": 95, "Reuters Politics": 95,
    "Kyiv Independent": 70, "Euromaidan": 65, "Middle East Eye": 72,
    "Global Voices": 70, "Axios World": 85, "OSINT_X": 55,
}

CONFIRMED_KW  = ["confirmed","official","government","ministry","according to","announced","statement"]
UNCONFIRMED_KW = ["alleged","reportedly","unconfirmed","claims","sources say","rumored","possible"]

def calculate_confidence(source, title, summary):
    base = SOURCE_CREDIBILITY.get(source, 60)
    text = (title + " " + (summary or "")).lower()

    bonus = 0
    if any(k in text for k in CONFIRMED_KW):
        bonus += 10
    if any(k in text for k in UNCONFIRMED_KW):
        bonus -= 15
    if "breaking" in text:
        bonus -= 5  # breaking news less verified

    score = max(10, min(99, base + bonus))
    
    if score >= 85:
        label = "High"
        color = "#97c459"
    elif score >= 65:
        label = "Medium"
        color = "#ef9f27"
    else:
        label = "Low"
        color = "#e24b4a"

    return {"score": score, "label": label, "color": color}
