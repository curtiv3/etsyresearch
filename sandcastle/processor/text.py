from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "for",
    "to",
    "of",
    "in",
    "on",
    "with",
    "by",
    "from",
    "at",
    "is",
    "are",
    "be",
    "this",
    "that",
    "your",
    "you",
    "it",
    "as",
    "new",
    "best",
    "guide",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize_text(text: str) -> list[str]:
    tokens = TOKEN_RE.findall(text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def top_terms(tokens: Iterable[str], limit: int = 10) -> list[str]:
    counter = Counter(tokens)
    items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    return [term for term, _ in items[:limit]]


def bigrams(tokens: list[str]) -> list[str]:
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
