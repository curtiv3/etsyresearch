from __future__ import annotations

import os

import requests


class BraveDisabledError(RuntimeError):
    pass


def fetch(query: str, timeout_s: int, user_agent: str) -> list[dict]:
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        raise BraveDisabledError("BRAVE_API_KEY not set")
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "User-Agent": user_agent,
        "X-Subscription-Token": api_key,
    }
    params = {"q": query}
    response = requests.get(url, params=params, headers=headers, timeout=timeout_s)
    response.raise_for_status()
    payload = response.json()
    results = []
    for idx, item in enumerate(payload.get("web", {}).get("results", []), start=1):
        results.append(
            {
                "rank": idx,
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "snippet": item.get("description", ""),
                "raw_metadata": {"age": item.get("age")},
            }
        )
    return results
