"""
Ad Strategy Agent — recommends Meta campaign targeting, budgets, A/B test variations.

Analyzes the Baltimore market context and Nick's goals, then outputs:
  - Campaign structure recommendations
  - Audience targeting parameters (compliant with Housing Special Ad Category)
  - Budget allocation
  - A/B test ideas for the current week
  - Headline + primary text variations for paid ads
"""

import anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, BRAND, BALTIMORE_NEIGHBORHOODS, COMPLIANCE_FOOTER


SYSTEM_PROMPT = f"""You are a paid social media strategist specializing in real estate lead generation
for Meta (Facebook/Instagram). You are advising {BRAND['name']}, a REALTOR® in Baltimore, MD.

CRITICAL COMPLIANCE RULES — these are non-negotiable:
1. ALL real estate ads on Meta MUST use Special Ad Category: Housing
2. Under Housing Special Ad Category, targeting CANNOT exclude by: age, gender, zip code,
   religion, national origin, race, or any protected class proxy
3. Location targeting must be broad geographic areas (counties, MSA) — not zip code exclusions
4. Age targeting is locked at 18–65+ when Housing is selected
5. Interests and behaviors are limited — rely more on Lookalike Audiences and broad targeting

NICK'S LEAD GEN GOALS:
- Campaign A: First-time buyer guide downloads (free Maryland FTB Playbook PDF)
- Campaign B: Seller home valuation requests
- Target CPL (cost per lead): $15–$30
- Monthly budget ceiling: $500–$750 (scaling after proof of concept)
- Geography: Baltimore City + Baltimore County + Montgomery County + PG County

BALTIMORE MARKET CONTEXT:
- Strong inventory of rowhouses $150K–$400K — excellent entry point for FTBs
- Baltimore City Live Near Your Work grant: up to $5,000 for employees of eligible employers
- Maryland SmartBuy: pays off student loans + down payment assistance
- FHA 3.5% down = buyer needs ~$10K on a $250K home (after seller credits)

OUTPUT FORMAT:
Return JSON with keys: campaign_recommendations, ab_test_ideas, weekly_ad_copy_variations, budget_split, notes
"""


def run(weekly_budget: float = 175.0, focus: str = "first_time_buyer") -> dict:
    """
    Generate weekly ad strategy recommendation.

    Args:
        weekly_budget: weekly Meta ad spend budget in USD
        focus: "first_time_buyer" | "seller" | "investor" | "mixed"
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    neighborhoods_str = ", ".join(
        f"{n['name']} (${n['median_price']:,})" for n in BALTIMORE_NEIGHBORHOODS[:5]
    )

    user_prompt = f"""
Week of: {datetime.now().strftime('%B %d, %Y')}
Weekly budget: ${weekly_budget:.0f}
Campaign focus: {focus}
Key Baltimore neighborhoods this week: {neighborhoods_str}

Generate a weekly Meta ad strategy. Include:
1. How to split budget between Campaign A (FTB guide) and Campaign B (seller valuation)
2. 2-3 A/B test ideas for ad creative or copy
3. 3 headline variations and 3 primary text variations for the top campaign
4. Audience strategy within Housing Special Ad Category constraints
5. Any seasonal or market timing notes for this week

Return JSON only (no markdown fences):
{{
  "campaign_recommendations": {{
    "campaign_a_budget": 0.0,
    "campaign_b_budget": 0.0,
    "campaign_a_notes": "...",
    "campaign_b_notes": "..."
  }},
  "ab_test_ideas": ["idea1", "idea2", "idea3"],
  "weekly_ad_copy_variations": {{
    "headlines": ["h1", "h2", "h3"],
    "primary_texts": ["p1", "p2", "p3"],
    "call_to_action": "..."
  }},
  "audience_strategy": "...",
  "budget_split": {{"campaign_a_pct": 60, "campaign_b_pct": 40}},
  "notes": "..."
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
    result["generated_at"] = datetime.now().isoformat()
    result["weekly_budget"] = weekly_budget
    result["focus"] = focus
    return result


if __name__ == "__main__":
    import json
    result = run()
    print(json.dumps(result, indent=2))
