"""
Central configuration + brand constants.
All agents import from here — never hardcode values elsewhere.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID      = os.getenv("FACEBOOK_PAGE_ID", "")
INSTAGRAM_ACCOUNT_ID  = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
AGENTOS_BASE_URL      = os.getenv("AGENTOS_BASE_URL", "http://localhost:8000")

# ── Posting mode ──────────────────────────────────────────────────────────────
POSTING_MODE = os.getenv("POSTING_MODE", "draft")  # "draft" | "auto"

# ── Scheduling ────────────────────────────────────────────────────────────────
DAILY_RUN_HOUR   = int(os.getenv("DAILY_RUN_HOUR", "9"))
DAILY_RUN_MINUTE = int(os.getenv("DAILY_RUN_MINUTE", "0"))

# ── Market focus ──────────────────────────────────────────────────────────────
PRIMARY_MARKET     = os.getenv("PRIMARY_MARKET", "Baltimore City, MD")
SECONDARY_MARKETS  = os.getenv("SECONDARY_MARKETS", "").split(",")

# ── Model ─────────────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-6"

# ── Brand constants ───────────────────────────────────────────────────────────
BRAND = {
    "name":       "Nick Jungmarker",
    "title":      "REALTOR®",
    "brokerage":  "Long & Foster Real Estate",
    "phone":      "(301) 875-7182",
    "email":      "nickjungmarker@lnf.com",
    "website":    "jungmarker.com",
    "instagram":  "@nickjungmarker.realtor",
    "tiktok":     "@dorlpob",
    "languages":  ["English", "Spanish"],
    "license":    "MD License #5017475",
    "reviews":    "47+ five-star Google reviews",
    "office": {
        "name":    "Long & Foster Real Estate",
        "address": "12520 Prosperity Dr #105, Silver Spring, MD 20904",
        "phone":   "(301) 388-2600",
    },
    # Matches jungmarker.com (tailwind.config.js): Outfit headings, Inter body
    "fonts": {"heading": "Outfit", "body": "Inter"},
    "colors": {
        "warm_white": "#faf7f2",
        "stone":      "#f0ece4",
        "concrete":   "#e4dfd6",
        "ash":        "#716b62",
        "charcoal":   "#1c1917",
        "gold":       "#c9a84c",
        "md_red":     "#b31942",   # Maryland flag red, primary CTA
        "navy":       "#0f1b2d",
        "brick":      "#7a2e1a",
    },
}

# Required compliance footer for all social captions
COMPLIANCE_FOOTER = (
    "\n\n—\n"
    "Nick Jungmarker | REALTOR® | Long & Foster Real Estate\n"
    "(301) 875-7182 | jungmarker.com\n"
    "Equal Housing Opportunity 🏠"
)

# ── Baltimore neighborhood data ────────────────────────────────────────────────
BALTIMORE_NEIGHBORHOODS = [
    {"name": "Hampden",        "type": "rowhouse",  "median_price": 285000, "vibe": "artsy, walkable"},
    {"name": "Canton",         "type": "rowhouse",  "median_price": 350000, "vibe": "waterfront, trendy"},
    {"name": "Federal Hill",   "type": "rowhouse",  "median_price": 360000, "vibe": "historic, Inner Harbor"},
    {"name": "Remington",      "type": "rowhouse",  "median_price": 240000, "vibe": "up-and-coming, affordable"},
    {"name": "Charles Village", "type": "rowhouse", "median_price": 230000, "vibe": "near Hopkins, diverse"},
    {"name": "Pigtown",        "type": "rowhouse",  "median_price": 185000, "vibe": "affordable, improving"},
    {"name": "Waverly",        "type": "rowhouse",  "median_price": 175000, "vibe": "affordable, community-driven"},
    {"name": "Lauraville",     "type": "rowhouse",  "median_price": 200000, "vibe": "quiet, northeast Baltimore"},
    {"name": "Belair-Edison",  "type": "rowhouse",  "median_price": 160000, "vibe": "affordable, diverse"},
    {"name": "Hamilton",       "type": "rowhouse",  "median_price": 190000, "vibe": "northeast, first-time buyer hotspot"},
]

# ── Content calendar (weekly rhythm) ──────────────────────────────────────────
CONTENT_CALENDAR = {
    "Monday":    {"theme": "educational",    "format": "video",    "topic": "First-time buyer tips"},
    "Tuesday":   {"theme": "carousel",       "format": "carousel", "topic": "Neighborhood spotlight"},
    "Wednesday": {"theme": "seller/market",  "format": "static",   "topic": "Market update + home values"},
    "Thursday":  {"theme": "neighborhood",   "format": "reel",     "topic": "Baltimore neighborhood tour"},
    "Friday":    {"theme": "personal",       "format": "static",   "topic": "Client win / personal story"},
    "Saturday":  {"theme": "market_data",    "format": "carousel", "topic": "Week in Baltimore real estate"},
    "Sunday":    {"theme": "community",      "format": "static",   "topic": "Community + lifestyle content"},
}

# ── Output paths ──────────────────────────────────────────────────────────────
DRAFTS_DIR = "output/drafts"
LOGS_DIR   = "output/logs"
