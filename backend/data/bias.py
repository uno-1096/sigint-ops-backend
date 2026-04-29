# Media bias ratings based on AllSides + Ad Fontes Media charts
# Bias: far-left, left, center-left, center, center-right, right, far-right

SOURCE_BIAS = {
    # Center
    "Reuters":          {"bias": "center",       "label": "C",  "color": "#888780"},
    "AP News":          {"bias": "center",       "label": "C",  "color": "#888780"},
    "AP Top News":      {"bias": "center",       "label": "C",  "color": "#888780"},
    "USGS Quakes":      {"bias": "center",       "label": "C",  "color": "#888780"},
    "UN News":          {"bias": "center",       "label": "C",  "color": "#888780"},
    "Relief Web":       {"bias": "center",       "label": "C",  "color": "#888780"},
    "Crisis Group":     {"bias": "center",       "label": "C",  "color": "#888780"},
    "Reuters World":    {"bias": "center",       "label": "C",  "color": "#888780"},
    "Reuters Politics": {"bias": "center",       "label": "C",  "color": "#888780"},

    # Center-Left
    "BBC World":        {"bias": "center-left",  "label": "CL", "color": "#378add"},
    "France 24":        {"bias": "center-left",  "label": "CL", "color": "#378add"},
    "DW News":          {"bias": "center-left",  "label": "CL", "color": "#378add"},
    "The Guardian":     {"bias": "center-left",  "label": "CL", "color": "#378add"},
    "Axios World":      {"bias": "center-left",  "label": "CL", "color": "#378add"},
    "Global Voices":    {"bias": "center-left",  "label": "CL", "color": "#378add"},
    "Euronews":         {"bias": "center-left",  "label": "CL", "color": "#378add"},

    # Left
    "Al Jazeera":       {"bias": "left",         "label": "L",  "color": "#185fa5"},
    "Middle East Eye":  {"bias": "left",         "label": "L",  "color": "#185fa5"},
    "Kyiv Independent": {"bias": "left",         "label": "L",  "color": "#185fa5"},
    "Euromaidan":       {"bias": "left",         "label": "L",  "color": "#185fa5"},

    # Center-Right
    "Times of Israel":  {"bias": "center-right", "label": "CR", "color": "#ef9f27"},
    "Jerusalem Post":   {"bias": "center-right", "label": "CR", "color": "#ef9f27"},
    "Haaretz":          {"bias": "center-left",  "label": "CL", "color": "#378add"},

    # Right
    "Al Arabiya":       {"bias": "center-right", "label": "CR", "color": "#ef9f27"},

    # State/Govt aligned
    "TASS":             {"bias": "state",        "label": "ST", "color": "#e24b4a"},

    # OSINT - unrated
    "OSINT_X":          {"bias": "unrated",      "label": "OS", "color": "#b077dd"},
}

def get_bias(source):
    return SOURCE_BIAS.get(source, {"bias": "unrated", "label": "?", "color": "#3a4a58"})
