import websocket
import threading
import logging
import json
import time
from data.locations import get_location
from data.bias import get_bias

log = logging.getLogger(__name__)

FINLIGHT_KEY = "sk_b933ae6a4b4d62fd87a8544b5dc27f45ffc6ff1aec1155a4efe5c7c9d6e3a04f"

# Use a mutable container so the same object is shared across imports
_state = {"buffer": [], "lock": threading.Lock()}

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("action") == "admit":
            log.info("Finlight admitted: %s" % data.get("leaseId"))
            return
        if data.get("action") == "sendArticle":
            article = data.get("data", {})
        else:
            return

        title = (article.get("title") or "").strip()
        if not title:
            return

        summary = article.get("summary", "")[:200]
        source = article.get("source", "Finlight")
        coords = get_location(title, summary)

        item = {
            "source": source,
            "title": title,
            "summary": summary,
            "url": article.get("link", ""),
            "published": article.get("publishDate", ""),
            "category": "news",
            "severity": "elevated",
            "tags": ["LIVE"],
            "lat": coords[0] if coords else None,
            "lon": coords[1] if coords else None,
            "image": None,
            "bias": get_bias(source),
            "confidence": {"score": 80, "label": "Medium", "color": "#ef9f27"},
            "coverage_count": 1,
            "coverage_sources": [source],
        }

        with _state["lock"]:
            _state["buffer"].insert(0, item)
            _state["buffer"] = _state["buffer"][:100]

        log.info("Finlight LIVE: %s" % title[:70])

    except Exception as e:
        log.error("Finlight message error: %s" % e)

def on_error(ws, error):
    log.error("Finlight WS error: %s" % error)

def on_close(ws, close_status_code, close_msg):
    log.warning("Finlight WS closed, reconnecting in 30s...")
    time.sleep(30)
    _connect()

def on_open(ws):
    log.info("Finlight WebSocket connected!")
    ws.send(json.dumps({
        "type": "subscribe",
        "query": "war OR military OR conflict OR attack OR iran OR ukraine OR russia OR israel OR missile OR sanctions OR nuclear"
    }))

def _connect():
    try:
        ws = websocket.WebSocketApp(
            "wss://wss.finlight.me?apiKey=" + FINLIGHT_KEY,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        t = threading.Thread(target=ws.run_forever, daemon=True)
        t.start()
        log.info("Finlight WebSocket thread started")
    except Exception as e:
        log.error("Finlight connect failed: %s" % e)

def start_finlight_stream():
    if not FINLIGHT_KEY:
        return
    _connect()

def fetch_finlight():
    with _state["lock"]:
        return list(_state["buffer"])
