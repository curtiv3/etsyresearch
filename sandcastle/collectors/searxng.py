from __future__ import annotations

import requests


def fetch(query: str, base_url: str, timeout_s: int, user_agent: str) -> list[dict]:
    url = f"{base_url.rstrip('/')}/search"
    params = {"q": query, "format": "json"}
    headers = {"User-Agent": user_agent}
    response = requests.get(url, params=params, headers=headers, timeout=timeout_s)
    response.raise_for_status()
    payload = response.json()
    results = []
    for idx, item in enumerate(payload.get("results", []), start=1):
        results.append(
            {
                "rank": idx,
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "raw_metadata": {"score": item.get("score")},
            }
        )
    return results
