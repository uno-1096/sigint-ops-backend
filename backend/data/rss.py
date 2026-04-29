import feedparser
import logging
import re
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from data.locations import get_location
from data.bias import get_bias
from data.confidence import calculate_confidence

log = logging.getLogger(__name__)

FEEDS = [
    {"source": "Reuters",     "url": "https://feeds.reuters.com/reuters/worldNews",       "category": "news"},
    {"source": "AP News",     "url": "https://rsshub.app/apnews/topics/apf-intlnews",     "category": "news"},
    {"source": "BBC World",   "url": "http://feeds.bbci.co.uk/news/world/rss.xml",        "category": "news"},
    {"source": "Al Jazeera",  "url": "https://www.aljazeera.com/xml/rss/all.xml",         "category": "news"},
    {"source": "France 24",   "url": "https://www.france24.com/en/rss",                   "category": "news"},
    {"source": "DW News",     "url": "https://rss.dw.com/rdf/rss-en-all",                 "category": "news"},
    {"source": "USGS Quakes", "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.atom", "category": "disaster"},
    {"source": "Relief Web",  "url": "https://reliefweb.int/updates/rss.xml",             "category": "disaster"},
    {"source": "UN News",     "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "category": "political"},
    {"source": "Times of Israel", "url": "https://www.timesofisrael.com/feed/",           "category": "news"},
    {"source": "Haaretz",     "url": "https://www.haaretz.com/srv/haaretz-israel-news",   "category": "news"},
    {"source": "Al Arabiya",  "url": "https://english.alarabiya.net/tools/rss",           "category": "news"},
    {"source": "TASS",        "url": "https://tass.com/rss/v2.xml",                       "category": "news"},
    {"source": "Global Voices","url": "https://globalvoices.org/feed/",                   "category": "news"},
    {"source": "Crisis Group","url": "https://www.crisisgroup.org/rss.xml",               "category": "political"},
    {"source": "OSINT_X",    "url": "https://nitter.poast.org/warmonitors/rss",           "category": "news"},
    {"source": "OSINT_X",    "url": "https://nitter.poast.org/IntelCrab/rss",             "category": "news"},
    {"source": "OSINT_X",    "url": "https://nitter.poast.org/sentdefender/rss",          "category": "news"},
    {"source": "OSINT_X",    "url": "https://nitter.poast.org/OSINTtechnical/rss",        "category": "news"},
    {"source": "TG:Intel",   "url": "https://rsshub.app/telegram/channel/intelslava",        "category": "news"},
    {"source": "TG:WarNews", "url": "https://rsshub.app/telegram/channel/warnewsua",         "category": "news"},
    {"source": "TG:OSINT",   "url": "https://rsshub.app/telegram/channel/osintdefender",     "category": "news"},
    {"source": "TG:MidEast", "url": "https://rsshub.app/telegram/channel/middleeasteye",     "category": "news"},
    {"source": "Reuters World", "url": "https://feeds.reuters.com/Reuters/worldNews",      "category": "news"},
    {"source": "Reuters Politics","url": "https://feeds.reuters.com/Reuters/politicsNews", "category": "political"},
    {"source": "AP Top News",  "url": "https://rsshub.app/apnews/topics/apf-topnews",      "category": "news"},
    {"source": "Axios World",  "url": "https://api.axios.com/feed/",                       "category": "news"},
    {"source": "The Guardian", "url": "https://www.theguardian.com/world/rss",             "category": "news"},
    {"source": "Jerusalem Post","url": "https://www.jpost.com/rss/rssfeedsfrontpage.aspx", "category": "news"},
    {"source": "Middle East Eye","url": "https://www.middleeasteye.net/rss",               "category": "news"},
    {"source": "Kyiv Independent","url": "https://kyivindependent.com/feed/",             "category": "news"},
    {"source": "Euromaidan",   "url": "https://euromaidanpress.com/feed/",                 "category": "news"},
]

MILITARY_KW  = ["military","troops","airstrike","missile","strike","naval","warship","combat","weapon","bomb","explosion","rocket","drone","idf","irgc","pentagon","nato","forces"]
DISASTER_KW  = ["earthquake","flood","hurricane","typhoon","wildfire","tsunami","eruption","disaster","storm"]
POLITICAL_KW = ["sanctions","diplomat","summit","treaty","election","protest","unrest","coup","resign","parliament"]
CRITICAL_KW  = ["killed","dead","attack","war","crisis","emergency","evacuate","collapse"]

def tag_item(title, summary, category):
    text = (title + " " + summary).lower()
    tags = []
    severity = "monitor"
    if any(k in text for k in CRITICAL_KW):
        severity = "critical"
        tags.append("CRITICAL")
    elif any(k in text for k in MILITARY_KW):
        severity = "elevated"
        tags.append("MILITARY")
    elif any(k in text for k in DISASTER_KW):
        tags.append("DISASTER")
    elif any(k in text for k in POLITICAL_KW):
        tags.append("POLITICAL")
    else:
        tags.append("NEWS")
    return {"severity": severity, "tags": tags}

def fetch_og_data(url, timeout=4):
    try:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        r = requests.get(url, timeout=timeout, headers={"User-Agent": ua})
        text = r.text[:12000]
        image = None
        summary = None
        # Match og:image — handle both attribute orders
        for pat in [
            r'property="og:image"\s+content="([^"]+)"',
            r'content="([^"]+)"\s+property="og:image"',
            r"property='og:image'\s+content='([^']+)'",
        ]:
            m = re.search(pat, text)
            if m:
                image = m.group(1)
                break
        # Match og:description
        for pat in [
            r'property="og:description"\s+content="([^"]+)"',
            r'content="([^"]+)"\s+property="og:description"',
        ]:
            m = re.search(pat, text)
            if m:
                summary = m.group(1)[:200]
                break
        return image, summary
    except Exception:
        return None, None

def fetch_one(feed_def):
    items = []
    try:
        parsed = feedparser.parse(feed_def["url"])
        for entry in parsed.entries[:5]:
            title   = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()[:200]
            link    = entry.get("link", "")
            pub     = entry.get("published", "")
            if not title:
                continue
            image, og_sum = fetch_og_data(link) if link else (None, None)
            if og_sum and not summary:
                summary = og_sum[:200]
            meta   = tag_item(title, summary, feed_def["category"])
            coords = get_location(title, summary)
            items.append({
                "source":    feed_def["source"],
                "title":     title,
                "summary":   summary,
                "url":       link,
                "published": pub,
                "category":  feed_def["category"],
                "severity":  meta["severity"],
                "tags":      meta["tags"],
                "lat":       coords[0] if coords else None,
                "lon":       coords[1] if coords else None,
                "image":     image,
                "bias":      get_bias(feed_def["source"]),
                "confidence": calculate_confidence(feed_def["source"], title, summary),
            })
    except Exception as e:
        log.warning(f"RSS {feed_def['source']} failed: {e}")
    return items

def fetch_rss_feeds():
    all_items = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_one, f): f for f in FEEDS}
        for future in as_completed(futures):
            all_items.extend(future.result())
    priority = {"critical": 0, "elevated": 1, "monitor": 2}
    all_items.sort(key=lambda x: priority.get(x["severity"], 2))
    log.info(f"RSS: fetched {len(all_items)} items from {len(FEEDS)} sources")
    return all_items
