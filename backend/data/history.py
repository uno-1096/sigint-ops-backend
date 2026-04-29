import json
import os
import time
import logging
from datetime import datetime, timezone

log = logging.getLogger(__name__)

HISTORY_FILE = "/home/ubuntu/sigint-ops/backend/data/history.json"
MAX_ENTRIES = 288  # 24 hours at 5-min intervals

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE) as f:
                return json.load(f)
    except:
        pass
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history[-MAX_ENTRIES:], f)
    except Exception as e:
        log.error(f"History save failed: {e}")

def record_snapshot(score, active_incidents, feed_items):
    history = load_history()
    snapshot = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "incidents": active_incidents,
        "top_headlines": [
            {"title": i.get("title",""), "source": i.get("source",""), "severity": i.get("severity","")}
            for i in feed_items[:5]
        ]
    }
    history.append(snapshot)
    save_history(history)
    return history

def get_history():
    return load_history()
