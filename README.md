# SIGINT Ops — Backend

Real-time global intelligence platform backend. Powers [ops.unocloud.us](https://ops.unocloud.us) with live incident data, news aggregation, and escalation scoring.

## Architecture

Flask + Socket.IO backend polling multiple data sources every 60 seconds, pushing live updates to connected clients via WebSocket.

## Data Sources

| Source | Data | Refresh |
|--------|------|---------|
| GDELT 2.0 | Geolocated global events | 15 min |
| USGS Earthquake API | M2.5+ earthquakes worldwide | 60s |
| Reuters, AP, BBC, Al Jazeera | Breaking news RSS | 60s |
| France 24, DW, UN News | International news RSS | 60s |
| Times of Israel, Haaretz | Middle East news | 60s |
| Al Arabiya, TASS | Regional OSINT | 60s |
| Crisis Group, Relief Web | Conflict/humanitarian | 60s |

## Features

- **Live escalation scoring** — keyword-weighted algorithm scores global tension 0-100
- **Geolocation engine** — extracts country/region coordinates from headlines
- **WebSocket push** — real-time updates to all connected clients
- **REST API** — fallback endpoints for all data
- **Systemd service** — runs as a persistent background service on EC2

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /api/score | Escalation score, active incidents, sources online |
| GET /api/feed | Latest 30 news items with severity tags and coordinates |
| GET /api/incidents | GDELT geolocated events |
| GET /api/earthquakes | USGS earthquake feed |
| GET /api/status | Health check |

## Stack

- Python 3 / Flask
- Flask-SocketIO (WebSocket)
- feedparser (RSS aggregation)
- requests (API polling)
- Systemd (process management)
- Nginx + Certbot (reverse proxy + SSL)

## Deployment

Deployed on AWS EC2 t3.micro (Ubuntu 22.04) behind Nginx with SSL.

```bash
git clone https://github.com/uno-1096/sigint-ops-backend
cd sigint-ops-backend/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## Infrastructure

- **Cloud:** AWS EC2 t3.micro
- **Domain:** ops.unocloud.us (Cloudflare DNS)
- **SSL:** Let's Encrypt via Certbot
- **VPN:** Tailscale
- **Monitoring:** Uptime Kuma

## Related

- [Frontend Repository](https://github.com/uno-1096/sigint-ops-frontend)
- [Live Site](https://ops.unocloud.us)
