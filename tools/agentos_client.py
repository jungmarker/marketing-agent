"""
AgentOS client — thin HTTP wrapper for the fsbo-agent FastAPI backend.
Handles lead CRUD and social post scheduling calls.
"""

import httpx
from config import AGENTOS_BASE_URL


def get_leads(status: str | None = None, limit: int = 50) -> list[dict]:
    """Fetch leads from AgentOS. Returns empty list if unreachable."""
    try:
        params = {"limit": limit}
        if status:
            params["status"] = status
        resp = httpx.get(f"{AGENTOS_BASE_URL}/api/v1/leads/", params=params, timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def update_lead_status(lead_id: str, new_status: str) -> bool:
    """Update a lead's status in AgentOS."""
    try:
        resp = httpx.put(
            f"{AGENTOS_BASE_URL}/api/v1/leads/{lead_id}/status",
            json={"status": new_status},
            timeout=5.0,
        )
        resp.raise_for_status()
        return True
    except Exception:
        return False


def add_follow_up_note(lead_id: str, note: str, method: str = "email") -> bool:
    """Record a follow-up action on a lead."""
    try:
        resp = httpx.post(
            f"{AGENTOS_BASE_URL}/api/v1/leads/{lead_id}/follow-up",
            json={"note": note, "method": method},
            timeout=5.0,
        )
        resp.raise_for_status()
        return True
    except Exception:
        return False


def schedule_social_post(platform: str, content: str, scheduled_time: str) -> dict:
    """Schedule a social post via AgentOS."""
    try:
        resp = httpx.post(
            f"{AGENTOS_BASE_URL}/api/v1/social/schedule",
            json={
                "platform": platform,
                "content": content,
                "scheduled_time": scheduled_time,
            },
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
