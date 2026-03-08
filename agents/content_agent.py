"""
Content Agent — generates Facebook + Instagram post copy.

Given a day-of-week theme from the content calendar, produces:
  - Facebook post (longer, more educational)
  - Instagram caption (punchy hook + hashtags)
  - Suggested visual description for the creative team

Uses Claude claude-sonnet-4-6 with a system prompt tuned to Nick's brand voice.
"""

import anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, BRAND, COMPLIANCE_FOOTER, CONTENT_CALENDAR, BALTIMORE_NEIGHBORHOODS
import random


SYSTEM_PROMPT = f"""You are a social media content writer for {BRAND['name']}, a bilingual (English/Spanish)
REALTOR® with Long & Foster Real Estate in Maryland.

BRAND VOICE:
- Direct, warm, approachable — not corporate
- Educates without being preachy
- Uses real numbers and local specifics (Baltimore neighborhoods, actual price points)
- Bilingual: writes primarily in English but occasionally drops natural Spanish phrases
- Shows personality — Nick works with real people making the biggest financial decision of their lives
- Never generic "call me for all your real estate needs" filler

TARGET AUDIENCE (Baltimore metro):
- First-time home buyers aged 25–40 who are currently renting and think they can't afford to buy
- Move-up buyers in Baltimore rowhouse neighborhoods
- Investors interested in Baltimore City cash-flow properties

BALTIMORE CONTEXT:
- Baltimore rowhouses are Nick's specialty — brand them as character-filled, affordable, investment-grade
- Key neighborhoods: Hampden ($285K median), Canton ($350K), Federal Hill ($360K), Remington ($240K),
  Charles Village ($230K), Pigtown ($185K), Waverly ($175K), Lauraville ($200K)
- Maryland first-time buyer programs: Maryland Mortgage Program, SmartBuy, Baltimore City Live Near Your Work
- FHA loans: 3.5% down. Conventional: 3–5% down. Many buyers qualify with less than $15K out of pocket.

COMPLIANCE REQUIREMENTS (always include in every post):
- Every caption ends with the compliance footer provided
- Never make specific income, tax, or investment promises
- Never use language that could be discriminatory under Fair Housing

OUTPUT FORMAT:
You return JSON with keys: facebook_post, instagram_caption, visual_description, hashtags
"""


def run(day_of_week: str | None = None) -> dict:
    """
    Generate content for the given day (defaults to today).
    Returns dict with facebook_post, instagram_caption, visual_description, hashtags.
    """
    if not day_of_week:
        day_of_week = datetime.now().strftime("%A")

    calendar_entry = CONTENT_CALENDAR.get(day_of_week, CONTENT_CALENDAR["Monday"])
    neighborhood = random.choice(BALTIMORE_NEIGHBORHOODS)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_prompt = f"""
Today is {day_of_week}.
Theme: {calendar_entry['theme']}
Format: {calendar_entry['format']}
Topic: {calendar_entry['topic']}
Featured neighborhood (if relevant): {neighborhood['name']} — {neighborhood['vibe']}, median price ~${neighborhood['median_price']:,}

Generate content for this. Be specific, use real numbers, make it feel human.

Return JSON only (no markdown fences):
{{
  "facebook_post": "...",
  "instagram_caption": "...",
  "visual_description": "Describe the ideal photo/graphic for this post in 2-3 sentences.",
  "hashtags": ["list", "of", "relevant", "hashtags"]
}}

Every caption must end with this footer exactly:
{COMPLIANCE_FOOTER}
"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    import json
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    result["day"] = day_of_week
    result["theme"] = calendar_entry["theme"]
    result["neighborhood"] = neighborhood["name"]
    result["generated_at"] = datetime.now().isoformat()
    return result


if __name__ == "__main__":
    import json
    result = run()
    print(json.dumps(result, indent=2))
