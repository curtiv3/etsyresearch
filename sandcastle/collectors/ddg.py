from __future__ import annotations


class DdgUnavailableError(RuntimeError):
    pass


def fetch(query: str) -> list[dict]:
    try:
        from duckduckgo_search import DDGS
    except ImportError as exc:
        raise DdgUnavailableError("duckduckgo-search not installed") from exc

    results = []
    with DDGS() as ddgs:
        for idx, item in enumerate(ddgs.text(query, max_results=10), start=1):
            results.append(
                {
                    "rank": idx,
                    "url": item.get("href", ""),
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "raw_metadata": {"source": "ddg"},
                }
            )
    return results
