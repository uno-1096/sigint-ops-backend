import anthropic
import logging
import os
from datetime import datetime, timezone
from data.history import get_history

log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

def generate_prediction(feed_items, score, incidents):
    """Use Claude to analyze trends and predict escalation trajectory"""
    try:
        history = get_history()
        
        if len(history) < 3:
            return None

        # Build trend data
        recent = history[-24:]
        scores = [h["score"] for h in recent]
        avg_score = sum(scores) / len(scores)
        trend = scores[-1] - scores[0] if len(scores) > 1 else 0
        trend_dir = "RISING" if trend > 5 else "FALLING" if trend < -5 else "STABLE"

        # Get critical headlines
        critical = [i for i in feed_items if i.get("severity") == "critical"][:10]
        headlines = "\n".join([f"- {i.get('source','')}: {i.get('title','')}" for i in critical])

        # Top covered stories
        multi = sorted(feed_items, key=lambda x: x.get("coverage_count", 1), reverse=True)[:5]
        top_stories = "\n".join([f"- [{i.get('coverage_count',1)} sources] {i.get('title','')[:80]}" for i in multi])

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")

        prompt = f"""You are a senior geopolitical analyst. Based on the following intelligence data, provide a PREDICTIVE ASSESSMENT for the next 24-48 hours.

CURRENT STATUS ({now}):
- Escalation Index: {score}/100 ({trend_dir}, {'+' if trend > 0 else ''}{trend:.1f} change over last {len(recent)} snapshots)
- Average score last {len(recent)} snapshots: {avg_score:.1f}
- Active incidents: {len(incidents)}
- Score history (last 10): {scores[-10:]}

TOP MULTI-SOURCE STORIES:
{top_stories}

CRITICAL HEADLINES:
{headlines}

Provide a PREDICTIVE ASSESSMENT with these sections:
1. TRAJECTORY (one sentence: is situation escalating, de-escalating, or stable and why)
2. 24H FORECAST (2-3 sentences on most likely developments in next 24 hours)
3. KEY TRIGGERS (2-3 specific events that could cause rapid escalation)
4. KEY DE-ESCALATORS (2-3 specific events that could reduce tension)
5. PROBABILITY ASSESSMENT (assign rough % probabilities: escalation continues X%, de-escalation Y%, status quo Z%)

Keep it concise, analytical, and actionable. No markdown formatting. Voice like a CIA daily brief."""

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        prediction = response.content[0].text.strip()
        log.info("Predictive assessment generated successfully")
        return prediction

    except Exception as e:
        log.error(f"Prediction generation failed: {e}")
        return None
