# CLAUDE.md — Marketing Agent Best Practices

This file is the living source of truth for how Claude should work in this repo.
Update it whenever we learn something new, fix a recurring mistake, or agree on a better approach.

---

## Project Overview

**Autonomous multi-agent marketing system** for Nick Jungmarker | REALTOR® | Long & Foster Real Estate.

Daily pipeline: generates Baltimore real estate social content, scores leads, writes follow-ups,
and analyzes Meta ad performance — all tuned to the Baltimore rowhouse market.

---

## Architecture Rules

- `config.py` is the single source of truth for brand constants, API keys, and settings.
  **Never hardcode values in agents or tools.**
- All agents live in `agents/`. Each agent exposes a `run()` function as its public interface.
- All external API clients live in `tools/`. Agents call tools — tools call APIs.
- Output goes to `output/drafts/` (human-readable) and `output/logs/` (machine log).
- `orchestrator.py` coordinates the pipeline — it should not contain business logic.

---

## Claude API Usage

- Model: always use `CLAUDE_MODEL` from `config.py` (currently `claude-sonnet-4-6`).
- Client: instantiate `anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)` — never hardcode the key.
- Always request JSON output from Claude. Strip markdown fences defensively (see `content_agent.py`).
- Set `max_tokens` appropriate to the output size — content agents use 1500, analytics can use 2000+.
- Wrap all Claude calls in try/except in the orchestrator. A single agent failure must not stop the pipeline.

---

## Posting Safety

- Default `POSTING_MODE=draft`. **Never change to `auto` without the user explicitly requesting it.**
- In auto mode, always log the Meta API response ID so posts can be traced.
- Compliance footer must appear in every caption — it is injected at the prompt level, not post-processed.

---

## Compliance & Fair Housing

- Every social post ends with the exact compliance footer defined in `config.py::COMPLIANCE_FOOTER`.
- Meta ads must always use **Special Ad Category: Housing** — no demographic targeting or exclusions.
- Never write copy that makes specific income, tax, or investment promises.
- Bilingual content (English/Spanish) is intentional — do not remove it.

---

## Lead Handling

- Lead scorer returns tiers: `hot`, `warm`, `medium`, `cold`.
- Follow-up agent caps at 3 priority leads per day (orchestrator enforces this).
- Lead stages: `initial → day3 → day7 → day14 → day30 → reactivation`.
- If AgentOS is not running, lead scorer should return mock/demo data gracefully — never crash.

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

Monday = weekly ad strategy refresh. Saturday = analytics report.

---

## Key Brand Facts (for prompt context)

- Name: Nick Jungmarker | REALTOR® | Long & Foster Real Estate
- Phone: (301) 875-7182 | Website: jungmarker.com | Instagram: @nickjungmarker.realtor
- Languages: English + Spanish
- Specialty: Baltimore rowhouses, first-time buyers, bilingual clients
- Social proof: 47+ five-star Google reviews
- Primary audience: renters aged 25–40 in Baltimore metro who think they can't afford to buy

---

## Environment Setup Checklist

Before running, ensure `.env` has:
- [ ] `ANTHROPIC_API_KEY` — required for all agents
- [ ] `FACEBOOK_ACCESS_TOKEN` — required for auto-posting
- [ ] `FACEBOOK_PAGE_ID` — required for auto-posting
- [ ] `INSTAGRAM_ACCOUNT_ID` — required for auto-posting
- [ ] `POSTING_MODE=draft` — start here, switch to `auto` only when ready
- [ ] `AGENTOS_BASE_URL` — only needed when fsbo-agent backend is running

---

## Development Workflow

1. Always develop on the designated feature branch (see task context).
2. Run `python main.py --content` to smoke-test content generation without the full pipeline.
3. Run `python main.py --score` to test lead scoring independently.
4. Review `output/drafts/YYYY-MM-DD.md` before considering auto-post mode.
5. Commit with clear messages describing what changed and why.

---

## Lessons Learned / Feedback Loop

_Add entries here as we discover issues, fix bugs, or agree on better approaches._

| Date | Learning |
|---|---|
| 2026-03-08 | CLAUDE.md created — establish feedback loop from day one |

---

## What to Ask the User When Blocked

- **API keys missing**: ask for the specific key needed; do not guess or skip.
- **AgentOS offline**: confirm whether to use mock lead data or wait for backend.
- **Posting mode**: always confirm before switching from `draft` to `auto`.
- **New neighborhood data**: ask Nick directly — he knows the Baltimore market better than any data source.
