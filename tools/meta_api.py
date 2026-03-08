"""
Meta Graph API client — Facebook + Instagram publishing.

Wraps the Graph API endpoints for:
  - Publishing Facebook page posts
  - Publishing Instagram feed posts (via Content Publishing API)
  - Fetching post insights
"""

import httpx
from config import FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID, INSTAGRAM_ACCOUNT_ID

GRAPH_BASE = "https://graph.facebook.com/v19.0"


def publish_facebook_post(message: str, image_url: str | None = None) -> dict:
    """
    Publish a text (or link) post to the Facebook page.

    Args:
        message: Post text content
        image_url: Optional URL of an image to attach (must be publicly accessible)

    Returns:
        API response dict with 'id' key on success
    """
    if not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN == "your_page_access_token_here":
        print("  [META API] No token configured — simulating post (draft mode)")
        return {"id": "mock-fb-post-id", "simulated": True}

    url = f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": FACEBOOK_ACCESS_TOKEN,
    }
    if image_url:
        payload["link"] = image_url

    resp = httpx.post(url, data=payload, timeout=15.0)
    resp.raise_for_status()
    return resp.json()


def publish_instagram_post(caption: str, image_url: str | None = None) -> dict:
    """
    Publish an Instagram post via the Content Publishing API.
    Requires image_url for feed posts (Instagram requires media).

    NOTE: Instagram requires a media URL to publish feed posts.
    Caption-only posts are not supported — you must provide an image.

    Args:
        caption: Instagram caption text
        image_url: URL of the image (must be publicly accessible, JPG/PNG)

    Returns:
        API response dict with 'id' key on success
    """
    if not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN == "your_page_access_token_here":
        print("  [META API] No token configured — simulating Instagram post (draft mode)")
        return {"id": "mock-ig-post-id", "simulated": True}

    if not image_url:
        print("  [META API] Instagram requires an image URL — skipping post")
        return {"error": "image_url required for Instagram posts"}

    if not INSTAGRAM_ACCOUNT_ID:
        return {"error": "INSTAGRAM_ACCOUNT_ID not configured"}

    # Step 1: Create media container
    container_url = f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media"
    container_resp = httpx.post(
        container_url,
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": FACEBOOK_ACCESS_TOKEN,
        },
        timeout=15.0,
    )
    container_resp.raise_for_status()
    container_id = container_resp.json().get("id")

    # Step 2: Publish the container
    publish_url = f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    publish_resp = httpx.post(
        publish_url,
        data={
            "creation_id": container_id,
            "access_token": FACEBOOK_ACCESS_TOKEN,
        },
        timeout=15.0,
    )
    publish_resp.raise_for_status()
    return publish_resp.json()


def get_post_insights(post_id: str, metrics: list[str] | None = None) -> dict:
    """
    Fetch insights for a specific Facebook post.

    Args:
        post_id: The post ID returned from publish_facebook_post
        metrics: List of metric names (default: reach, impressions, engaged_users)

    Returns:
        Dict with metric names as keys
    """
    if not metrics:
        metrics = ["post_impressions", "post_impressions_unique", "post_engaged_users", "post_clicks"]

    if not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN == "your_page_access_token_here":
        return {"error": "No token configured", "simulated": True}

    url = f"{GRAPH_BASE}/{post_id}/insights"
    params = {
        "metric": ",".join(metrics),
        "access_token": FACEBOOK_ACCESS_TOKEN,
    }
    resp = httpx.get(url, params=params, timeout=10.0)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return {m["name"]: m.get("values", [{}])[0].get("value", 0) for m in data}
