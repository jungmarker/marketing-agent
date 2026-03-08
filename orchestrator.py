"""
Marketing Orchestrator — coordinates all sub-agents and produces the daily output package.

Daily run sequence:
  1. market_agent    → Baltimore market context for the week
  2. content_agent   → Facebook + Instagram posts (uses market context)
  3. ad_strategy_agent → Weekly paid ad recommendations
  4. lead_scorer     → Score new leads from AgentOS
  5. followup_agent  → Generate follow-ups for hot/warm leads
  6. analytics_agent → Weekly performance report (Saturday only)

Output is written to:
  - output/drafts/YYYY-MM-DD.md  (human-readable review file)
  - output/logs/YYYY-MM-DD.log   (machine log)

In POSTING_MODE=draft: saves to file, waits for review
In POSTING_MODE=auto:  posts directly to Meta (use with caution)
"""

import json
import os
from datetime import datetime
from pathlib import Path

from config import POSTING_MODE, DRAFTS_DIR, LOGS_DIR, BRAND
from agents import content_agent, ad_strategy_agent, lead_scorer, followup_agent, analytics_agent, market_agent
from tools.meta_api import publish_facebook_post, publish_instagram_post
from tools.file_store import save_draft, append_log


def run_daily(day_of_week: str | None = None, force_analytics: bool = False) -> dict:
    """
    Run the full daily marketing pipeline.
    Returns a summary dict of all agent outputs.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    if not day_of_week:
        day_of_week = datetime.now().strftime("%A")

    print(f"\n{'='*60}")
    print(f"  Marketing Orchestrator — {today} ({day_of_week})")
    print(f"  Mode: {POSTING_MODE.upper()}")
    print(f"{'='*60}\n")

    results = {"date": today, "day": day_of_week, "agents": {}}

    # ── 1. Market Context ──────────────────────────────────────────
    print("▶ Running Market Agent...")
    try:
        market_data = market_agent.run()
        results["agents"]["market"] = {"status": "ok", "data": market_data}
        print(f"  ✓ Market summary: {market_data.get('market_summary', '')[:80]}...")
    except Exception as e:
        results["agents"]["market"] = {"status": "error", "error": str(e)}
        print(f"  ✗ Market agent failed: {e}")
        market_data = {}

    # ── 2. Content Generation ──────────────────────────────────────
    print("\n▶ Running Content Agent...")
    try:
        content = content_agent.run(day_of_week=day_of_week)
        results["agents"]["content"] = {"status": "ok", "data": content}
        print(f"  ✓ {day_of_week} content generated ({content.get('theme', '')} theme)")
    except Exception as e:
        results["agents"]["content"] = {"status": "error", "error": str(e)}
        print(f"  ✗ Content agent failed: {e}")
        content = {}

    # ── 3. Ad Strategy (Monday only, or on demand) ─────────────────
    strategy = {}
    if day_of_week == "Monday":
        print("\n▶ Running Ad Strategy Agent (Monday refresh)...")
        try:
            strategy = ad_strategy_agent.run()
            results["agents"]["strategy"] = {"status": "ok", "data": strategy}
            print(f"  ✓ Weekly strategy generated")
        except Exception as e:
            results["agents"]["strategy"] = {"status": "error", "error": str(e)}
            print(f"  ✗ Strategy agent failed: {e}")

    # ── 4. Lead Scoring ────────────────────────────────────────────
    print("\n▶ Running Lead Scorer...")
    try:
        scored_leads = lead_scorer.run(max_leads=10)
        results["agents"]["lead_scoring"] = {"status": "ok", "count": len(scored_leads), "data": scored_leads}
        hot_count = sum(1 for l in scored_leads if l.get("tier") == "hot")
        warm_count = sum(1 for l in scored_leads if l.get("tier") == "warm")
        print(f"  ✓ {len(scored_leads)} leads scored — {hot_count} hot, {warm_count} warm")
    except Exception as e:
        results["agents"]["lead_scoring"] = {"status": "error", "error": str(e)}
        print(f"  ✗ Lead scorer failed: {e}")
        scored_leads = []

    # ── 5. Follow-up Messages for Hot/Warm Leads ──────────────────
    followups = []
    priority_leads = [l for l in scored_leads if l.get("tier") in ("hot", "warm")]
    if priority_leads:
        print(f"\n▶ Running Follow-up Agent for {len(priority_leads)} priority lead(s)...")
        for lead in priority_leads[:3]:  # Cap at 3 per day
            try:
                msgs = followup_agent.run(lead=lead, stage="initial")
                followups.append({"lead": lead.get("name"), "messages": msgs})
                print(f"  ✓ Follow-up drafted for {lead.get('name', 'Unknown')}")
            except Exception as e:
                print(f"  ✗ Follow-up failed for {lead.get('name', '?')}: {e}")
    results["agents"]["followups"] = {"status": "ok", "data": followups}

    # ── 6. Analytics (Saturday only, or forced) ────────────────────
    analytics = {}
    if day_of_week == "Saturday" or force_analytics:
        print("\n▶ Running Analytics Agent (weekly report)...")
        try:
            analytics = analytics_agent.run(days_back=7)
            results["agents"]["analytics"] = {"status": "ok", "data": analytics}
            print(f"  ✓ Weekly analytics report generated")
        except Exception as e:
            results["agents"]["analytics"] = {"status": "error", "error": str(e)}
            print(f"  ✗ Analytics agent failed: {e}")

    # ── Save draft file ────────────────────────────────────────────
    draft_path = save_draft(
        date=today,
        day=day_of_week,
        content=content,
        strategy=strategy,
        scored_leads=scored_leads,
        followups=followups,
        analytics=analytics,
        market=market_data,
    )
    print(f"\n✅ Draft saved: {draft_path}")

    # ── Post or hold ───────────────────────────────────────────────
    if POSTING_MODE == "auto" and content:
        print("\n▶ Auto-posting to Meta...")
        _auto_post(content)
    else:
        print(f"\n⏸  Review mode — open {draft_path} to review before posting.")

    append_log(today, results)
    return results


def _auto_post(content: dict):
    """Post to Facebook + Instagram (only in auto mode)."""
    fb_text = content.get("facebook_post", "")
    ig_caption = content.get("instagram_caption", "")

    if fb_text:
        try:
            resp = publish_facebook_post(fb_text)
            print(f"  ✓ Facebook posted: {resp.get('id', 'ok')}")
        except Exception as e:
            print(f"  ✗ Facebook post failed: {e}")

    if ig_caption:
        try:
            resp = publish_instagram_post(ig_caption)
            print(f"  ✓ Instagram posted: {resp.get('id', 'ok')}")
        except Exception as e:
            print(f"  ✗ Instagram post failed: {e}")


if __name__ == "__main__":
    run_daily()
