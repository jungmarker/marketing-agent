# Marketing Agent — Baltimore Real Estate Lead Gen

Autonomous multi-agent marketing system for **Nick Jungmarker | REALTOR® | Long & Foster Real Estate**.

Generates daily Facebook/Instagram content, scores incoming leads, writes follow-up messages, and analyzes Meta ad performance — all tuned to the Baltimore rowhouse market and first-time buyer audience.

---

## Architecture

```
orchestrator.py          ← Lead agent that runs the daily pipeline
│
├── agents/
│   ├── content_agent.py       ← Facebook + Instagram post generation
│   ├── ad_strategy_agent.py   ← Weekly Meta campaign targeting + budget strategy
│   ├── lead_scorer.py         ← Scores leads 0-10 from AgentOS
│   ├── followup_agent.py      ← Personalized SMS/email/voicemail scripts
│   ├── analytics_agent.py     ← Meta Ads API performance reports
│   └── market_agent.py        ← Baltimore market context for content
│
├── tools/
│   ├── meta_api.py            ← Facebook + Instagram Graph API client
│   ├── agentos_client.py      ← AgentOS (fsbo-agent) API wrapper
│   └── file_store.py          ← Draft file + log management
│
├── output/
│   ├── drafts/YYYY-MM-DD.md   ← Daily review file (human-readable)
│   └── logs/YYYY-MM-DD.log    ← Machine log
│
├── config.py                  ← Brand constants, API keys, settings
└── main.py                    ← CLI entry point
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/jungmarker/marketing-agent.git
cd marketing-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Required env vars
| Key | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `FACEBOOK_ACCESS_TOKEN` | Meta Business Suite → Token Tools |
| `FACEBOOK_PAGE_ID` | Your Facebook page URL or Settings |
| `INSTAGRAM_ACCOUNT_ID` | Meta Business Suite → Instagram account |

---

## Usage

```bash
# Run the full daily pipeline
python main.py

# Run as a specific day (to generate Monday's strategy on any day)
python main.py --day Monday

# Individual agents
python main.py --content       # Generate today's social content only
python main.py --score         # Score leads from AgentOS only
python main.py --strategy      # Generate weekly ad strategy only
python main.py --analytics     # Force weekly analytics report

# Start daily scheduler (runs at 9am)
python main.py --schedule
```

---

## Posting Modes

Set in `.env`:

| Mode | Behavior |
|---|---|
| `POSTING_MODE=draft` | Saves to `output/drafts/YYYY-MM-DD.md` for review before posting |
| `POSTING_MODE=auto` | Posts directly to Facebook + Instagram (requires valid tokens) |

**Start in draft mode.** Review `output/drafts/` before switching to auto.

---

## Sub-Agent Overview

### `content_agent` — Daily Social Content
- Reads the content calendar (Monday=educational, Tuesday=carousel, etc.)
- Picks a Baltimore neighborhood to spotlight
- Generates Facebook post + Instagram caption + visual description
- Bilingual — writes in Spanish for Spanish-speaking audiences
- Always appends compliance footer

### `ad_strategy_agent` — Weekly Meta Strategy (Mondays)
- Recommends budget split between Campaign A (FTB guide) and Campaign B (seller valuation)
- Generates 3 headline variations + 3 primary text variations
- Proposes A/B test ideas
- Stays within Housing Special Ad Category constraints (no demographic targeting)

### `lead_scorer` — Lead Prioritization
- Pulls new leads from AgentOS API
- Scores 0–10 on: contact quality, timeline, motivation, pre-qualification, source
- Returns tiered list: hot / warm / medium / cold

### `followup_agent` — Personalized Outreach
- Generates SMS (<155 chars), email subject + body, voicemail script
- Uses lead's name, source, and message to personalize
- Writes in Spanish if lead appears Spanish-speaking
- Stages: initial → day3 → day7 → day14 → day30 → reactivation

### `analytics_agent` — Meta Ad Performance (Saturdays)
- Fetches campaign spend, impressions, CTR, leads, CPL from Meta Ads API
- Returns plain-English summary + wins/concerns/recommendations
- Uses mock data until real FACEBOOK_ACCESS_TOKEN is configured

### `market_agent` — Baltimore Market Context
- Generates weekly Baltimore market narrative (prices, inventory, seasonality)
- Spotlights 2 neighborhoods
- Produces content hooks for social media
- Feeds context into content + strategy agents

---

## Content Calendar

| Day | Theme | Format |
|---|---|---|
| Monday | Educational | Video script |
| Tuesday | Carousel | Neighborhood spotlight |
| Wednesday | Seller/Market | Static image |
| Thursday | Neighborhood | Reel |
| Friday | Personal | Static image |
| Saturday | Market data | Carousel |
| Sunday | Community | Static image |

---

## Compliance

Every post auto-includes:
```
Nick Jungmarker | REALTOR® | Long & Foster Real Estate
(301) 875-7182 | jungmarker.com
Equal Housing Opportunity 🏠
```

All Meta ads use **Special Ad Category: Housing** — no demographic targeting or exclusions.

---

## Integration with AgentOS

When the `fsbo-agent` backend is running locally at `http://localhost:8000`:
- `lead_scorer` pulls and scores real leads
- `followup_agent` pulls lead details for personalization
- `agentos_client` can write follow-up notes back to lead records

---

## Remote Access

To continue work remotely:
1. **GitHub** — this repo. Clone on any device.
2. **GitHub Codespaces** — open the repo → Code → Codespaces → New. Full Claude Code access from browser/phone.
3. **SSH to Mac** — install Tailscale on your Mac, then SSH in from any device.

---

_Nick Jungmarker | REALTOR® | Long & Foster Real Estate | Maryland Licensed_
_Equal Housing Opportunity_
