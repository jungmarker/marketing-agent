"""
Marketing Agent — entry point.

Usage:
  python main.py               # Run today's daily pipeline
  python main.py --day Monday  # Run as if today is Monday
  python main.py --schedule    # Start the daily scheduler (runs at 9am)
  python main.py --analytics   # Force run analytics report
  python main.py --score       # Score leads only
  python main.py --content     # Generate content only
  python main.py --strategy    # Generate ad strategy only
"""

import argparse
import schedule
import time
from datetime import datetime

from orchestrator import run_daily
from agents import content_agent, ad_strategy_agent, lead_scorer, analytics_agent
from config import DAILY_RUN_HOUR, DAILY_RUN_MINUTE


def scheduled_job():
    run_daily()


def main():
    parser = argparse.ArgumentParser(description="Marketing Agent — Baltimore Real Estate")
    parser.add_argument("--day",       help="Override day of week (e.g. Monday)")
    parser.add_argument("--schedule",  action="store_true", help="Run on daily schedule")
    parser.add_argument("--analytics", action="store_true", help="Force analytics report")
    parser.add_argument("--score",     action="store_true", help="Score leads only")
    parser.add_argument("--content",   action="store_true", help="Generate content only")
    parser.add_argument("--strategy",  action="store_true", help="Generate ad strategy only")
    args = parser.parse_args()

    if args.score:
        import json
        results = lead_scorer.run()
        print(f"\n=== LEAD SCORES ({len(results)} leads) ===")
        for r in results:
            tier = r.get("tier", "?").upper()
            score = r.get("score", 0)
            name = r.get("name", "Unknown")
            action = r.get("next_action", "—")
            print(f"[{tier:6}] {score}/10 — {name}")
            print(f"        → {action}")
        return

    if args.content:
        import json
        day = args.day or datetime.now().strftime("%A")
        result = content_agent.run(day_of_week=day)
        print(f"\n=== {day.upper()} CONTENT ===")
        print("\n--- FACEBOOK ---")
        print(result.get("facebook_post", ""))
        print("\n--- INSTAGRAM ---")
        print(result.get("instagram_caption", ""))
        print("\n--- VISUAL ---")
        print(result.get("visual_description", ""))
        return

    if args.strategy:
        import json
        result = ad_strategy_agent.run()
        print(json.dumps(result, indent=2))
        return

    if args.analytics:
        import json
        result = analytics_agent.run(days_back=7)
        a = result.get("analysis", {})
        print("\n=== ANALYTICS REPORT ===")
        print(a.get("summary", ""))
        print("\nWINS:", a.get("wins", []))
        print("CONCERNS:", a.get("concerns", []))
        print("RECOMMENDATIONS:", a.get("recommendations", []))
        return

    if args.schedule:
        print(f"Scheduler started — running daily at {DAILY_RUN_HOUR:02d}:{DAILY_RUN_MINUTE:02d}")
        schedule.every().day.at(f"{DAILY_RUN_HOUR:02d}:{DAILY_RUN_MINUTE:02d}").do(scheduled_job)
        while True:
            schedule.run_pending()
            time.sleep(60)
        return

    # Default: run daily pipeline
    run_daily(day_of_week=args.day, force_analytics=args.analytics)


if __name__ == "__main__":
    main()
