"""
Follow-up Agent — generates personalized follow-up messages for leads.

Given a lead's profile and their stage in the pipeline, produces:
  - SMS text (under 160 chars)
  - Email subject + body
  - Voicemail script (30 seconds)

Bilingual: will write in Spanish if the lead's name or message suggests Spanish-speaking.
"""

import anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, BRAND


SYSTEM_PROMPT = f"""You are writing follow-up messages for {BRAND['name']}, a bilingual
(English/Spanish) REALTOR® in Baltimore, MD at Long & Foster Real Estate.

TONE RULES:
- Personal and direct — use the lead's first name
- Never salesy or pushy — be a helpful advisor, not a closer
- Reference something specific from their inquiry when possible
- Keep SMS under 155 characters (leave room for name)
- Email body: 3–5 short paragraphs, mobile-friendly

BILINGUAL RULE:
- If the lead's name or message is in Spanish, write all outputs in Spanish
- Otherwise write in English

COMPLIANCE:
- Always sign off with: Nick Jungmarker | REALTOR® | Long & Foster | (301) 875-7182
- Never make promises about price appreciation or investment returns
- Fair Housing: never reference the lead's race, religion, national origin, etc.

OUTPUT FORMAT — return JSON only:
{{
  "sms": "...",
  "email_subject": "...",
  "email_body": "...",
  "voicemail_script": "...",
  "language": "english" | "spanish"
}}
"""


def run(lead: dict, stage: str = "initial") -> dict:
    """
    Generate follow-up messages for a single lead.

    Args:
        lead: dict with keys: name, email, phone, source, message, score, tier
        stage: "initial" | "day3" | "day7" | "day14" | "day30" | "reactivation"
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    stage_context = {
        "initial":     "This is the first outreach, within 24 hours of the lead coming in.",
        "day3":        "3 days since initial contact. No response yet. Gentle check-in.",
        "day7":        "7 days out. Second follow-up. Add value — share a relevant resource.",
        "day14":       "2 weeks out. Last easy follow-up before spacing out to monthly.",
        "day30":       "1 month out. Long-game nurture — market update angle.",
        "reactivation":"This lead went cold 60+ days ago. Reactivation with a fresh angle.",
    }.get(stage, "Initial outreach.")

    user_prompt = f"""
Lead details:
- Name: {lead.get('name', 'there')}
- Source: {lead.get('source', 'unknown')}
- Their message: {lead.get('message', '(no message)')}
- Lead score: {lead.get('score', 'unscored')}/10 — {lead.get('tier', 'unknown')} tier
- Next action noted: {lead.get('next_action', 'general follow-up')}

Follow-up stage: {stage}
Context: {stage_context}

Generate personalized follow-up messages. Return JSON only.
"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    import json
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    result["generated_at"] = datetime.now().isoformat()
    result["lead_name"] = lead.get("name", "Unknown")
    result["stage"] = stage
    return result


if __name__ == "__main__":
    import json
    sample_lead = {
        "name": "Maria Lopez",
        "source": "website_form",
        "message": "Looking to buy my first home in Baltimore, budget $250K. Pre-approval in progress.",
        "score": 8,
        "tier": "warm",
        "next_action": "Call within 24 hours to discuss pre-approval timeline",
    }
    result = run(sample_lead, stage="initial")
    print(json.dumps(result, indent=2))
