import websocket
import threading
import logging
import json
import time
from data.locations import get_location
from data.bias import get_bias
from data.confidence import calculate_confidence

log = logging.getLogger(__name__)

FINLIGHT_KEY = "sk_b933ae6a4b4d62fd87a8544b5dc27f45ffc6ff1aec1155a4efe5c7c9d6e3a04f"

finlight_buffer = []
buffer_lock = threading.Lock()

def on_message(ws, message):
    global finlight_buffer
    try:
        data = json.loads(message)
        articles = data if isinstance(data, list) else [data]
        for article in articles:
            title = (article.get("title") or "").strip()
            if not title:
                continue
            summary = article.get("summary", "")[:200]
            source = article.get("source", "Finlight")
            coords = get_location(title, summary)
            item = {
                "source": source,
                "title": title,
                "summary": summary,
                "url": article.get("link", article.get("url", "")),
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
            with buffer_lock:
                finlight_buffer.insert(0, item)
                finlight_buffer = finlight_buffer[:100]
            log.info("Finlight LIVE: %s" % title[:60])
    except Exception as e:
        log.error("Finlight message error: %s" % e)

def on_error(ws, error):
    log.error("Finlight WS error: %s" % error)

def on_close(ws, close_status_code, close_msg):
    log.warning("Finlight WS closed, reconnecting in 30s...")
    time.sleep(30)
    start_finlight_stream()

def on_open(ws):
    log.info("Finlight WebSocket connected - live stream active!")

def start_finlight_stream():
    if not FINLIGHT_KEY:
        return
    try:
        ws = websocket.WebSocketApp(
            "wss://wss.finlight.me/raw?apiKey=" + FINLIGHT_KEY,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        t = threading.Thread(target=ws.run_forever, daemon=True)
        t.start()
        log.info("Finlight WebSocket stream started")
    except Exception as e:
        log.error("Finlight stream failed: %s" % e)

def fetch_finlight():
    with buffer_lock:
        return list(finlight_buffer)
