"""
File store — saves drafts and logs to output/ directory.

Drafts are human-readable Markdown files for Nick to review.
Logs are JSON for machine consumption.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from config import DRAFTS_DIR, LOGS_DIR, BRAND


def _ensure_dirs():
    Path(DRAFTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)


def save_draft(
    date: str,
    day: str,
    content: dict,
    strategy: dict,
    scored_leads: list,
    followups: list,
    analytics: dict,
    market: dict,
) -> str:
    """
    Write a human-readable Markdown review file.
    Returns the file path.
    """
    _ensure_dirs()
    path = f"{DRAFTS_DIR}/{date}.md"

    lines = [
        f"# Marketing Daily Brief — {date} ({day})",
        f"_Generated {datetime.now().strftime('%I:%M %p')} | Review before posting_",
        "",
        "---",
        "",
    ]

    # Market snapshot
    if market:
        lines += [
            "## 📊 Baltimore Market Context",
            "",
            market.get("market_summary", "_No market summary available_"),
            "",
        ]
        hooks = market.get("content_hooks", [])
        if hooks:
            lines.append("**Content hooks this week:**")
            for h in hooks:
                lines.append(f"- {h}")
            lines.append("")

    # Social content
    if content:
        lines += [
            "---",
            "",
            f"## 📱 Today's Content ({content.get('theme', '').title()} Theme)",
            f"_Neighborhood spotlight: {content.get('neighborhood', 'N/A')}_",
            "",
            "### Facebook Post",
            "```",
            content.get("facebook_post", "_No content generated_"),
            "```",
            "",
            "### Instagram Caption",
            "```",
            content.get("instagram_caption", "_No content generated_"),
            "```",
            "",
            "### Visual Description",
            f"> {content.get('visual_description', '_No description_')}",
            "",
            "### Hashtags",
            " ".join(f"#{h.lstrip('#')}" for h in content.get("hashtags", [])),
            "",
        ]

    # Ad strategy (Monday)
    if strategy:
        lines += [
            "---",
            "",
            "## 💰 Weekly Ad Strategy",
            "",
            f"**Budget split:** {strategy.get('campaign_recommendations', {}).get('campaign_a_budget', 0):.0f} Campaign A / "
            f"{strategy.get('campaign_recommendations', {}).get('campaign_b_budget', 0):.0f} Campaign B",
            "",
            "**A/B test ideas this week:**",
        ]
        for idea in strategy.get("ab_test_ideas", []):
            lines.append(f"- {idea}")
        lines.append("")

        copy = strategy.get("weekly_ad_copy_variations", {})
        if copy.get("headlines"):
            lines.append("**Headline variations:**")
            for h in copy["headlines"]:
                lines.append(f"- {h}")
            lines.append("")

    # Lead scoring
    if scored_leads:
        lines += [
            "---",
            "",
            f"## 🎯 Lead Queue ({len(scored_leads)} leads scored)",
            "",
            "| Name | Score | Tier | Next Action |",
            "|---|---|---|---|",
        ]
        for lead in scored_leads:
            tier_emoji = {"hot": "🔥", "warm": "☀️", "medium": "🌤", "cold": "❄️"}.get(lead.get("tier", ""), "")
            lines.append(
                f"| {lead.get('name', 'Unknown')} | {lead.get('score', '?')}/10 | "
                f"{tier_emoji} {lead.get('tier', '?')} | {lead.get('next_action', '—')} |"
            )
        lines.append("")

    # Follow-ups
    if followups:
        lines += [
            "---",
            "",
            "## 📞 Follow-up Messages (Review before sending)",
            "",
        ]
        for fu in followups:
            msgs = fu.get("messages", {})
            name = fu.get("lead", "Unknown")
            lines += [
                f"### {name}",
                "",
                f"**SMS:** `{msgs.get('sms', '_N/A_')}`",
                "",
                f"**Email subject:** {msgs.get('email_subject', '_N/A_')}",
                "",
                f"**Email body:**",
                "```",
                msgs.get("email_body", "_N/A_"),
                "```",
                "",
                f"**Voicemail script:**",
                f"> {msgs.get('voicemail_script', '_N/A_')}",
                "",
            ]

    # Analytics (Saturday)
    if analytics and analytics.get("analysis"):
        a = analytics["analysis"]
        lines += [
            "---",
            "",
            "## 📈 Weekly Ad Analytics",
            "",
            f"**Period:** {analytics.get('period', 'Last 7 days')}",
            "",
            f"**Summary:** {a.get('summary', '_No summary_')}",
            "",
            "**Wins:**",
        ]
        for w in a.get("wins", []):
            lines.append(f"- {w}")
        lines.append("\n**Concerns:**")
        for c in a.get("concerns", []):
            lines.append(f"- {c}")
        lines.append("\n**Recommendations:**")
        for r in a.get("recommendations", []):
            lines.append(f"- {r}")
        lines.append("")

    # Footer
    lines += [
        "---",
        "",
        f"_Nick Jungmarker | REALTOR® | Long & Foster Real Estate | (301) 875-7182_",
        f"_To post: run `python main.py post --date {date}` or edit above and approve_",
    ]

    with open(path, "w") as f:
        f.write("\n".join(lines))

    return path


def append_log(date: str, data: dict):
    """Append a JSON log entry for the day's run."""
    _ensure_dirs()
    path = f"{LOGS_DIR}/{date}.log"
    entry = {"timestamp": datetime.now().isoformat(), **data}
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")
