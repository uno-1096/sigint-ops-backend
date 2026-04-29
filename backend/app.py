from flask import Flask, jsonify
from datetime import datetime, timezone
from flask_socketio import SocketIO
from flask_cors import CORS
import threading
import time
import logging
from data.gdelt import fetch_gdelt_events
from data.usgs import fetch_earthquakes
from data.rss import fetch_rss_feeds
from data.scoring import calculate_escalation_score
from data.brief import generate_daily_brief
from data.clustering import cluster_stories
from data.newsapi import fetch_newsapi
from data.guardian import fetch_guardian
from data.gdelt_cloud import fetch_gdelt_cloud
from data.finlight import fetch_finlight, start_finlight_stream
from data.newsdata import fetch_newsdata
from data.strategic import get_strategic_locations
from data.history import record_snapshot, get_history
from data.prediction import generate_prediction
from data.ioda import fetch_internet_outages
from data.weather import fetch_weather_alerts
from data.aircraft import fetch_aircraft

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Start Finlight real-time stream
start_finlight_stream()

app = Flask(__name__)
app.config["SECRET_KEY"] = "sigint-ops-secret"
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

state = {
    "incidents":        [],
    "earthquakes":      [],
    "feed_items":       [],
    "aircraft":         [],
    "escalation_score": 0,
    "active_incidents": 0,
    "sources_online":   0,
    "brief":            None,
    "brief_updated":    None,
}

brief_interval = 0  # generate brief every 10 polls (~10 min)

def polling_loop():
    global brief_interval
    while True:
        try:
            log.info("Polling data sources...")

            incidents  = fetch_gdelt_events()
            quakes     = fetch_earthquakes()
            feed       = fetch_rss_feeds()
            newsapi    = fetch_newsapi()
            guardian   = fetch_guardian()
            newsdata   = fetch_newsdata()
            gdelt_cloud = fetch_gdelt_cloud()
            finlight   = fetch_finlight()
            feed       = cluster_stories(feed + newsapi + guardian + newsdata + gdelt_cloud + finlight)
            aircraft   = fetch_aircraft()
            outages    = fetch_internet_outages()
            weather    = fetch_weather_alerts()
            score      = calculate_escalation_score(feed)

            # Generate AI brief every 10 minutes
            brief_interval += 1
            brief = state["brief"]
            brief_updated = state["brief_updated"]
            if brief_interval >= 10 or brief is None:
                log.info("Generating AI brief...")
                result = generate_daily_brief(feed, incidents=incidents + quakes, score=score, aircraft_count=len(aircraft))
                brief = result if isinstance(result, str) else result.get("brief", str(result))
                brief_updated = datetime.now(timezone.utc).isoformat()
                brief_interval = 0

            state['outages'] = outages
            state['weather'] = weather
            state.update({
                "incidents":        incidents,
                "earthquakes":      quakes,
                "feed_items":       feed,
                "aircraft":         aircraft,
                "escalation_score": score,
                "active_incidents": len(incidents) + len(quakes),
                "sources_online":   len([f for f in feed if f]),
                "brief":            brief,
                "brief_updated":    brief_updated,
                "prediction":       state.get("prediction"),
            })

            record_snapshot(score, state["active_incidents"], feed)
            if brief_interval >= 10 or state["prediction"] is None:
                prediction = generate_prediction(feed, score, incidents + quakes)
                if prediction:
                    state["prediction"] = prediction
            socketio.emit("state_update", {
                "incidents":        incidents,
                "earthquakes":      quakes,
                "feed_items":       feed[:30],
                "aircraft":         aircraft,
                "escalation_score": score,
                "active_incidents": state["active_incidents"],
                "brief":            brief,
                "brief_updated":    brief_updated,
                "prediction":       state.get("prediction"),
            })
            log.info(f"Update pushed — score={score}, incidents={len(incidents)}, aircraft={len(aircraft)}, feed={len(feed)}")

        except Exception as e:
            log.error(f"Polling error: {e}")

        time.sleep(20)

@app.route("/api/status")
def status():
    return jsonify({"ok": True, "escalation_score": state["escalation_score"]})

@app.route("/api/incidents")
def incidents():
    return jsonify(state["incidents"])

@app.route("/api/earthquakes")
def earthquakes():
    return jsonify(state["earthquakes"])

@app.route("/api/feed")
def feed():
    return jsonify(state["feed_items"][:30])

@app.route("/api/score")
def score():
    return jsonify({
        "score":            state["escalation_score"],
        "active_incidents": state["active_incidents"],
        "sources_online":   state["sources_online"],
    })

@app.route("/api/aircraft")
def aircraft():
    return jsonify(state["aircraft"])

@app.route('/api/prediction')
def prediction():
    return jsonify({"prediction": state.get("prediction"), "updated": state.get("brief_updated")})

@app.route('/api/weather')
def weather():
    return jsonify(state.get('weather', []))

@app.route('/api/outages')
def outages():
    return jsonify(state.get('outages', []))

@app.route('/api/history')
def history():
    return jsonify(get_history())

@app.route('/api/strategic')
def strategic():
    return jsonify(get_strategic_locations())

@app.route("/api/brief")
def brief():
    return jsonify({
        "brief":   state["brief"] or "Generating initial brief...",
        "updated": state["brief_updated"],
    })

@socketio.on("connect")
def on_connect():
    log.info("Client connected")
    socketio.emit("state_update", {
        "incidents":        state["incidents"],
        "earthquakes":      state["earthquakes"],
        "feed_items":       state["feed_items"][:30],
        "aircraft":         state["aircraft"],
        "escalation_score": state["escalation_score"],
        "active_incidents": state["active_incidents"],
        "brief":            state["brief"],
        "brief_updated":    state["brief_updated"],
    })

if __name__ == "__main__":
    t = threading.Thread(target=polling_loop, daemon=True)
    t.start()
    log.info("Polling thread started")
    socketio.run(app, host="0.0.0.0", port=5002, debug=False, allow_unsafe_werkzeug=True)
