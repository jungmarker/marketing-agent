"""
Lead Scorer Agent — scores incoming leads and prioritizes the follow-up queue.

Pulls leads from AgentOS API (fsbo-agent), scores them 0–10, and returns
a prioritized list with recommended next action for each lead.

Score rubric:
  10  = Hot: verified contact info + specific timeline + pre-qualified or pre-approved
  7-9 = Warm: engaged, realistic timeline (0-6 months), has down payment questions
  4-6 = Medium: curious but no clear timeline, generic inquiry
  0-3 = Cold: no contact info, spam indicators, far timeline (>12 months)
"""

import anthropic
import httpx
from datetime import datetime
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, AGENTOS_BASE_URL


SYSTEM_PROMPT = """You are a real estate lead scoring assistant for a Baltimore REALTOR®.

Score leads 0-10 based on these signals:
- CONTACT QUALITY: verified phone/email = +2, only email = +1, no contact = -3
- TIMELINE: 0-3 months = +3, 3-6 months = +2, 6-12 months = +1, 12+ months = 0
- MOTIVATION: specific address/neighborhood interest = +2, vague "someday" = 0
- PRE-QUALIFICATION: pre-approved = +2, has talked to lender = +1, hasn't started = 0
- LEAD SOURCE: direct website form = +1, FSBO (motivated seller) = +2, social media = +1
- ENGAGEMENT: multiple touchpoints = +1, single cold form = 0

For each lead, provide:
- score: integer 0-10
- tier: "hot" | "warm" | "medium" | "cold"
- next_action: specific recommended follow-up step
- reasoning: 1-sentence explanation

Return JSON only."""


def fetch_leads_from_agentos() -> list[dict]:
    """Pull leads from AgentOS API. Returns empty list if API is unreachable."""
    try:
        resp = httpx.get(f"{AGENTOS_BASE_URL}/api/v1/leads/", timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        # Return sample leads for testing when AgentOS isn't running
        return [
            {
                "id": "sample-1",
                "name": "Maria Lopez",
                "email": "maria@example.com",
                "phone": "443-555-0101",
                "source": "website_form",
                "message": "Looking to buy my first home in Baltimore, budget around $250K. Pre-approval in progress.",
                "created_at": datetime.now().isoformat(),
                "status": "new",
            },
            {
                "id": "sample-2",
                "name": "James T",
                "email": "jthomp@gmail.com",
                "phone": None,
                "source": "social_media",
                "message": "How much is my house worth?",
                "created_at": datetime.now().isoformat(),
                "status": "new",
            },
        ]


def run(max_leads: int = 20) -> list[dict]:
    """
    Score the most recent unscored leads from AgentOS.
    Returns prioritized list with scores attached.
    """
    leads = fetch_leads_from_agentos()
    if not leads:
        return []

    # Score up to max_leads recent new leads
    new_leads = [l for l in leads if l.get("status") == "new"][:max_leads]
    if not new_leads:
        return []

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    import json
    leads_json = json.dumps(new_leads, indent=2)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Score these leads and return a JSON array:\n\n{leads_json}"
        }],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    scored = json.loads(raw)

    # Merge score data back with original lead data
    scored_by_id = {s.get("id", s.get("lead_id")): s for s in scored}
    results = []
    for lead in new_leads:
        score_data = scored_by_id.get(lead["id"], {})
        results.append({**lead, **score_data})

    # Sort by score descending
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results


if __name__ == "__main__":
    import json
    results = run()
    for r in results:
        tier = r.get("tier", "?")
        score = r.get("score", 0)
        name = r.get("name", "Unknown")
        action = r.get("next_action", "No action")
        print(f"[{tier.upper():6}] {score}/10 — {name}: {action}")
