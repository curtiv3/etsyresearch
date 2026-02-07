from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_PARAMS_PREFIXES = ("utm_",)
TRACKING_PARAMS_EXACT = {
    "fbclid",
    "gclid",
    "mc_eid",
    "_hsenc",
    "_hsmi",
    "igshid",
    "ref",
    "spm",
}

MULTI_SLASH_RE = re.compile(r"/{2,}")


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = "https"
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]

    path = MULTI_SLASH_RE.sub("/", parsed.path)
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    query_pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        key_lower = key.lower()
        if key_lower.startswith(TRACKING_PARAMS_PREFIXES):
            continue
        if key_lower in TRACKING_PARAMS_EXACT:
            continue
        query_pairs.append((key, value))

    query_pairs.sort(key=lambda item: (item[0], item[1]))
    query = urlencode(query_pairs, doseq=True)

    canonical = urlunparse((scheme, netloc, path, "", query, ""))
    return canonical
