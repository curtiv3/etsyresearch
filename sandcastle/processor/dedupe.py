from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

from rapidfuzz.distance import Jaccard

from sandcastle.processor.canonicalize import canonicalize_url
from sandcastle.processor.text import tokenize_text


@dataclass
class NormalizedRecord:
    query: str
    engine: str
    rank: int
    url: str
    title: str
    snippet: str
    timestamp: str
    canonical_url: str


@dataclass
class DedupedRecord:
    id: str
    canonical_url: str
    title: str
    snippet: str
    engines: list[str]
    best_rank: int
    timestamp: str


def normalize_records(records: Iterable[dict[str, str]]) -> list[NormalizedRecord]:
    normalized: list[NormalizedRecord] = []
    for record in records:
        canonical = canonicalize_url(record["url"])
        normalized.append(
            NormalizedRecord(
                query=record["query"],
                engine=record["engine"],
                rank=int(record["rank"]),
                url=record["url"],
                title=record.get("title", ""),
                snippet=record.get("snippet", ""),
                timestamp=record["timestamp"],
                canonical_url=canonical,
            )
        )
    return normalized


def _record_id(canonical_url: str) -> str:
    return hashlib.sha1(canonical_url.encode("utf-8")).hexdigest()[:10]


def _text_signature(title: str, snippet: str) -> list[str]:
    return tokenize_text(f"{title} {snippet}")


def dedupe_records(records: list[NormalizedRecord], threshold: float) -> list[DedupedRecord]:
    by_url: dict[str, DedupedRecord] = {}
    for record in records:
        existing = by_url.get(record.canonical_url)
        if existing:
            if record.rank < existing.best_rank:
                existing.best_rank = record.rank
                existing.title = record.title or existing.title
                existing.snippet = record.snippet or existing.snippet
                existing.timestamp = record.timestamp
            if record.engine not in existing.engines:
                existing.engines.append(record.engine)
            continue
        by_url[record.canonical_url] = DedupedRecord(
            id=_record_id(record.canonical_url),
            canonical_url=record.canonical_url,
            title=record.title,
            snippet=record.snippet,
            engines=[record.engine],
            best_rank=record.rank,
            timestamp=record.timestamp,
        )

    deduped: list[DedupedRecord] = []
    for record in by_url.values():
        merged = False
        record_tokens = _text_signature(record.title, record.snippet)
        for existing in deduped:
            existing_tokens = _text_signature(existing.title, existing.snippet)
            similarity = Jaccard.similarity(record_tokens, existing_tokens)
            if similarity >= threshold:
                merged = True
                if record.best_rank < existing.best_rank:
                    existing.best_rank = record.best_rank
                    existing.title = record.title or existing.title
                    existing.snippet = record.snippet or existing.snippet
                    existing.canonical_url = record.canonical_url
                    existing.id = record.id
                    existing.timestamp = record.timestamp
                for engine in record.engines:
                    if engine not in existing.engines:
                        existing.engines.append(engine)
                break
        if not merged:
            deduped.append(record)

    return sorted(deduped, key=lambda item: (item.best_rank, item.canonical_url))
