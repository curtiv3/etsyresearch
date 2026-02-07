from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from sandcastle.processor.text import bigrams, tokenize_text, top_terms

INTENT_TAGS = ["worksheet", "prompts", "pdf", "undated", "bundle", "printable"]


@dataclass
class ClusterResult:
    cluster_id: str
    label: str
    member_ids: list[str]
    count: int
    top_terms: list[str]
    top_bigrams: list[str]
    intent_counts: dict[str, int]


def load_keywords(path: Path) -> list[str]:
    keywords: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            cleaned = line.strip()
            if cleaned:
                keywords.append(cleaned.lower())
    return keywords


def keyword_id(keyword: str) -> str:
    return keyword.replace(" ", "_")


def assign_clusters(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    cluster_ids = []
    for keyword in keywords:
        if keyword in lowered:
            cluster_ids.append(keyword_id(keyword))
    return cluster_ids


def build_clusters(items: list[dict], keywords: list[str]) -> list[ClusterResult]:
    clusters: dict[str, dict] = defaultdict(lambda: {
        "label": "",
        "members": [],
        "tokens": [],
        "bigrams": [],
        "intent_counts": Counter(),
    })

    for item in items:
        text = f"{item['title']} {item['snippet']}"
        cluster_ids = assign_clusters(text, keywords)
        item["cluster_ids"] = cluster_ids
        tokens = tokenize_text(text)
        bi = bigrams(tokens)
        intents_found = [tag for tag in INTENT_TAGS if tag in text.lower()]

        for cluster_id in cluster_ids:
            cluster = clusters[cluster_id]
            cluster["label"] = cluster_id.replace("_", " ")
            cluster["members"].append(item["id"])
            cluster["tokens"].extend(tokens)
            cluster["bigrams"].extend(bi)
            cluster["intent_counts"].update(intents_found)

    results: list[ClusterResult] = []
    for cluster_id, data in clusters.items():
        tokens = data["tokens"]
        bigram_terms = data["bigrams"]
        results.append(
            ClusterResult(
                cluster_id=cluster_id,
                label=data["label"],
                member_ids=data["members"],
                count=len(data["members"]),
                top_terms=top_terms(tokens, limit=10),
                top_bigrams=top_terms(bigram_terms, limit=10),
                intent_counts=dict(data["intent_counts"]),
            )
        )

    return sorted(results, key=lambda item: item.cluster_id)
