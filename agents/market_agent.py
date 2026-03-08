"""
Baltimore Market Research Agent — monitors market conditions to inform content.

Generates weekly market context that feeds the content and strategy agents:
  - Baltimore City median price trend narrative
  - Inventory conditions (buyer's vs seller's market signals)
  - Mortgage rate impact talking points
  - Seasonal market timing notes
  - Neighborhood-specific opportunities to highlight

This is a context-generation agent — its output is passed to content_agent and
ad_strategy_agent to make their output more relevant and timely.
"""

import anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, BALTIMORE_NEIGHBORHOODS, BRAND


SYSTEM_PROMPT = f"""You are a Baltimore real estate market analyst helping {BRAND['name']},
a REALTOR® at Long & Foster, stay on top of market conditions to share with clients.

Your job is to generate market context narratives for content creation — not investment advice.

BALTIMORE MARKET PROFILE (baseline knowledge):
- Baltimore City has ~5,000–8,000 active listings at any time
- Rowhouses dominate: typically 2–4 bed, 1–2 bath, lot sizes under 0.1 acres
- Price range: $80K (distressed) → $600K+ (renovated waterfront/historic)
- First-time buyer sweet spot: $150K–$320K (Waverly, Hamilton, Lauraville, Remington)
- Seasonal pattern: Spring (March–June) = peak activity; Winter = buyer's advantage
- Baltimore City Live Near Your Work grants: up to $5,000 for qualifying employers
- Maryland SmartBuy 3.0: eliminates student debt + provides down payment assistance

CURRENT DATE: {datetime.now().strftime('%B %Y')}

Generate market context that is:
- Honest and accurate (use hedged language: "typically," "historically," "many buyers find")
- Actionable for content creation
- Relatable to renters who haven't considered buying yet
- Compliant with Fair Housing (no neighborhood characterizations based on demographics)

Return JSON with keys: market_summary, key_stats, content_hooks, neighborhood_spotlight,
seasonal_notes, buyer_opportunities, seller_opportunities
"""


def run(week_of: str | None = None) -> dict:
    """Generate weekly Baltimore market context report."""
    if not week_of:
        week_of = datetime.now().strftime("%B %d, %Y")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Spotlight 2 neighborhoods this week
    import random
    spotlight_neighborhoods = random.sample(BALTIMORE_NEIGHBORHOODS, k=2)
    spotlight_str = "\n".join(
        f"- {n['name']}: {n['vibe']}, median ~${n['median_price']:,}"
        for n in spotlight_neighborhoods
    )

    user_prompt = f"""
Week of: {week_of}
Month: {datetime.now().strftime('%B %Y')}
Season: {"Winter" if datetime.now().month in [12,1,2] else "Spring" if datetime.now().month in [3,4,5] else "Summer" if datetime.now().month in [6,7,8] else "Fall"}

Neighborhood spotlight candidates this week:
{spotlight_str}

Generate a comprehensive Baltimore market context package for content creation this week.

Return JSON only (no markdown fences):
{{
  "market_summary": "2-3 sentence overview of current Baltimore market conditions",
  "key_stats": {{
    "median_price_baltimore_city": "$...",
    "days_on_market_avg": "...",
    "inventory_level": "low/moderate/high",
    "market_type": "buyer's/seller's/balanced"
  }},
  "content_hooks": [
    "Attention-grabbing stat or fact suitable for social media hook",
    "Another hook angle",
    "Third hook — different angle"
  ],
  "neighborhood_spotlight": {{
    "primary": {{
      "name": "...",
      "why_now": "Why is this neighborhood good to highlight this week?",
      "talking_points": ["point1", "point2", "point3"]
    }},
    "secondary": {{
      "name": "...",
      "why_now": "...",
      "talking_points": ["point1", "point2"]
    }}
  }},
  "seasonal_notes": "What seasonal factors should content address this week?",
  "buyer_opportunities": ["opportunity1", "opportunity2"],
  "seller_opportunities": ["opportunity1", "opportunity2"]
}}
"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
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
    result["week_of"] = week_of
    result["generated_at"] = datetime.now().isoformat()
    return result


if __name__ == "__main__":
    import json
    result = run()
    print(json.dumps(result, indent=2))
