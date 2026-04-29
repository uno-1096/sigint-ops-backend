import os
import anthropic
import logging
from datetime import datetime, timezone

log = logging.getLogger(__name__)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def generate_ai_brief(feed_items, incidents, score, aircraft_count):
    """Generate a professional intelligence brief using Claude API"""
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

        # Build context from feed items
        critical = [i for i in feed_items if i.get("severity") == "critical"][:15]
        elevated = [i for i in feed_items if i.get("severity") == "elevated"][:8]

        headlines = ""
        for item in critical:
            headlines += f"[CRITICAL] {item.get('source','')}: {item.get('title','')}\n"
        for item in elevated:
            headlines += f"[ELEVATED] {item.get('source','')}: {item.get('title','')}\n"

        # Build incident summary
        inc_summary = f"{len(incidents)} active incidents tracked globally"

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")

        prompt = f"""You are a senior intelligence analyst. Based on the following OSINT data, write a concise professional SITREP (Situation Report) for {now}.

ESCALATION INDEX: {score}/100
ACTIVE INCIDENTS: {inc_summary}
AIRCRAFT TRACKED: {aircraft_count}

CURRENT HEADLINES:
{headlines}

Write a SITREP with these sections:
1. EXECUTIVE SUMMARY (2-3 sentences, overall situation assessment)
2. KEY DEVELOPMENTS (3-5 most significant events, one line each)
3. REGIONAL FOCUS (which regions have highest activity and why)
4. THREAT ASSESSMENT (current threat level justification)
5. ANALYST NOTE (one sentence on what to watch in next 24 hours)

Keep it concise, professional, and factual. Use intelligence community writing style. No markdown, no bullet points with dashes — use numbered points only."""

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )

        brief = response.content[0].text.strip()
        log.info("Claude AI brief generated successfully")
        return brief

    except Exception as e:
        log.error(f"Claude brief generation failed: {e}")
        return None


def generate_daily_brief(feed_items, incidents=None, score=0, aircraft_count=0):
    """Main brief function - tries Claude first, falls back to rule-based"""
    
    # Try Claude AI brief first
    ai_brief = generate_ai_brief(feed_items, incidents or [], score, aircraft_count)
    if ai_brief:
        return ai_brief

    # Fallback to rule-based brief
    if not feed_items:
        return "Insufficient data for situation report."

    critical = [i for i in feed_items if i.get("severity") == "critical"]
    elevated = [i for i in feed_items if i.get("severity") == "elevated"]

    brief = f"EXECUTIVE SUMMARY: Global threat index stands at {score}/100. "
    brief += f"Analysis of {len(feed_items)} intelligence sources identifies {len(critical)} critical and {len(elevated)} elevated-priority developments across 5 active regions.\n\n"

    if critical:
        brief += "KEY DEVELOPMENTS:\n"
        for i, item in enumerate(critical[:5], 1):
            brief += f"{i}. [{item.get('source','')}] {item.get('title','')}\n"

    brief += "\nSituation remains volatile — continued escalation likely in active regions."
    return brief
