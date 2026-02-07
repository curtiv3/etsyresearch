from __future__ import annotations

from urllib.parse import urlparse


def apply_domain_filters(items: list[dict], domain_config: dict) -> list[dict]:
    include_domains = set(domain_config.get("include", []))
    exclude_config = domain_config.get("exclude", {})
    exclude_domains: set[str] = set()
    for entry in exclude_config.values():
        if entry.get("enabled", False):
            exclude_domains.update(entry.get("domains", []))

    filtered: list[dict] = []
    for item in items:
        domain = urlparse(item["canonical_url"]).netloc
        if include_domains and domain not in include_domains:
            continue
        if domain in exclude_domains:
            continue
        filtered.append(item)
    return filtered
