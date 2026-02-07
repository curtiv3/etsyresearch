from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CollectorRecord(BaseModel):
    query: str
    engine: str
    rank: int
    url: str
    title: str
    snippet: str
    timestamp: str
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class DedupedItem(BaseModel):
    id: str
    canonical_url: str
    title: str
    snippet: str
    engines: list[str]
    best_rank: int
    cluster_ids: list[str]
    timestamp: str


class ClusterSummary(BaseModel):
    cluster_id: str
    label: str
    member_ids: list[str]
    count: int
    top_terms: list[str]
    top_bigrams: list[str]
    intent_counts: dict[str, int]


class TermsSummary(BaseModel):
    global_top_terms: list[list[str | int]]
    global_top_bigrams: list[list[str | int]]


class StrategyItem(BaseModel):
    cluster_id: str
    recommendation: str
    priority: int


class ResearchQuestion(BaseModel):
    question: str
    related_clusters: list[str]
    status: str
