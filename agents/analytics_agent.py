"""
Analytics Agent — pulls Meta ad performance data and generates weekly reports.

Connects to Meta Graph API to fetch:
  - Spend, impressions, reach, CPM, CTR, leads, CPL
  - Campaign-level breakdown
  - Trend vs prior week

Also generates a plain-English summary with recommendations.
"""

import anthropic
import httpx
from datetime import datetime, timedelta
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID, BRAND


SYSTEM_PROMPT = f"""You are an analytics interpreter for {BRAND['name']}'s Meta ad campaigns.

Given raw Meta Ads API data, generate:
1. Plain-English performance summary (2-3 sentences)
2. What's working well
3. What needs adjustment
4. Specific recommended changes for next week
5. Whether to scale up, hold steady, or pause each campaign

BENCHMARKS for real estate lead gen:
- Good CPL: < $25 per lead
- Acceptable CPL: $25–$50
- Poor CPL: > $50 (pause/restructure)
- Good CTR: > 1.5%
- Good conversion rate (click to lead): > 3%

Return JSON with keys: summary, wins, concerns, recommendations, campaign_actions
"""


def fetch_meta_insights(days_back: int = 7) -> dict:
    """
    Fetch campaign insights from Meta Ads API.
    Returns empty/mock data if token not configured.
    """
    if not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN == "your_page_access_token_here":
        # Return mock data for development / when token not set
        return {
            "data": [
                {
                    "campaign_name": "Campaign A — FTB Guide Download",
                    "spend": "142.50",
                    "impressions": "18420",
                    "reach": "14200",
                    "clicks": "312",
                    "leads": "8",
                    "cpm": "7.74",
                    "ctr": "1.69",
                    "cost_per_lead": "17.81",
                    "date_start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "date_stop": datetime.now().strftime("%Y-%m-%d"),
                },
                {
                    "campaign_name": "Campaign B — Seller Valuation",
                    "spend": "87.25",
                    "impressions": "11300",
                    "reach": "9800",
                    "clicks": "145",
                    "leads": "3",
                    "cpm": "7.72",
                    "ctr": "1.28",
                    "cost_per_lead": "29.08",
                    "date_start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "date_stop": datetime.now().strftime("%Y-%m-%d"),
                },
            ],
            "note": "Mock data — connect FACEBOOK_ACCESS_TOKEN to pull live data",
        }

    # Real API call (when token is configured)
    since = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")

    url = f"https://graph.facebook.com/v19.0/act_{FACEBOOK_PAGE_ID}/campaigns"
    params = {
        "access_token": FACEBOOK_ACCESS_TOKEN,
        "fields": "name,insights{spend,impressions,reach,clicks,leads,cpm,ctr,cost_per_lead}",
        "time_range": f'{{"since":"{since}","until":"{until}"}}',
    }

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e), "data": []}


def run(days_back: int = 7) -> dict:
    """
    Fetch analytics and generate weekly performance report.
    Returns dict with raw data + AI-generated interpretation.
    """
    raw_data = fetch_meta_insights(days_back=days_back)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    import json
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Analyze this week's Meta ad performance and give recommendations:\n\n{json.dumps(raw_data, indent=2)}"
        }],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    analysis = json.loads(raw)
    return {
        "period": f"Last {days_back} days ending {datetime.now().strftime('%Y-%m-%d')}",
        "raw_data": raw_data,
        "analysis": analysis,
        "generated_at": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import json
    result = run()
    print("\n=== ANALYTICS REPORT ===")
    print(result["analysis"].get("summary", ""))
    print("\nWINS:", result["analysis"].get("wins", []))
    print("\nCONCERNS:", result["analysis"].get("concerns", []))
    print("\nRECOMMENDATIONS:", result["analysis"].get("recommendations", []))
