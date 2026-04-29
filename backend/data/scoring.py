import logging

log = logging.getLogger(__name__)

# Keyword weights for scoring
WEIGHTS = {
    # Tier 1 — war/attack level (high weight)
    'war':         10, 'attack':      9,  'airstrike':   9,
    'missile':     8,  'explosion':   8,  'killed':      8,
    'strike':      7,  'bomb':        7,  'rocket':      7,
    'hostage':     7,  'invasion':    10, 'nuclear':     10,

    # Tier 2 — military/crisis (medium weight)
    'military':    4,  'troops':      4,  'warship':     4,
    'naval':       4,  'sanctions':   3,  'escalat':     5,
    'conflict':    5,  'crisis':      5,  'emergency':   5,
    'combat':      5,  'drone':       4,  'irgc':        6,

    # Tier 3 — political tension (low weight)
    'protest':     2,  'unrest':      2,  'coup':        4,
    'evacuate':    3,  'warning':     2,  'threat':      3,
    'deploy':      3,  'intercept':   4,
}

def calculate_escalation_score(feed_items: list) -> int:
    """
    Score 0-100 based on:
    - Keyword severity weighting across all headlines
    - Volume of critical/elevated items
    - Recency bonus for critical items at top of feed
    """
    if not feed_items:
        return 0

    raw_score = 0
    critical_count  = sum(1 for i in feed_items if i.get('severity') == 'critical')
    elevated_count  = sum(1 for i in feed_items if i.get('severity') == 'elevated')

    # Keyword scan across all headlines
    for item in feed_items:
        text = (item.get('title', '') + ' ' + item.get('summary', '')).lower()
        for keyword, weight in WEIGHTS.items():
            if keyword in text:
                raw_score += weight

    # Volume bonus
    raw_score += critical_count * 5
    raw_score += elevated_count * 2

    # Recency boost — top 5 items count double
    for item in feed_items[:5]:
        text = (item.get('title', '') + ' ' + item.get('summary', '')).lower()
        for keyword, weight in WEIGHTS.items():
            if keyword in text:
                raw_score += weight  # double count for recency

    # Normalize to 0-100
    # Raw scores typically land between 0-400 in active periods
    normalized = min(100, int((raw_score / 400) * 100))

    log.info(f"Escalation score: {normalized} (raw={raw_score}, critical={critical_count}, elevated={elevated_count})")
    return normalized
